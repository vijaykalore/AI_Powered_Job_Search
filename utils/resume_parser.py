import os
import tempfile
import re
from config import OPENAI_API_KEY


# NOTE: langchain imports that pull compiled/vector libraries (FAISS, etc.)
# are deferred and imported lazily inside methods that need them. This
# prevents import-time failures on builders that can't compile native
# extensions (for example, Streamlit Cloud without SWIG/Rust compilers).


class ResumeParser:
    """Lightweight resume parser with optional RAG and spaCy features.

    This implementation avoids importing heavy or native packages at
    module import time. spaCy and langchain components are loaded
    lazily inside the class constructor or methods and fall back to
    no-op behaviors when unavailable.
    """

    def __init__(self):
        self.use_rag = False

        # Lazy spaCy loading: prefer larger models but fall back safely.
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_lg")
            except Exception:
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except Exception:
                    self.nlp = spacy.blank("en")
        except Exception:
            # Minimal fallback object with the attributes we access.
            class _Blank:
                def __call__(self, txt):
                    class Doc:
                        def __init__(self, t):
                            self.text = t
                            self.ents = []

                    return Doc(txt)

            self.nlp = _Blank()

        # Lazy langchain/OpenAI integration for RAG-like features
        if OPENAI_API_KEY:
            try:
                from langchain.embeddings import OpenAIEmbeddings
                from langchain.llms import OpenAI

                self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
                self.llm = OpenAI(api_key=OPENAI_API_KEY)
                self.use_rag = True
            except Exception:
                self.use_rag = False

    def save_uploaded_file(self, uploaded_file):
        """Save an uploaded file to a temporary location and return the path."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_file.getbuffer())
            return tmp.name

    def parse_resume(self, text: str):
        """Public method to parse resume text and return structured data."""
        if not text:
            return None

        return self.extract_information(text)

    def extract_information(self, text: str) -> dict:
        """Extract structured information from resume text.

        This method uses keyword heuristics and spaCy NER (if available).
        If RAG features are enabled they are applied in guarded blocks.
        """
        doc = self.nlp(text)

        skills = set()
        education = []
        experience = []
        contact_info = {"email": "", "phone": ""}

        # Simple contact extraction
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info["email"] = emails[0]

        phone_pattern = r"\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info["phone"] = phones[0]

        # Keyword-based skills (kept deliberately small for speed)
        skill_keywords = [
            "python", "java", "javascript", "react", "node.js", "sql",
            "aws", "azure", "gcp", "docker", "kubernetes", "tensorflow",
            "pytorch", "pandas", "numpy", "flask", "django"
        ]

        for kw in skill_keywords:
            if kw.lower() in text.lower():
                skills.add(kw)

        # Use spaCy entities if available
        try:
            for ent in getattr(doc, "ents", []):
                if getattr(ent, "label_", "") in ("ORG", "PRODUCT"):
                    skills.add(ent.text)
                if getattr(ent, "label_", "") == "ORG":
                    # crude check for education-looking orgs
                    if any(term in ent.text.lower() for term in ("university", "college", "institute")):
                        education.append(ent.text)
        except Exception:
            pass

        # Basic experience heuristics: look for common headers
        lower = text.lower()
        for header in ("experience", "work experience", "professional experience"):
            if header in lower:
                # grab a slice after the header to present as experience summary
                idx = lower.find(header)
                snippet = text[idx: idx + 1000]
                experience.append(snippet.strip())
                break

        # Optionally try RAG enhancements in guarded blocks
        if self.use_rag:
            try:
                from langchain.text_splitter import RecursiveCharacterTextSplitter

                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = splitter.split_text(text)

                try:
                    from langchain.vectorstores import FAISS
                    from langchain.chains import RetrievalQA

                    vectorstore = FAISS.from_texts(chunks, self.embeddings)
                    retriever = vectorstore.as_retriever()
                    qa_chain = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=retriever)

                    # guarded queries - results appended if present
                    resp = qa_chain.run("List the technical skills mentioned in this resume.")
                    if resp:
                        for s in re.split(r"[,\n•-]", resp):
                            s = s.strip()
                            if s:
                                skills.add(s)
                except Exception:
                    # Vectorstore or FAISS not available; skip RAG
                    pass
            except Exception:
                pass

        return {
            "raw_text": text,
            "skills": list(skills),
            "education": list(set(education)),
            "experience": experience,
            "contact_info": contact_info,
        }