from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Команда для загрузки тестовых данных'

    def handle(self, *args, **options):
        import csv
        import sqlite3

        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()

        #cur.execute('DELETE FROM recipes_ingredient;',)
        with open(
            "/home/alexey/Dev/foodgram-project-react/data/ingredients.csv"
        ) as file:
            file_read = csv.DictReader(file)
            to_db = [(i['name'], i['measurement_unit']) for i in file_read]
        cur.executemany(
            "INSERT INTO recipes_ingredient (name, "
            "measurement_unit) VALUES (?, ?);",
            to_db
        )

        con.commit()
        con.close()

        print('Загрузка тестовых данных в базу завершена!')
