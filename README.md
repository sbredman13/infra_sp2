# Проект infra_sp2
### Проект контейнеризации приложения API_YAMDB в Docker
Проект позволяет развернуть приложение api_yamdb на любом компьютере
### Технологии
Python 3.7
Django 2.2.19
docker
rest_api
pip - менеджер пакетов
docker - контейниризатор приложений
### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt
- Создайте файл .env с переменными окружения в директории infra_sp2/infra
Пример файла и необходимые переменные:
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=admin # логин для подключения к базе данных
POSTGRES_PASSWORD=admin # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
SECRET_KEY='admin'
```
pip install -r requirements.txt
```
- Соберите контейнеры и образы
```
docker-compose up -d --build
```
- Выполните миграции
```
docker-compose exec web python manage.py migrate
- Загрузите статику
```
docker-compose exec web python manage.py collectstatic --no-input
- Наполните Базу данных данными из файла фикстур
```
python manage.py loaddata infra_sp2/infra/fixtures.json

### Автор
Сергей Шапшинов и замечательная команда Яндекс. Практикума