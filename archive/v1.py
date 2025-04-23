import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import math
import os

# Модуль для работы с данными
class DataHandler:
    @staticmethod
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True

    @staticmethod
    def generate_semiprimes(count=1000):
        primes = [i for i in range(2, 10000) if DataHandler.is_prime(i)]
        semiprimes = []
        for p in primes:
            for q in primes:
                if p * q not in semiprimes:
                    semiprimes.append(p * q)
                if len(semiprimes) >= count:
                    return sorted(semiprimes[:count])
        return sorted(semiprimes)

    @staticmethod
    def ker(a):
        a = abs(a)
        while a >= 10:
            a = sum(int(d) for d in str(a))
        return a

# Модуль работы с БД
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS semiprimes
                             (id INTEGER PRIMARY KEY, value INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ker_values
                             (id INTEGER PRIMARY KEY, x INTEGER, y INTEGER, value INTEGER)''')
        self.conn.commit()

    def save_semiprimes(self, data):
        self.cursor.executemany('INSERT INTO semiprimes (value) VALUES (?)', 
                               [(x,) for x in data])
        self.conn.commit()

    def save_ker_values(self, data):
        self.cursor.executemany('INSERT INTO ker_values (x, y, value) VALUES (?, ?, ?)',
                               [(x, y, v) for x, row in enumerate(data) for y, v in enumerate(row)])
        self.conn.commit()

# Модуль HMM
class HMM:
    @staticmethod
    def hmm_n(data, mod):
        return [x % mod for x in data]

    @staticmethod
    def hmm_b(data, base):
        return [x // base for x in data]

# Графический интерфейс
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Хромоматематическое моделирование")
        self.geometry("800x600")
        self.db = Database()
        self.create_menu()
        
        # Создаем каталоги если их нет
        if not os.path.exists('help'):
            os.makedirs('help')

    def create_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)
        
        # Меню данных
        data_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Данные", menu=data_menu)
        data_menu.add_command(label="Сгенерировать данные", command=self.generate_data)
        
        # Меню форм
        forms_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Формы", menu=forms_menu)
        forms_menu.add_command(label="1D: Полупростые числа", command=self.open_1d)
        forms_menu.add_command(label="2D: Ker(X*Y - X+Y)", command=self.open_2d)
        
        # Справка
        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

    def generate_data(self):
        # Генерация 1D данных
        semiprimes = DataHandler.generate_semiprimes(1000)
        self.db.save_semiprimes(semiprimes)
        
        # Генерация 2D данных
        data = []
        for x in range(-50, 50):
            row = []
            for y in range(-50, 50):
                value = DataHandler.ker(x*y - (x+y))
                row.append(value)
            data.append(row)
        self.db.save_ker_values(data)
        
        messagebox.showinfo("Успех", "Данные успешно сгенерированы и сохранены")

    def open_1d(self):
        window = tk.Toplevel(self)
        window.title("1D: Полупростые числа")
        
        # Получение данных из БД
        self.db.cursor.execute("SELECT value FROM semiprimes")
        data = [row[0] for row in self.db.cursor.fetchall()]
        
        # Визуализации
        tab_control = ttk.Notebook(window)
        
        # Спираль Улама
        spiral_frame = ttk.Frame(tab_control)
        self.draw_spiral(spiral_frame, data)
        tab_control.add(spiral_frame, text="Спираль Улама")
        
        # Гистограмма
        hist_frame = ttk.Frame(tab_control)
        self.draw_histogram(hist_frame, data)
        tab_control.add(hist_frame, text="Гистограмма")
        
        tab_control.pack(expand=1, fill="both")

    def draw_spiral(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600)
        canvas.pack()
        
        # Алгоритм отрисовки спирали
        center_x, center_y = 300, 300
        step = 5
        direction = 0
        x, y = 0, 0
        dx, dy = 0, -1
        
        for num in data:
            if -300//step < x < 300//step and -300//step < y < 300//step:
                canvas.create_oval(center_x + x*step, center_y + y*step,
                                  center_x + x*step + 2, center_y + y*step + 2,
                                  fill="black")
            
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                dx, dy = -dy, dx
            
            x, y = x + dx, y + dy

    def draw_histogram(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=400)
        canvas.pack()
        
        max_val = max(data)
        bin_count = 20
        bin_width = 600 // bin_count
        
        for i in range(bin_count):
            count = len([x for x in data if i*(max_val//bin_count) <= x < (i+1)*(max_val//bin_count)])
            height = 300 * count / len(data)
            canvas.create_rectangle(i*bin_width, 350 - height,
                                   (i+1)*bin_width, 350,
                                   fill="blue")

    def open_2d(self):
        window = tk.Toplevel(self)
        window.title("2D: Ker(X*Y - X+Y)")
        
        # Получение данных
        self.db.cursor.execute("SELECT x, y, value FROM ker_values")
        data = {}
        for x, y, v in self.db.cursor.fetchall():
            if x not in data:
                data[x] = {}
            data[x][y] = v
        
        # Визуализации
        tab_control = ttk.Notebook(window)
        
        # Тепловая карта
        heatmap_frame = ttk.Frame(tab_control)
        self.draw_heatmap(heatmap_frame, data)
        tab_control.add(heatmap_frame, text="Тепловая карта")
        
        tab_control.pack(expand=1, fill="both")

    def draw_heatmap(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600)
        canvas.pack()
        
        cell_size = 5
        colors = ['#FF0000', '#FF4500', '#FF8C00', '#FFA500', '#FFFF00',
                 '#ADFF2F', '#7FFF00', '#00FF00', '#32CD32', '#008000']
        
        for x in data:
            for y in data[x]:
                value = data[x][y]
                color = colors[value % len(colors)]
                canvas.create_rectangle(x*cell_size, y*cell_size,
                                      (x+1)*cell_size, (y+1)*cell_size,
                                      fill=color, outline="")

    def show_about(self):
        messagebox.showinfo("О программе", 
                          "Программа для хромоматематического моделирования\n"
                          "Версия 1.0\n"
                          "Автор: Ваше имя")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()