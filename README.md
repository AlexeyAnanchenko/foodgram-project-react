### Ревьюеру
Адрес сервера: http://foodgram.viewdns.net/

Данные для входа в раздел администратора:
- email - admin@yandex.ru
- password - admin

# Foodgram
Cайт Foodgram, «Продуктовый помощник».

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
http://foodgram.viewdns.net/api/docs/

## Как развернуть проект на сервере

Для начала понадобится добавить Секреты (переменные среды в Github) в свой репозиторий после fork-а:
- DOCKER_USERNAME (имя пользователя в Docker Hub)
- DOCKER_PASSWORD (пароль от учётной записи в Docker Hub)
- HOST (ip-дрес боевого сервера)
- USER (имя пользоватля для подключения к серверу)
- PASSPHRASE (фраза-пароль для использования SSH-ключа)
- SSH-KEY (закрытый ключ компьютера с доступом к серверу)
- TELEGRAM_TO (id Вашего аккаунта в Telegram)
- TELEGRAM_TOKEN (токен бота для рассылки уведомления)
- SECRET_KEY (ключ Django-проекта)
- DB_ENGINE (используемая база, по умолчанию django.db.backends.postgresql)
- DB_NAME (имя базы)
- POSTGRES_USER (пользователь базы)
- POSTGRES_PASSWORD (пароль пользователя)
- DB_HOST (хост базы данных)
- DB_PORT (порт базы данных)

После этого выполнить следующие действия:

1. Клонировать репозиторий:

```sh
git clone git@github.com:AlexeyAnanchenko/foodgram-project-react.git
```

3. Зайти на свой удаленный сервер и остановить службу nginx (если запущена):

```sh
sudo systemctl stop nginx
```

4. Установите docker и docker-compose (если не установлено), с этим вам поможет официальная документация: https://docs.docker.com/compose/install

5. Скопируйте файлы docker-compose.yaml и nginx.conf из папки infra из вашего проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx.conf соответственно.


__Далее после каждого пуша проект будет автоматически разворачиваться на боевом сервере__

__Для корректной работы, после первого деплоя надо сделать следующие операции в контейнере проекта на сервере:__

6. Выполните миграции и создайте суперпользователя:

```sh
sudo docker-compose exec web python manage.py migrate
```

```sh
sudo docker-compose exec web python manage.py createsuperuser
```

7. Соберите статику:

```sh
sudo docker-compose exec web python manage.py collectstatic --no-input
```

8. Загрузите подготовленные данные с помощю менеджмент-команды:

```sh
sudo docker-compose exec web python manage.py import-csv
```

Готово!

### Автор

Ананченко Алексей

### Бейдж со статусом Workflow:
![example workflow](https://github.com/AlexeyAnanchenko/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg)

### Лицензия

MIT License

Copyright (c) 2022 AlexeyAn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
