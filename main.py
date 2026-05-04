import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("900x600")

        # Данные книг
        self.books = []
        self.load_data()

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Фрейм для ввода данных
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10)

        # Поле названия книги
        ttk.Label(input_frame, text="Название книги:").grid(row=0, column=0, padx=5, sticky="w")
        self.title_entry = ttk.Entry(input_frame, width=25)
        self.title_entry.grid(row=0, column=1, padx=5)

        # Поле автора
        ttk.Label(input_frame, text="Автор:").grid(row=0, column=2, padx=5, sticky="w")
        self.author_entry = ttk.Entry(input_frame, width=25)
        self.author_entry.grid(row=0, column=3, padx=5)

        # Поле жанра
        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=4, padx=5, sticky="w")
        self.genre_combo = ttk.Combobox(
            input_frame,
            values=["Фантастика", "Детектив", "Роман", "Биография", "Научная литература", "Поэзия", "Другое"],
            width=20
        )
        self.genre_combo.grid(row=0, column=5, padx=5)

        # Поле количества страниц
        ttk.Label(input_frame, text="Страниц:").grid(row=0, column=6, padx=5, sticky="w")
        self.pages_entry = ttk.Entry(input_frame, width=10)
        self.pages_entry.grid(row=0, column=7, padx=5)

        # Кнопка добавления книги
        add_button = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        add_button.grid(row=0, column=8, padx=10)

        # Кнопка удаления книги
        delete_button = ttk.Button(input_frame, text="Удалить выбранную", command=self.delete_book)
        delete_button.grid(row=0, column=9, padx=5)

        # Таблица для отображения книг
        columns = ("ID", "Название", "Автор", "Жанр", "Страниц")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Название":
                self.tree.column(col, width=200)
            elif col == "Автор":
                self.tree.column(col, width=150)
            elif col == "Жанр":
                self.tree.column(col, width=120)
            else:
                self.tree.column(col, width=80)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Фрейм для фильтрации
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=10)

        # Фильтрация по жанру
        ttk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5)
        self.filter_genre = ttk.Combobox(
            filter_frame,
            values=["Все"] + ["Фантастика", "Детектив", "Роман", "Биография", "Научная литература", "Поэзия", "Другое"]
        )
        self.filter_genre.set("Все")
        self.filter_genre.grid(row=0, column=1, padx=5)

        # Фильтрация по количеству страниц
        ttk.Label(filter_frame, text="Страниц больше:").grid(row=0, column=2, padx=5)
        self.min_pages_entry = ttk.Entry(filter_frame, width=10)
        self.min_pages_entry.insert(0, "0")
        self.min_pages_entry.grid(row=0, column=3, padx=5)

        # Кнопки фильтрации
        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=0, column=4, padx=5)

        clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        clear_filter_button.grid(row=0, column=5, padx=5)

        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def validate_input(self, title, author, genre, pages_str):
        """Проверка корректности ввода"""
        if not all([title, author, genre]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return False

        try:
            pages = int(pages_str)
            if pages <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат количества страниц")
            return False

        return True

    def add_book(self):
        """Добавление новой книги"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_combo.get().strip()
        pages_str = self.pages_entry.get().strip()

        if not self.validate_input(title, author, genre, pages_str):
            return

        book = {
            "id": self.get_next_id(),
            "title": title,
            "author": author,
            "genre": genre,
            "pages": int(pages_str)
        }

        self.books.append(book)
        self.save_data()
        self.refresh_table()
        self.clear_input()

    def get_next_id(self):
        """Получение следующего ID для книги"""
        if not self.books:
            return 1
        return max(book["id"] for book in self.books) + 1

    def delete_book(self):
        """Удаление выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления")
            return

        item = selected[0]
        book_id = self.tree.item(item, "values")[0]

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту книгу?"):
            self.books = [b for b in self.books if b["id"] != book_id]
            self.save_data()
            self.refresh_table()

    def clear_input(self):
        "Очистка полей ввода"
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_combo.set("")
        self.pages_entry.delete(0, tk.END)

    def refresh_table(self, data=None):
        """Обновление таблицы с книгами"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        display_data = data if data is not None else self.books

        for book in display_data:
            self.tree.insert("", "end", values=(
                book["id"],
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))

    def apply_filter(self):
        """Применение фильтров"""
        filtered = self.books

        # Фильтр по жанру
        genre_filter = self.filter_genre.get()
        if genre_filter != "Все":
            filtered = [b for b in filtered if b["genre"] == genre_filter]

        # Фильтр по количеству страниц
        min_pages_str = self.min_pages_entry.get()
        if min_pages_str:
            try:
                min_pages = int(min_pages_str)
                filtered = [b for b in filtered if b["pages"] >= min_pages]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат минимального количества страниц")
                return

        self.refresh_table(filtered)

    def clear_filter(self):
        """Сброс фильтров и обновление таблицы"""
        self.filter_genre.set("Все")
        self.min_pages_entry.delete(0, tk.END)
        self.min_pages_entry.insert(0, "0")
        self.refresh_table()

    def save_data(self):
        """Сохранение данных в JSON-файл"""
        try:
            with open("books.json", "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

    def load_data(self):
        """Загрузка данных из JSON-файла"""
        if os.path.exists("books.json"):
            try:
                with open("books.json", "r", encoding="utf-8") as f:
                    self.books = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
                self.books = []
        else:
            self.books = []

    def on_closing(self):
        """Обработка закрытия окна с подтверждением"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти? Данные будут сохранены."):
            self.save_data()
            self.root.destroy()

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()