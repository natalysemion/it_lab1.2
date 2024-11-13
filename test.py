import unittest
from datetime import date

from task.py import Database, Table, DateInterval

class TestDatabaseFunctions(unittest.TestCase):

    def test_create_table(self):
        # Створюємо базу даних та таблицю
        db = Database("TestDB")
        schema = [("id", int), ("name", str), ("dob", date)]
        db.create_table("users", schema)

        # Перевіряємо, чи таблиця була створена
        self.assertIn("users", db.tables)
        self.assertEqual(db.tables["users"].name, "users")
        self.assertEqual(db.tables["users"].get_schema(), schema)

    def test_add_row(self):
        # Створюємо базу даних та таблицю
        db = Database("TestDB")
        schema = [("id", int), ("name", str), ("dob", date)]
        db.create_table("users", schema)
        table = db.tables["users"]

        # Додаємо рядок у таблицю
        row_data = [1, "John Doe", date(1990, 5, 15)]
        table.add_row(row_data)

        # Перевіряємо, чи рядок додано
        self.assertEqual(len(table.rows), 1)
        self.assertEqual(table.rows[0], row_data)

    def test_edit_row(self):
        # Створюємо базу даних та таблицю
        db = Database("TestDB")
        schema = [("id", int), ("name", str), ("dob", date)]
        db.create_table("users", schema)
        table = db.tables["users"]

        # Додаємо рядок у таблицю
        row_data = [1, "John Doe", date(1990, 5, 15)]
        table.add_row(row_data)

        # Редагуємо рядок
        new_row_data = [1, "John Doe", date(1992, 8, 23)]
        old_data = table.edit_row(0, new_row_data)

        # Перевіряємо, чи редагування успішне
        self.assertEqual(old_data, row_data)  # Перевіряємо старі дані
        self.assertEqual(table.rows[0], new_row_data)  # Перевіряємо нові дані

    def test_delete_row(self):
        # Створюємо базу даних та таблицю
        db = Database("TestDB")
        schema = [("id", int), ("name", str), ("dob", date)]
        db.create_table("users", schema)
        table = db.tables["users"]

        # Додаємо рядок у таблицю
        row_data = [1, "John Doe", date(1990, 5, 15)]
        table.add_row(row_data)

        # Видаляємо рядок
        table.delete_row(0)

        # Перевіряємо, чи рядок видалено
        self.assertEqual(len(table.rows), 0)

    def test_difference_between_tables(self):
        # Створюємо базу даних та таблиці
        db = Database("TestDB")
        schema = [("id", int), ("name", str), ("dob", date)]
        db.create_table("users", schema)
        db.create_table("employees", schema)

        users_table = db.tables["users"]
        employees_table = db.tables["employees"]

        # Додаємо різні дані в таблиці
        users_table.add_row([1, "John Doe", date(1990, 5, 15)])
        employees_table.add_row([2, "Jane Smith", date(1988, 4, 11)])

        # Перевіряємо різницю
        diff = users_table.difference(employees_table)
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0], [1, "John Doe", date(1990, 5, 15)])

if __name__ == '__main__':
    unittest.main()
