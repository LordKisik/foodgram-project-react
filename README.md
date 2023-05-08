![foodgram status](https://github.com/LordKisik/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master&event=push)

<h1 align="center">foodgram - продуктовый помощник</h1>
Адрес проекта: http://62.84.119.18/

## Описание проекта
На этом сайте можно публиковать свои рецепты, подписываться на других авторов, добавлять рецепты в списки покупок и в избранное. Доступна фильтрация по тегам. Реализована функция формирования списка покупок на основе ингредиентов в рецептах, добавленных в список покупок.

## Используемые технологии:<br/>
- Django - 3.2.18
- Django Rest Framework - 3.14.0
- Python 3.7
- PostgreSQL
- Docker
- Docker-compose
- Gunicorn
- Nginx
- React
- CI/CD

## Структура проекта:<br/>
- frontend — файлы необходимые для сборки фронтенда приложения
- infra — конфигурационный файл nginx и docker-compose.yml
- backend — файлы для сборки бекенд приложения
- data подготовлены теги и список ингредиентов с единицами измерения
- docs — файлы спецификации API, по которым работает проект

## Локальный запуск проекта в контейнерах:

- Склонировать репозиторий к себе на компьютер и перейти в корневую папку
```
git clone git@github.com:LordKisik/foodgram-project-react.git
```
```
cd foodgram-project-react
```
- Создать файл .env с переменными окружения, необходимыми для работы

> DB_ENGINE=django.db.backends.postgresql<br/>
> DB_NAME=postgres<br/>
> POSTGRES_USER=postgres<br/>
> POSTGRES_PASSWORD=postgres<br/>
> DB_HOST=db<br/>
> DB_PORT=5432<br/>
> SECRET_KEY=postgres<br/>

- Перейти в папку /infra и запустить сборку контейнеров (запущены контейнеры db, web, nginx)
```
sudo docker-compose up -d
```
- Внутри контейнера backend создать миграции, выполнить миграции, создать суперпользователя, собрать статику и загрузить ингредиенты и теги
```
sudo docker-compose exec web python manage.py makemigrations
```
```
sudo docker-compose exec web python manage.py migrate
```
```
sudo docker-compose exec web python manage.py createsuperuser
```
```
sudo docker-compose exec web python manage.py collectstatic --no-input
```
```
sudo docker-compose exec web python manage.py importcsv
```

**Автор проекта:**<br/>

**Виталий Никонов** - https://github.com/LordKisik<br/>