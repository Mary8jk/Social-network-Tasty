# Профильная социальная сеть #

Данный проект реализован в виде профильной социальной сети. <br>
Здесь вы можете делиться рецептами блюд, добавлять их в избранное, отображать список покупок для приготовления любимых блюд, загружать карточку покупок в формате TXT и подписываться на других пользователей. В карточке покупок, для удобства, количество дублирующихся продуктов суммируется автоматически.<br>
Для добавления ингредиентов в ваши рецепты используется локальная база данных.

После запуска в контейнерах проект доступен по:
<http://localhost:9001/>

Здесь вы можете ознакомиться с API: <http://localhost:9001/api/>.

Redoc: <http://localhost:9001/api/docs/>.

## Стек технологий ##
+ Python 3.10.10
+ Django 3.2
+ Django REST Framework 3.12
+ PostgresQL
+ Docker
+ Postman
+ GitHub Actions

## Для развертывания этого проекта необходимы следующие шаги: ##
Загрузите проект с использованием SSH:
```python
git clone git@github.com:Mary8jk/Social-network-Tasty.git
```
Подключитесь к своему серверу:
```python
ssh <server user>@<server IP>
```
Установите Docker на свой сервер:
```python
sudo apt install docker.io
```
Установите Docker Compose (для Linux):
```python
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
Получите разрешение для docker-compose:
```python
sudo chmod +x /usr/local/bin/docker-compose
```
Создайте директорию проекта:
```python
mkdir foodgram && cd foodgram/
```
Создайте env-file:
```python
touch .env
```
Добавьте в env-file данные:
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
Скопируйте файлы из 'nginx/' (на вашем локальном ПК) на ваш сервер:
```python
scp -r nginx/* <server user>@<server IP>:/home/<server user>/foodgram/
```
Запустите docker-compose:
```python
sudo docker-compose up -d
```
