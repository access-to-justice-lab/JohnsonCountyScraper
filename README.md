# JohnsonCountyScraper

## MySQL
You need to create an env.list file and populate it with
```
sql_user=user
sql_password=password
sql_ip=ip
sql_schema=johnsoncounty
```
Make sure to create a schema called johnsoncounty (or whatever you want to name it) and that the user above has appropriate access to that table.

## Docker
```
docker build -t joco_server .
```
If you are running a msyql docker container on the same machine you can use the docker command below to get the IP address.
```
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' [docker container name]
```

## Scraping
Run the docker container with the env.list file that you create and then add in the --env values for the starting case number and how many cases you want to scrape
```
docker run --env-file env.list --env startingcase=20CR00001 --env limit=2500 --rm --name joco joco_server
```
If you want to run it detached then run it with -d flags
```
docker run --env-file env.list --env startingcase=20CR00001 --env limit=2500 --rm -d--name joco joco_server
```
## Testing
To run all tests
```
docker run --env-file env.list --entrypoint python --rm --name joco-test joco_server /app/test.py
```
To run just a single test
```
docker run --env-file env.list --entrypoint python --rm --name joco-test joco_server /app/test.py TestSQL.testSQLCredentials
```