import csv
import os

import psycopg2
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

load_dotenv()


class Command(BaseCommand):
    help = 'Команда для загрузки тестовых данных'

    def handle(self, *args, **options):

        con = psycopg2.connect(
            database=os.getenv('DB_NAME'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        print('Соединение с базой установлено.')
        cur = con.cursor()

        with open(
            "data/ingredients.csv"
        ) as file:
            file_read = csv.DictReader(file)
            to_db = [(i['name'], i['measurement_unit']) for i in file_read]
        cur.executemany(
            "INSERT INTO recipes_ingredient (name, "
            "measurement_unit) VALUES (%s, %s);",
            to_db
        )

        con.commit()
        con.close()

        print('Загрузка тестовых данных в базу завершена!')
