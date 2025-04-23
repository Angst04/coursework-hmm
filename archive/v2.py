import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import math
import os

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
                product = p * q
                if product not in semiprimes:
                    semiprimes.append(product)
                if len(semiprimes) >= count:
                    return sorted(semiprimes[:count])
        return sorted(semiprimes)

    @staticmethod
    def ker(a):
        a = abs(a)
        while a >= 10:
            a = sum(int(d) for d in str(a))
        return a

class Database:
    def __init__(self):
        os.makedirs('data', exist_ok=True)
        self.conn = sqlite3.connect('data/database.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS semiprimes
                             (id INTEGER PRIMARY KEY, value INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ker_values
                             (id INTEGER PRIMARY KEY, x INTEGER, y INTEGER, value INTEGER)''')
        self.conn.commit()

    def save_semiprimes(self, data):
        self.cursor.execute('DELETE FROM semiprimes')
        self.cursor.executemany('INSERT INTO semiprimes (value) VALUES (?)', 
                               [(x,) for x in data])
        self.conn.commit()

    def save_ker_values(self, data):
        self.cursor.execute('DELETE FROM ker_values')
        self.cursor.executemany('INSERT INTO ker_values (x, y, value) VALUES (?, ?, ?)',
                               [(x, y, v) for x, row in enumerate(data) for y, v in enumerate(row)])
        self.conn.commit()

class HMM:
    @staticmethod
    def hmm_n(data, mod):
        return [x % mod for x in data]

    @staticmethod
    def hmm_b(data, base):
        return [x // base for x in data]

    @staticmethod
    def hmm_dn(data, mod):
        return [[v % mod for v in row] for row in data]

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Хромоматематическое моделирование")
        self.geometry("1200x800")
        self.db = Database()
        self.create_menu()
        self.create_dirs()

    def create_dirs(self):
        os.makedirs('help', exist_ok=True)
        os.makedirs('source', exist_ok=True)

    def create_menu(self):
        menu = tk.Menu(self)
        
        # Меню данных
        data_menu = tk.Menu(menu, tearoff=0)
        data_menu.add_command(label="Сгенерировать данные", command=self.generate_data)
        menu.add_cascade(label="Данные", menu=data_menu)
        
        # Меню форм
        forms_menu = tk.Menu(menu, tearoff=0)
        forms_menu.add_command(label="1D: Полупростые числа", command=self.open_1d)
        forms_menu.add_command(label="2D: Ker(X*Y - X+Y)", command=self.open_2d)
        menu.add_cascade(label="Формы", menu=forms_menu)
        
        # Справка
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        help_menu.add_command(label="Справка", command=self.show_help)
        menu.add_cascade(label="Справка", menu=help_menu)
        
        self.config(menu=menu)

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
        
        messagebox.showinfo("Успех", "Данные успешно сгенерированы!")

    def open_1d(self):
        window = tk.Toplevel(self)
        window.title("1D: Полупростые числа")
        
        # Получение данных
        self.db.cursor.execute("SELECT value FROM semiprimes")
        data = [row[0] for row in self.db.cursor.fetchall()]
        
        # Панель управления
        control_frame = ttk.Frame(window)
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="Модель:").pack(side=tk.LEFT)
        model_var = tk.StringVar(value='HMM_N')
        model_combobox = ttk.Combobox(control_frame, textvariable=model_var, values=['HMM_N', 'HMM_B'])
        model_combobox.pack(side=tk.LEFT)
        
        ttk.Label(control_frame, text="Параметр:").pack(side=tk.LEFT)
        param_entry = ttk.Entry(control_frame)
        param_entry.pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="Применить", command=lambda: self.update_1d_viz(data, model_var.get(), param_entry.get())).pack(side=tk.LEFT)
        
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
        
        # Замощение
        tiling_frame = ttk.Frame(tab_control)
        self.draw_tiling(tiling_frame, data)
        tab_control.add(tiling_frame, text="Замощение")
        
        # Точечный график
        scatter_frame = ttk.Frame(tab_control)
        self.draw_scatter(scatter_frame, data)
        tab_control.add(scatter_frame, text="Точечный график")
        
        tab_control.pack(expand=1, fill="both")

    def update_1d_viz(self, data, model, param):
        try:
            if model == 'HMM_N':
                mod = int(param)
                processed_data = HMM.hmm_n(data, mod)
            elif model == 'HMM_B':
                base = int(param)
                processed_data = HMM.hmm_b(data, base)
            else:
                processed_data = data
            # Обновление всех визуализаций
            self.draw_spiral(self.spiral_frame, processed_data)
            self.draw_histogram(self.hist_frame, processed_data)
            self.draw_tiling(self.tiling_frame, processed_data)
            self.draw_scatter(self.scatter_frame, processed_data)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный параметр")

    def draw_spiral(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600)
        canvas.pack()
        
        center_x, center_y = 300, 300
        step = 5
        x, y = 0, 0
        dx, dy = 0, -1
        
        for num in data:
            if -300//step < x < 300//step and -300//step < y < 300//step:
                canvas.create_oval(
                    center_x + x*step, center_y + y*step,
                    center_x + x*step + 2, center_y + y*step + 2,
                    fill="black"
                )
            
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                dx, dy = -dy, dx
            
            x, y = x + dx, y + dy

    def draw_histogram(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=400)
        canvas.pack()
        
        max_val = max(data) if data else 1
        bin_count = 20
        bin_width = 600 // bin_count
        
        for i in range(bin_count):
            count = len([x for x in data if i*(max_val/bin_count) <= x < (i+1)*(max_val/bin_count)])
            height = 350 * count / len(data) if data else 0
            canvas.create_rectangle(
                i*bin_width, 380 - height,
                (i+1)*bin_width, 380,
                fill="blue"
            )

    def draw_tiling(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600)
        canvas.pack()
        
        size = 20
        colors = ['#FFB6C1', '#87CEFA', '#98FB98', '#DDA0DD']
        for i, num in enumerate(data[:100]):
            x = (i % 10) * size
            y = (i // 10) * size
            color = colors[num % len(colors)]
            canvas.create_rectangle(x, y, x+size, y+size, fill=color)

    def draw_scatter(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600)
        canvas.pack()
        
        max_val = max(data) if data else 1
        for i, val in enumerate(data):
            x = (i % 100) * 6
            y = 600 - (val / max_val * 600) if max_val != 0 else 0
            canvas.create_oval(x-2, y-2, x+2, y+2, fill="red")

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
        
        # Панель управления
        control_frame = ttk.Frame(window)
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="Модель:").pack(side=tk.LEFT)
        model_var = tk.StringVar(value='HMM_DN')
        model_combobox = ttk.Combobox(control_frame, textvariable=model_var, values=['HMM_DN'])
        model_combobox.pack(side=tk.LEFT)
        
        ttk.Label(control_frame, text="Параметр:").pack(side=tk.LEFT)
        param_entry = ttk.Entry(control_frame)
        param_entry.pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="Применить", command=lambda: self.update_2d_viz(data, model_var.get(), param_entry.get())).pack(side=tk.LEFT)
        
        # Визуализации
        tab_control = ttk.Notebook(window)
        
        # Тепловая карта
        heatmap_frame = ttk.Frame(tab_control)
        self.draw_heatmap(heatmap_frame, data)
        tab_control.add(heatmap_frame, text="Тепловая карта")
        
        # Контурная карта
        contour_frame = ttk.Frame(tab_control)
        self.draw_contour(contour_frame, data)
        tab_control.add(contour_frame, text="Контурная карта")
        
        # 3D-поверхность
        surface_frame = ttk.Frame(tab_control)
        self.draw_3d_surface(surface_frame, data)
        tab_control.add(surface_frame, text="3D-поверхность")
        
        tab_control.pack(expand=1, fill="both")

    def update_2d_viz(self, data, model, param):
        try:
            if model == 'HMM_DN':
                mod = int(param)
                processed_data = HMM.hmm_dn(data, mod)
            else:
                processed_data = data
            self.draw_heatmap(self.heatmap_frame, processed_data)
            self.draw_contour(self.contour_frame, processed_data)
            self.draw_3d_surface(self.surface_frame, processed_data)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный параметр")

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
                canvas.create_rectangle(
                    x*cell_size, y*cell_size,
                    (x+1)*cell_size, (y+1)*cell_size,
                    fill=color, outline=""
                )

    def draw_contour(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600)
        canvas.pack()
        
        levels = [0, 2, 4, 6, 8]
        cell_size = 5
        for x in data:
            for y in data[x]:
                value = data[x][y]
                if value in levels:
                    canvas.create_rectangle(
                        x*cell_size, y*cell_size,
                        (x+1)*cell_size, (y+1)*cell_size,
                        fill='black'
                    )

    def draw_3d_surface(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600)
        canvas.pack()
        
        cell_size = 5
        for x in data:
            for y in data[x]:
                value = data[x][y]
                height = value * 2
                canvas.create_rectangle(
                    x*cell_size, 600 - y*cell_size - height,
                    (x+1)*cell_size, 600 - y*cell_size,
                    fill='#%02x%02x%02x' % (0, 0, 255 - value*20)
                )

    def show_about(self):
        messagebox.showinfo("О программе", 
                          "Программа для хромоматематического моделирования\n"
                          "Версия 2.0\n"
                          "Автор: Ваше имя")

    def show_help(self):
        messagebox.showinfo("Справка", 
                          "1. Сгенерируйте данные через меню 'Данные'\n"
                          "2. Выберите форму для визуализации\n"
                          "3. Используйте параметры для настройки моделей")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()