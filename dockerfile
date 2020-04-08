FROM python:3
RUN apt-get update
RUN pip install pprint sqlalchemy pymysql bs4 requests lxml
RUN pip install PyMySQL[rsa]
