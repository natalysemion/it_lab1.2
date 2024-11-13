import os
import pickle
from datetime import date
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from pathlib import Path


# Клас для інтервалу дат
class DateInterval:
    def __init__(self, start_date, end_date):
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise Exception("Both start and end must be of type 'date'.")
        if start_date > end_date:
            raise Exception("Start date cannot be after end date.")
        self.start_date = start_date
        self.end_date = end_date

    def __str__(self):
        return f"{self.start_date} to {self.end_date}"


# Клас для таблиці
class Table:
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema  # Список пар (ім'я атрибуту, тип атрибуту)
        self.rows = []

    def validate_row(self, row_data):
        """Перевіряє, чи відповідають дані рядка схемі таблиці"""
        if len(row_data) != len(self.schema):
            raise Exception("Row length does not match table schema.")
        for (field_name, field_type), value in zip(self.schema, row_data):
            if field_type == str and len(value) > 1:  # Для char обмежуємо до 1 символу
                raise Exception(f"Invalid type for field '{field_name}'. Expected char, got string with length > 1.")
            if not isinstance(value, field_type) and not (
                    field_type == DateInterval and isinstance(value, DateInterval)):
                raise Exception(
                    f"Invalid type for field '{field_name}'. Expected {field_type.__name__}, got {type(value).__name__}.")

    def add_row(self, row_data):
        """Додає рядок у таблицю після валідації"""
        self.validate_row(row_data)
        self.rows.append(row_data)

    def edit_row(self, row_index, new_data):
        """Редагує рядок за індексом"""
        old_data = self.rows[row_index]
        try:
            self.validate_row(new_data)
            self.rows[row_index] = new_data
            return old_data  # Повертаємо старі дані
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None  # Якщо валідація не пройшла

    def delete_row(self, row_index):
        """Видаляє рядок за індексом"""
        if row_index < 0 or row_index >= len(self.rows):
            raise Exception("Invalid row index.")
        del self.rows[row_index]

    def view_table(self):
        """Повертає усі рядки таблиці"""
        return self.rows

    def get_schema(self):
        """Повертає схему таблиці"""
        return self.schema

    def difference(self, other_table):
        """Повертає різницю між двома таблицями"""
        if self.schema != other_table.schema:
            raise Exception("Schemas do not match. Cannot compute difference.")

        diff = []
        for row in self.rows:
            if row not in other_table.rows:
                diff.append(row)
        return diff


# Клас для бази даних
class Database:
    def __init__(self, name):
        self.name = name
        self.tables = {}

    def create_table(self, table_name, schema):
        """Створює таблицю з переданою схемою"""
        if table_name in self.tables:
            raise Exception(f"Table '{table_name}' already exists.")
        self.tables[table_name] = Table(table_name, schema)

    def drop_table(self, table_name):
        """Видаляє таблицю з бази"""
        if table_name not in self.tables:
            raise Exception(f"Table '{table_name}' does not exist.")
        del self.tables[table_name]

    def save_to_disk(self, filename):
        """Зберігає базу даних у файл"""
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_from_disk(filename):
        """Зчитує базу даних із файлу"""
        with open(filename, 'rb') as f:
            return pickle.load(f)


