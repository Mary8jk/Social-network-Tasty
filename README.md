# Foodgram #

<https://foooodgram.hopto.org>

IP: <http://84.201.166.199/>

Here is the link to the API: <https://foooodgram.hopto.org/api/>.

Redoc: <https://foooodgram.hopto.org/api/docs/>.

This project is implemented in the form of a profile social network. Here you can share recipes of dishes, add them to favorites, display a shopping list for cooking your favorite dishes, download a shopping card in TXT format, and subscribe to other users.
A local database is used to add ingredients to your recipes.


## Technologies ##
+ Python 3.10.10
+ Django 3.2
+ Django REST Framework 3.12
+ PostgresQL
+ Docker
+ Postman
+ GitHub Actions

## To deploy this project need the next steps ##
Download project with SSH:
```python
git clone git@github.com:Mary8jk/foodgram-project-react.git
```
Connect to your server:
```python
ssh <server user>@<server IP>
```
Install Docker on your server:
```python
sudo apt install docker.io
```
Install Docker Compose (for Linux):
```python
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
Get permissions for docker-compose:
```python
sudo chmod +x /usr/local/bin/docker-compose
```
Create project directory (preferably in your home directory):
```python
mkdir foodgram && cd foodgram/
```
Create env-file:
```python
touch .env
```
Add in the env-file like it:
```python
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=<Your_password>
POSTGRES_DB=foodgram
DB_HOST=db
DB_PORT=5432

SECRET_KEY=<Your_secret_key>
DEBUG=False
DJANGO_ALLOWED_HOSTS=<Your_host>
```
Copy files from 'nginx/' (on your local machine) to your server:
```python
scp -r nginx/* <server user>@<server IP>:/home/<server user>/foodgram/
```
Run docker-compose:
```python
sudo docker-compose up -d
```
