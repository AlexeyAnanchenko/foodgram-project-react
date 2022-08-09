# Foodgram
Cайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект написан в рамках дипломной работы на Яндекс-Практикум. Мной реализована backend часть сервиса (API), а так же настройка CI/CD, а именно:

- Регистрация / авторизация пользователя.
- Создание, изменение и удаление контента (рецептов).
- Подписка на авторов.
- Добавление рецептов в избранное, а так же в корзину покупок.
- Скачивание списка покупок в .txt формате на основе рецептов в корзине покупок клиента
- Фильтрация и пагинация выдачи рецептов.
- Настройки прав доступа в зависимости от вида операции.
- Настройка админ-панели
- CI/CD через workflow Github Actions (проверка кода на PEP8, Создание и отправка Docker образа в DockerHub, Деплой на сервер, отправка уведомления в Telegram)

Стек технологий:
- Django
- Django Rest Framework
- PostgreSQL
- Docker
- Gunicorn
- nginx

Подробный обзор реализованных эндпоинтов API с примерами запросов можно посмотреть в файле Redoc по пути:
http://localhost/api/docs/

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

### Автор

Ананченко Алексей

### Бейдж со статусом Workflow:
![example workflow](https://github.com/AlexeyAnanchenko/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg)

### Лицензия

MIT License

https://github.com/AlexeyAnanchenko/foodgram-project-react/blob/master/LICENSE