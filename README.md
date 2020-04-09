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
'''
docker build -t joco_server .
```
## Scraping
Run the docker container with the env.list file that you create and then add in the --env values for the starting case number and how many cases you want to scrape
```
docker run --env-file env.list --env startingcase=20CR00001 --env limit=2500 --rm --name joco joco_server
'''
If you want to run it detached then run it with -d flags
```
docker run --env-file env.list --env startingcase=20CR00001 --env limit=2500 --rm -d--name joco joco_server
```
## Python Testing
To run all tests
```
docker run --env-file env.list --env startingcase=20CR00001 --env limit=2500 --entrypoint python -t --rm --name joco-test joco_server /app/test.py
```
To run just a single test
```
docker run --env-file env.list --env startingcase=20CR00001 --env limit=2500 --entrypoint python -t --rm --name joco-test joco_server /app/test.py TestSQL.testSQLCredentials
```
For some reason pymysql[rsa] is not installing in the docker build. If you get an error run
```
pip install pymysql[rsa]
```