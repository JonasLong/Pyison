FROM python:3-slim
RUN pip3 install nltk
RUN python3 -c "import nltk; nltk.download('words'); nltk.download('stopwords')"
WORKDIR /var/www
COPY / ./
ENTRYPOINT ["python3", "-u", "src/server.py"]
