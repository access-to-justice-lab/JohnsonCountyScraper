# JohnsonCountyScraper

## MySQL
You need to create an env.list file and populate it with
```
sql_user=user
sql_password=password
sql_ip=ip
```
Make sure to create a schema called johnsoncounty that the user above has access to.

## Docker
docker build -t joco_server .
docker run --env-file env.list -itd -v ${PWD}:/app --name joco joco_server
docker exec -it joco bash

## Python Testing
To run all tests
```
python test.py
```
To run just a single test
```
python test.py TestSQL.testSQLCredentials
```
For some reason pymysql[rsa] is not installing in the docker build. If you get an error run
```
pip install pymysql[rsa]
```
## Scraping
```
python main.py 98CR00001 10
```
## ToDo
Custom time delay
VPN switcher
