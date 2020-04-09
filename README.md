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
docker run --env-file env.list --env startingcase=20CR00001 --env limit=5 -t --name joco joco_server

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
Argument 1 is the starting case number and the second argument is the limit before it stops.
```
python main.py 98CR00001 10
```
## ToDo
Custom time delay
VPN switcher
If there is no race it comes up as a blank string. It should be a None value
```
20CR00170
/F 05/09/02
```