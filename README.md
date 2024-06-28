# FOODGRAM 

## Описание
«Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Установка

Клонировать репозиторий и перейти в него в командной строке:
`git@github.com:Jim-0e/foodgram.git`
Перейти в папку `infra`

Cодержимое env-файла для запуска.
`POSTGRES_USER=foodgram_user`
`POSTGRES_PASSWORD=foodgram_password`
`POSTGRES_DB=foodgram`
`DB_HOST=db`
`DB_PORT=5432`

Запустить docker-compose:
`docker-compose up`

Запустить миграции:
`docker exec infra-backend-1 python  manage.py migrate`

Загрузить все ингредиенты в базу данных
`docker exec infra-backend-1 python manage.py import_ingredients ingredients.csv`

Открыть по адресу:
`http://localhost`

Посмотреть полную документацию к API:
`http://localhost/api/docs/`


## Готовый проект
[foodgram](https://foodgram-eats.ddns.net/)

Админка: 
 - email -> no8@gmail.com
 - password -> 123
# Примеры API 

## Пользователи
`api/users/` - GET Список пользователей
`api/users/` - POST Создание пользователя
` {
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов",
    "password": "Qwerty123"
}`
## Теги
`api/tags/` - GET Список тегов
`api/tags/{id}/` - GET Получение тега

## Рецепты
`api/recipes/` -  GET рецептов
`api/recipes/` -  POST рецепта

{
    "ingredients": [
        {
            "id": 1123,
            "amount": 10
        }
    ],
    "tags": [
            1,
            2
        ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "string",
    "text": "string",
    "cooking_time": 1
}
## Ингредиенты
`api/ingredients/` - GET Список тегов
`api/ingredients/{id}/` - GET Получение тега











