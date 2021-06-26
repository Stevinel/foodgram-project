# FOODGRAM
![foodgram](https://github.com/stevinel/foodgram-project/workflows/foodgram/badge.svg)

### «Продуктовый помощник».
Это онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Демо: http://www.foodgram-2021.tk/

### Установка

1. Подготовка

    Приложение работает за счет [Docker] и [docker-compose]

2. Запуск сервиса
    
    Приложение работает в двух docker контейнерах, для сборки и запуска всего окружения необходимо выполнить комманду
 
    ```
    docker-compose up
   ```
    
### Первоначальная настройка

1. Предварительная миграция (создание таблиц в БД)

    ```
    docker-compose run web python manage.py migrate
    ```

2. Создание суперпользователя
    ```
   docker-compose run web python manage.py createsuperuser
   ```
3. Загрузка демонстрационных данных
    ```
   docker-compose run web python manage.py loaddata fixtures.json
   ```

### Используемый стек
* [Python]
* [Django]
* [Docker]
* [Docker-compose]
* [Postgresql]

### Автор
Воронов Станислав.
Сайт создан в рамках обучения на курсах Yandex-Praktikum 
