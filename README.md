# Professional Job Search Assistant

Live demo: https://vijaykalore-ai-powered-job-search-app-oujbcb.streamlit.app/

A polished Streamlit app to analyze resumes, discover matching roles, and help you prepare for interviews — all in a single, easy-to-use interface.

---

## Why this app
- Upload a resume (PDF/DOCX/TXT) and receive an AI-driven breakdown of skills, experience highlights, and improvement suggestions.
- Search for matching jobs using your resume or a custom query and save interesting roles.
- Generate interview questions and practice answers tailored to a selected job.

## Live demo and quick access
- Live app: https://vijaykalore-ai-powered-job-search-app-oujbcb.streamlit.app/
- Source code: https://github.com/vijaykalore/AI_Powered_Job_Search

## Quick start (developer)
1. Clone the repo

   git clone https://github.com/vijaykalore/AI_Powered_Job_Search.git
   cd AI_Powered_Job_Search

2. Create & activate a virtual environment (PowerShell)

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

3. Install dependencies

   pip install -r requirements.txt

4. Set environment variables (example)

   # PowerShell example
   $env:OPENAI_API_KEY = "sk-..."
   $env:SERPAPI_API_KEY = "..."

5. Run locally

   streamlit run app.py

## Notes
- The project avoids shipping heavy native-compiled dependencies in the default Cloud requirements. If you need advanced vector/RAG features (FAISS, tiktoken), deploy with Docker and install the required system build tools in the image.
- For richer NLP tasks locally, install spaCy models:

  python -m spacy download en_core_web_lg

## Persistence
- Saved jobs and interview notes are stored under `saved_jobs/` and `saved_interviews/`. For production deployments, mount persistent storage or integrate external storage (S3, database).

## Contributing
- Issues and pull requests are welcome. Small UI edits, parser improvements, or refinements to the job matcher are great first contributions.

## Contact & links
- GitHub: https://github.com/vijaykalore/AI_Powered_Job_Search
- Live demo: https://vijaykalore-ai-powered-job-search-app-oujbcb.streamlit.app/

