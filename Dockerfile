FROM python:3
RUN apt-get update
RUN pip3 install nltk
RUN python3 -c "import nltk; nltk.download('words'); nltk.download('stopwords')"
RUN mkdir /var/www
COPY / ./var/www
WORKDIR /var/www
ENTRYPOINT ["python3", "src/server.py"]