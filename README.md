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