# Простий GUI для роботи з базою даних і таблицями
class DatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Manager")
        self.database = None
        self.save_directory = self.get_default_save_directory()

        # Поле для назви бази даних
        self.db_name_label = tk.Label(root, text="Database Name:")
        self.db_name_label.grid(row=0, column=0)

        self.db_name_entry = tk.Entry(root)
        self.db_name_entry.grid(row=0, column=1)

        # Кнопка для створення бази даних
        self.create_db_button = tk.Button(root, text="Create Database", command=self.create_database)
        self.create_db_button.grid(row=1, column=0, columnspan=2)

        # Поле для назви таблиці
        self.table_name_label = tk.Label(root, text="Table Name:")
        self.table_name_label.grid(row=2, column=0)

        self.table_name_entry = tk.Entry(root)
        self.table_name_entry.grid(row=2, column=1)

        # Кнопка для створення таблиці
        self.create_table_button = tk.Button(root, text="Create Table", command=self.create_table)
        self.create_table_button.grid(row=3, column=0, columnspan=2)

        # Кнопка для видалення таблиці
        self.drop_table_button = tk.Button(root, text="Drop Table", command=self.drop_table)
        self.drop_table_button.grid(row=4, column=0, columnspan=2)

        # Кнопка для перегляду таблиці
        self.view_table_button = tk.Button(root, text="View Table", command=self.view_table)
        self.view_table_button.grid(row=5, column=0, columnspan=2)

        # Кнопка для додавання рядка
        self.add_row_button = tk.Button(root, text="Add Row", command=self.add_row)
        self.add_row_button.grid(row=6, column=0, columnspan=2)

        # Кнопка для редагування рядка
        self.edit_row_button = tk.Button(root, text="Edit Row", command=self.edit_row)
        self.edit_row_button.grid(row=7, column=0, columnspan=2)

        # Кнопка для скасування редагування
        self.undo_button = tk.Button(root, text="Undo Edit", command=self.undo_edit)
        self.undo_button.grid(row=8, column=0, columnspan=2)

        # Кнопка для збереження бази даних на диск
        self.save_button = tk.Button(root, text="Save Database", command=self.save_database)
        self.save_button.grid(row=9, column=0, columnspan=2)

        # Кнопка для завантаження бази даних з диска
        self.load_button = tk.Button(root, text="Load Database", command=self.load_database)
        self.load_button.grid(row=10, column=0, columnspan=2)

        # Кнопка для обчислення різниці між таблицями
        self.difference_button = tk.Button(root, text="Difference", command=self.difference_between_tables)
        self.difference_button.grid(row=11, column=0, columnspan=2)

        # Віджет для перегляду даних таблиці
        self.table_view = ttk.Treeview(root)
        self.table_view.grid(row=12, column=0, columnspan=2)

        # Автоматичне завантаження бази при запуску
        self.auto_load_database()

        # Для зберігання даних про редагування
        self.last_edited_row_data = None
        self.last_edited_row_index = None

    def create_database(self):
        db_name = self.db_name_entry.get()
        if db_name:
            self.database = Database(db_name)
            messagebox.showinfo("Success", f"Database '{db_name}' created!")
        else:
            messagebox.showerror("Error", "Database name cannot be empty.")

    def create_table(self):
        if not self.database:
            messagebox.showerror("Error", "Create a database first.")
            return

        table_name = self.table_name_entry.get()
        if not table_name:
            messagebox.showerror("Error", "Table name cannot be empty.")
            return

        schema_input = simpledialog.askstring("Schema Input", "Enter schema as 'field_name:type, field_name:type':")
        if schema_input:
            try:
                schema = []
                for field in schema_input.split(','):
                    field_name, field_type = field.split(':')
                    field_type = field_type.strip()
                    if field_type == "int":
                        schema.append((field_name.strip(), int))
                    elif field_type == "real":
                        schema.append((field_name.strip(), float))
                    elif field_type == "char":
                        schema.append((field_name.strip(), str))  # char обробляється як str з обмеженням
                    elif field_type == "string":
                        schema.append((field_name.strip(), str))
                    elif field_type == "date":
                        schema.append((field_name.strip(), date))
                    elif field_type == "dateInvl":
                        schema.append((field_name.strip(), DateInterval))
                    else:
                        raise Exception(f"Invalid type '{field_type}' for field '{field_name.strip()}'.")
                self.database.create_table(table_name, schema)
                messagebox.showinfo("Success", f"Table '{table_name}' created!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def drop_table(self):
        if not self.database:
            messagebox.showerror("Error", "Create a database first.")
            return

        table_name = self.table_name_entry.get()
        if not table_name:
            messagebox.showerror("Error", "Table name cannot be empty.")
            return

        try:
            self.database.drop_table(table_name)
            messagebox.showinfo("Success", f"Table '{table_name}' dropped!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_row(self):
        if not self.database:
            messagebox.showerror("Error", "Create a database first.")
            return

        table_name = self.table_name_entry.get()
        if not table_name:
            messagebox.showerror("Error", "Table name cannot be empty.")
            return

        if table_name not in self.database.tables:
            messagebox.showerror("Error", f"Table '{table_name}' does not exist.")
            return

        table = self.database.tables[table_name]
        schema = table.get_schema()
        row_data = []

        for field in schema:
            value = simpledialog.askstring("Input", f"Enter value for '{field[0]}' ({field[1].__name__}):")
            if field[1] == int:
                row_data.append(int(value))
            elif field[1] == float:
                row_data.append(float(value))
            elif field[1] == str:
                row_data.append(value)
            elif field[1] == date:
                year, month, day = map(int, value.split('-'))
                row_data.append(date(year, month, day))
            elif field[1] == DateInterval:
                start_date_str = simpledialog.askstring("Input", "Enter start date (YYYY-MM-DD):")
                end_date_str = simpledialog.askstring("Input", "Enter end date (YYYY-MM-DD):")
                start_year, start_month, start_day = map(int, start_date_str.split('-'))
                end_year, end_month, end_day = map(int, end_date_str.split('-'))
                start_date = date(start_year, start_month, start_day)
                end_date = date(end_year, end_month, end_day)
                row_data.append(DateInterval(start_date, end_date))

        try:
            table.add_row(row_data)
            messagebox.showinfo("Success", "Row added!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_row(self):
        if not self.database:
            messagebox.showerror("Error", "Create a database first.")
            return

        table_name = self.table_name_entry.get()
        if not table_name:
            messagebox.showerror("Error", "Table name cannot be empty.")
            return

        if table_name not in self.database.tables:
            messagebox.showerror("Error", f"Table '{table_name}' does not exist.")
            return

        row_index = simpledialog.askinteger("Edit Row", "Enter row index to edit:")
        if row_index is None or row_index < 0:
            messagebox.showerror("Error", "Invalid row index.")
            return

        table = self.database.tables[table_name]
        schema = table.get_schema()
        new_row_data = []

        for field in schema:
            value = simpledialog.askstring("Input", f"Enter new value for '{field[0]}' ({field[1].__name__}):")
            if field[1] == int:
                new_row_data.append(int(value))
            elif field[1] == float:
                new_row_data.append(float(value))
            elif field[1] == str:
                new_row_data.append(value)
            elif field[1] == date:
                year, month, day = map(int, value.split('-'))
                new_row_data.append(date(year, month, day))
            elif field[1] == DateInterval:
                start_date_str = simpledialog.askstring("Input", "Enter start date (YYYY-MM-DD):")
                end_date_str = simpledialog.askstring("Input", "Enter end date (YYYY-MM-DD):")
                start_year, start_month, start_day = map(int, start_date_str.split('-'))
                end_year, end_month, end_day = map(int, end_date_str.split('-'))
                start_date = date(start_year, start_month, start_day)
                end_date = date(end_year, end_month, end_day)
                new_row_data.append(DateInterval(start_date, end_date))

        # Зберігаємо старі дані для можливості скасування
        old_data = table.edit_row(row_index, new_row_data)
        if old_data is not None:
            self.last_edited_row_data = old_data
            self.last_edited_row_index = row_index
            messagebox.showinfo("Success", "Row edited!")
        else:
            messagebox.showerror("Error", "Edit failed due to validation errors.")

    def undo_edit(self):
        if self.last_edited_row_data is not None and self.last_edited_row_index is not None:
            table_name = self.table_name_entry.get()
            table = self.database.tables[table_name]
            table.rows[self.last_edited_row_index] = self.last_edited_row_data
            messagebox.showinfo("Success", "Edit undone!")
            self.last_edited_row_data = None
            self.last_edited_row_index = None
        else:
            messagebox.showerror("Error", "No edit to undo.")

    def view_table(self):
        if not self.database:
            messagebox.showerror("Error", "Create a database first.")
            return

        table_name = self.table_name_entry.get()
        if not table_name:
            messagebox.showerror("Error", "Table name cannot be empty.")
            return

        if table_name not in self.database.tables:
            messagebox.showerror("Error", f"Table '{table_name}' does not exist.")
            return

        table = self.database.tables[table_name]
        rows = table.view_table()

        # Очищення виджету перед відображенням нових даних
        self.table_view.delete(*self.table_view.get_children())

        # Відображення даних у Treeview
        self.table_view["columns"] = [field[0] for field in table.get_schema()]
        for field in table.get_schema():
            self.table_view.heading(field[0], text=field[0])

        for row in rows:
            self.table_view.insert("", "end", values=row)

    def save_database(self):
        db_name = self.db_name_entry.get()
        if not db_name:
            messagebox.showerror("Error", "Database name cannot be empty.")
            return

        filename = os.path.join(self.save_directory, f"{db_name}.db")
        self.database.save_to_disk(filename)
        messagebox.showinfo("Success", f"Database saved to '{filename}'.")

    def load_database(self):
        db_name = self.db_name_entry.get()
        if not db_name:
            messagebox.showerror("Error", "Database name cannot be empty.")
            return

        filename = os.path.join(self.save_directory, f"{db_name}.db")
        if os.path.exists(filename):
            self.database = Database.load_from_disk(filename)
            messagebox.showinfo("Success", f"Database '{db_name}' loaded!")
        else:
            messagebox.showerror("Error", f"Database '{db_name}' not found.")

    def difference_between_tables(self):
        if not self.database:
            messagebox.showerror("Error", "Create a database first.")
            return

        table_name_1 = simpledialog.askstring("Table 1 Name", "Enter the first table name:")
        table_name_2 = simpledialog.askstring("Table 2 Name", "Enter the second table name:")

        if not table_name_1 or not table_name_2:
            messagebox.showerror("Error", "Both table names must be provided.")
            return

        if table_name_1 not in self.database.tables or table_name_2 not in self.database.tables:
            messagebox.showerror("Error", "One or both tables do not exist.")
            return

        table_1 = self.database.tables[table_name_1]
        table_2 = self.database.tables[table_name_2]

        try:
            diff = table_1.difference(table_2)
            if diff:
                messagebox.showinfo("Difference", f"Rows in '{table_name_1}' not in '{table_name_2}':\n{diff}")
            else:
                messagebox.showinfo("Difference", "No differences found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_default_save_directory(self):
        """Повертає шлях до директорії Documents користувача"""
        return str(Path.home() / "Documents")

    def auto_load_database(self):
        """Автоматично завантажує базу даних при запуску програми"""
        db_name = self.db_name_entry.get() or "default_database"
        filename = os.path.join(self.save_directory, f"{db_name}.db")
        if os.path.exists(filename):
            self.database = Database.load_from_disk(filename)
            messagebox.showinfo("Success", f"Database '{db_name}' loaded!")


# Головна частина програми
if __name__ == "__main__":
    root = tk.Tk()
    db_gui = DatabaseGUI(root)
    root.mainloop()