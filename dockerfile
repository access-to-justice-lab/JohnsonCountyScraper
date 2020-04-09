FROM python:3
RUN apt-get update
COPY app /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD [ "python", "/app/main.py" ]
# RUN pip install pprint sqlalchemy pymysql bs4 requests lxml
# RUN pip install PyMySQL[rsa]
