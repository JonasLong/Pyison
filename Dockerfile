FROM python:3
RUN apt-get update
RUN pip3 install nltk
RUN python3 -c "import nltk; nltk.download('words'); nltk.download('stopwords')"
WORKDIR /var/www
COPY / ./
ENTRYPOINT ["python3", "src/server.py"]