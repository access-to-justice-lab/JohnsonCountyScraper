FROM python:3
RUN apt-get update
COPY app /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install pymysql[rsa]
CMD [ "python", "/app/main.py" ]