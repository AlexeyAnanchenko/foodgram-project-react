# Foodgram
Cайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект написан в рамках дипломной работы на Яндекс-Практикум. Мной реализована backend часть сервиса (API), а именно:

- Регистрация / авторизация пользователя.
- Создание, изменение и удаление контента (рецептов).
- Подписка на авторов.
- Добавление рецептов в избранное, а так же в корзину покупок.
- Скачивание списка покупок в .txt формате на основе рецептов в корзине покупок клиента
- Фильтрация и пагинация выдачи рецептов.
- Настройки прав доступа в зависимости от вида операции.
- Настройка админ-панели

Помимо этого реализована настройка docker-compose для разворачивания проекта (4 контейнера: frontend(Javascript), nginx, БД(PostgreSQL), backend(DRF)), а так же CI/CD через workflow Github Actions:
1. Проверка кода на PEP8
2. Создание и отправка Docker образа в DockerHub
3. Деплой на сервер
4. Отправка уведомления в Telegram

Стек технологий:
- Django
- Django Rest Framework
- PostgreSQL
- Docker
- Gunicorn
- nginx

### Протестировать проект можно по пути:

1. http://foodgram.viewdns.net/ - Главная страница, переносит на эндпоинты frontend-части проекта

2. http://foodgram.viewdns.net/api/docs/ - документация по реализованному api на Django


## Как развернуть проект на локальном компьютере

1. Клонировать репозиторий:

```sh
git clone git@github.com:AlexeyAnanchenko/foodgram-project-react.git
```

3. Остановить службу nginx (если запущена):

```sh
sudo systemctl stop nginx
```

4. Установите docker и docker-compose (если не установлено), с этим вам поможет официальная документация: https://docs.docker.com/compose/install

5. Перейдите в папку infra и создайте файл с требуемыми переменными окружения:
    
- SECRET_KEY (ключ Django-проекта)
- DB_ENGINE (используемая база, по умолчанию django.db.backends.postgresql)
- DB_NAME (имя базы)
- POSTGRES_USER (пользователь базы)
- POSTGRES_PASSWORD (пароль пользователя)
- DB_HOST (хост базы данных)
- DB_PORT (порт базы данных)

6. Запустите проект с помощью docker-compose:

```sh
sudo docker-compose up -d
```

7. Выполните миграции и загрузите подготовленные данные в БД:

```sh
sudo docker-compose exec web python manage.py migrate
```

```sh
sudo docker-compose exec web python manage.py loaddata dump.json
```

8. Соберите статику:

```sh
sudo docker-compose exec web python manage.py collectstatic --no-input
```

Готово!

### Пути проекта

1. http://localhost/ - Главная страница, переносит на эндпоинты frontend-части проекта

2. http://localhost/admin/ - админ-панель проекта

3. http://localhost/redoc/ - документация по реализованному api на Django

### Автор

Ананченко Алексей

### Лицензия

MIT License

https://github.com/AlexeyAnanchenko/foodgram-project-react/blob/master/LICENSE
