FROM python:3.11

# Create a non-root user
RUN useradd -m user
USER user

WORKDIR /home/user/app

COPY --chown=user . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
