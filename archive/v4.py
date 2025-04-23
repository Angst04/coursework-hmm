import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import math
import os

class DataHandler:
    @staticmethod
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0: return False
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
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS semiprimes (value INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ker_values (x INTEGER, y INTEGER, value INTEGER)''')
        self.conn.commit()

    def save_semiprimes(self, data):
        self.cursor.execute('DELETE FROM semiprimes')
        self.cursor.executemany('INSERT INTO semiprimes VALUES (?)', [(x,) for x in data])
        self.conn.commit()

    def save_ker_values(self, data):
        self.cursor.execute('DELETE FROM ker_values')
        self.cursor.executemany('INSERT INTO ker_values VALUES (?, ?, ?)', 
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
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))

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
        self.window_1d = tk.Toplevel(self)
        self.window_1d.title("1D: Полупростые числа")
        self.window_1d.configure(bg='#f0f0f0')
        
        # Получение данных
        self.db.cursor.execute("SELECT value FROM semiprimes")
        self.data_1d = [row[0] for row in self.db.cursor.fetchall()]
        
        # Панель управления
        control_frame = ttk.Frame(self.window_1d)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Модель:").grid(row=0, column=0, padx=5)
        self.model_1d_var = tk.StringVar(value='HMM_N')
        model_combobox = ttk.Combobox(control_frame, textvariable=self.model_1d_var, 
                                     values=['HMM_N', 'HMM_B'], width=15)
        model_combobox.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Параметр:").grid(row=0, column=2, padx=5)
        self.param_1d_entry = ttk.Entry(control_frame, width=10)
        self.param_1d_entry.grid(row=0, column=3, padx=5)
        
        ttk.Button(control_frame, text="Применить", 
                  command=self.update_1d_viz).grid(row=0, column=4, padx=5)
        
        # Визуализации
        self.tab_control_1d = ttk.Notebook(self.window_1d)
        
        # Спираль Улама
        self.spiral_frame = ttk.Frame(self.tab_control_1d)
        self.draw_spiral(self.spiral_frame, self.data_1d)
        self.tab_control_1d.add(self.spiral_frame, text="Спираль Улама")
        
        # Гистограмма
        self.hist_frame = ttk.Frame(self.tab_control_1d)
        self.draw_histogram(self.hist_frame, self.data_1d)
        self.tab_control_1d.add(self.hist_frame, text="Гистограмма")
        
        # Замощение
        self.tiling_frame = ttk.Frame(self.tab_control_1d)
        self.draw_tiling(self.tiling_frame, self.data_1d)
        self.tab_control_1d.add(self.tiling_frame, text="Замощение")
        
        # Точечный график
        self.scatter_frame = ttk.Frame(self.tab_control_1d)
        self.draw_scatter(self.scatter_frame, self.data_1d)
        self.tab_control_1d.add(self.scatter_frame, text="Точечный график")
        
        self.tab_control_1d.pack(expand=1, fill="both", padx=10, pady=10)

    def update_1d_viz(self):
        try:
            model = self.model_1d_var.get()
            param = self.param_1d_entry.get()
            
            if model == 'HMM_N':
                mod = int(param)
                processed_data = HMM.hmm_n(self.data_1d, mod)
            elif model == 'HMM_B':
                base = int(param)
                processed_data = HMM.hmm_b(self.data_1d, base)
            else:
                processed_data = self.data_1d
            
            # Обновление всех визуализаций
            self.clear_frame(self.spiral_frame)
            self.draw_spiral(self.spiral_frame, processed_data)
            
            self.clear_frame(self.hist_frame)
            self.draw_histogram(self.hist_frame, processed_data)
            
            self.clear_frame(self.tiling_frame)
            self.draw_tiling(self.tiling_frame, processed_data)
            
            self.clear_frame(self.scatter_frame)
            self.draw_scatter(self.scatter_frame, processed_data)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный числовой параметр")

    def draw_spiral(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600, bg='white')
        canvas.pack()
        
        center_x, center_y = 300, 300
        step = 5
        x, y = 0, 0
        dx, dy = 0, -1
        
        for num in data:
            if -300//step < x < 300//step and -300//step < y < 300//step:
                canvas.create_oval(
                    center_x + x*step - 2, center_y + y*step - 2,
                    center_x + x*step + 2, center_y + y*step + 2,
                    fill="#2c3e50"
                )
            
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                dx, dy = -dy, dx
            
            x, y = x + dx, y + dy
        
        # Добавление подписей
        canvas.create_text(300, 580, text="Спираль Улама", font=('Arial', 12))

    def draw_histogram(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=400, bg='white')
        canvas.pack()
        
        max_val = max(data) if data else 1
        bin_count = 20
        bin_width = 600 // bin_count
        
        for i in range(bin_count):
            lower = i * (max_val / bin_count)
            upper = (i+1) * (max_val / bin_count)
            count = len([x for x in data if lower <= x < upper])
            height = 350 * count / len(data) if data else 0
            
            canvas.create_rectangle(
                i*bin_width, 380 - height,
                (i+1)*bin_width, 380,
                fill="#3498db",
                outline="#2980b9"
            )
        
        # Оси и подписи
        canvas.create_line(0, 380, 600, 380, fill="black")  # Ось X
        canvas.create_text(300, 395, text="Значения", font=('Arial', 10))

    def draw_tiling(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600, bg='white')
        canvas.pack()
        
        size = 20
        colors = ['#e74c3c', '#2ecc71', '#9b59b6', '#f1c40f']
        for i, num in enumerate(data[:100]):
            x = (i % 10) * size
            y = (i // 10) * size
            color = colors[num % len(colors)]
            canvas.create_rectangle(
                x, y, 
                x + size, y + size, 
                fill=color, 
                outline="#34495e"
            )

    def draw_scatter(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600, bg='white')
        canvas.pack()
        
        max_val = max(data) if data else 1
        for i, val in enumerate(data):
            x = (i % 100) * 6
            y = 600 - (val / max_val * 600) if max_val != 0 else 0
            canvas.create_oval(
                x - 2, y - 2, 
                x + 2, y + 2, 
                fill="#e67e22", 
                outline="#d35400"
            )

    def open_2d(self):
        self.window_2d = tk.Toplevel(self)
        self.window_2d.title("2D: Ker(X*Y - X+Y)")
        self.window_2d.configure(bg='#f0f0f0')
        
        # Получение данных
        self.db.cursor.execute("SELECT x, y, value FROM ker_values")
        raw_data = self.db.cursor.fetchall()
        self.data_2d = {}
        for x, y, v in raw_data:
            if x not in self.data_2d:
                self.data_2d[x] = {}
            self.data_2d[x][y] = v
        
        # Панель управления
        control_frame = ttk.Frame(self.window_2d)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Модель:").grid(row=0, column=0, padx=5)
        self.model_2d_var = tk.StringVar(value='HMM_DN')
        model_combobox = ttk.Combobox(control_frame, textvariable=self.model_2d_var, 
                                     values=['HMM_DN'], width=15)
        model_combobox.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Параметр:").grid(row=0, column=2, padx=5)
        self.param_2d_entry = ttk.Entry(control_frame, width=10)
        self.param_2d_entry.grid(row=0, column=3, padx=5)
        
        ttk.Button(control_frame, text="Применить", 
                  command=self.update_2d_viz).grid(row=0, column=4, padx=5)
        
        # Визуализации
        self.tab_control_2d = ttk.Notebook(self.window_2d)
        
        # Тепловая карта
        self.heatmap_frame = ttk.Frame(self.tab_control_2d)
        self.draw_heatmap(self.heatmap_frame, self.data_2d)
        self.tab_control_2d.add(self.heatmap_frame, text="Тепловая карта")
        
        # Контурная карта
        self.contour_frame = ttk.Frame(self.tab_control_2d)
        self.draw_contour(self.contour_frame, self.data_2d)
        self.tab_control_2d.add(self.contour_frame, text="Контурная карта")
        
        # 3D-поверхность
        self.surface_frame = ttk.Frame(self.tab_control_2d)
        self.draw_3d_surface(self.surface_frame, self.data_2d)
        self.tab_control_2d.add(self.surface_frame, text="3D-поверхность")
        
        self.tab_control_2d.pack(expand=1, fill="both", padx=10, pady=10)

    def update_2d_viz(self):
        try:
            model = self.model_2d_var.get()
            param = self.param_2d_entry.get()
            
            if model == 'HMM_DN':
                mod = int(param)
                # Преобразуем данные в двумерный массив
                processed_data = []
                for x in sorted(self.data_2d.keys()):
                    row = []
                    for y in sorted(self.data_2d[x].keys()):
                        row.append(self.data_2d[x][y])
                    processed_data.append(row)
                processed_data = HMM.hmm_dn(processed_data, mod)
                
                # Обновляем данные
                self.data_2d = {}
                for x, row in enumerate(processed_data):
                    for y, v in enumerate(row):
                        if x not in self.data_2d:
                            self.data_2d[x] = {}
                        self.data_2d[x][y] = v
                
                # Обновляем визуализации
                self.clear_frame(self.heatmap_frame)
                self.draw_heatmap(self.heatmap_frame, self.data_2d)
                
                self.clear_frame(self.contour_frame)
                self.draw_contour(self.contour_frame, self.data_2d)
                
                self.clear_frame(self.surface_frame)
                self.draw_3d_surface(self.surface_frame, self.data_2d)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный числовой параметр")

    def draw_heatmap(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600, bg='white')
        canvas.pack()
        
        cell_size = 5
        colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60',
                 '#3498db', '#2980b9', '#9b59b6', '#8e44ad', '#2c3e50']
        
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
        canvas = tk.Canvas(parent, width=600, height=600, bg='white')
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
                        fill='#34495e'
                    )

    def draw_3d_surface(self, parent, data):
        canvas = tk.Canvas(parent, width=600, height=600, bg='white')
        canvas.pack()
        
        cell_size = 5
        for x in data:
            for y in data[x]:
                value = data[x][y]
                height = value * 3
                canvas.create_rectangle(
                    x*cell_size, 600 - y*cell_size - height,
                    (x+1)*cell_size, 600 - y*cell_size,
                    fill='#%02x%02x%02x' % (52, 152, 219)
                )

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def show_about(self):
        messagebox.showinfo("О программе", 
                          "Программа для хромоматематического моделирования\n"
                          "Версия 3.0\n"
                          "Автор: [Ваше имя]")

    def show_help(self):
        messagebox.showinfo("Справка", 
                          "1. Сгенерируйте данные через меню 'Данные'\n"
                          "2. Выберите форму для визуализации\n"
                          "3. Используйте параметры для настройки моделей")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()