import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import math
import os

class DataHandler:
    @staticmethod
    def is_prime(n):
        """Проверка числа на простоту"""
        if n < 2: return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0: return False
        return True
    
    @staticmethod
    def is_semiprime(n):
        """Проверка на полупростоту (произведение двух простых)"""
        if n < 4: return False
        factors = []
        temp = n
        for i in range(2, int(math.sqrt(n)) + 1):
            while temp % i == 0:
                factors.append(i)
                temp = temp // i
        return (len(factors) == 2 and factors[0]*factors[1] == n) or (len(factors) == 1 and factors[0]**2 == n)

    @staticmethod
    def generate_semiprimes(count=1000):
        """Генерация полупростых чисел"""
        primes = [i for i in range(2, 10000) if DataHandler.is_prime(i)]
        semiprimes = []
        for i in range(len(primes)):
            for j in range(i, len(primes)):
                product = primes[i] * primes[j]
                if product not in semiprimes:
                    semiprimes.append(product)
                if len(semiprimes) >= count:
                    return sorted(semiprimes)
        return sorted(semiprimes)

    @staticmethod
    def ker(a):
        """Вычисление ядра числа (рекурсивная сумма цифр)"""
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
        """Создание таблиц БД"""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS semiprimes (value INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ker_values (x INTEGER, y INTEGER, value INTEGER)''')
        self.conn.commit()

    def save_semiprimes(self, data):
        """Сохранение полупростых чисел"""
        self.cursor.execute('DELETE FROM semiprimes')
        self.cursor.executemany('INSERT INTO semiprimes VALUES (?)', [(x,) for x in data])
        self.conn.commit()

    def save_ker_values(self, data):
        """Сохранение значений Ker"""
        self.cursor.execute('DELETE FROM ker_values')
        self.cursor.executemany('INSERT INTO ker_values VALUES (?, ?, ?)', 
                               [(x, y, v) for x, row in enumerate(data) for y, v in enumerate(row)])
        self.conn.commit()

class HMM:
    """Хромоматематические модели"""
    @staticmethod
    def hmm_n(data, mod):
        """Модульная арифметика: data[i] % mod"""
        return [x % mod for x in data]

    @staticmethod
    def hmm_b(data, base):
        """Биградиентная модель: data[i] // base"""
        return [x // base for x in data]

    @staticmethod
    def hmm_dn(data, mod):
        """Дискретная модель для 2D: каждая ячейка % mod"""
        return [[v % mod for v in row] for row in data]

    @staticmethod
    def hmm_r(data, a, b):
        """Мультиградиентная модель: (a*x + b*y) % 10"""
        return [[(a * x + b * y) % 10 for y in row] for x, row in enumerate(data)]

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Хромоматематическое моделирование")
        self.geometry("800x600")
        self.db = Database()
        self.create_menu()
        self.create_welcome_screen()
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))
        self.window_1d = None
        self.window_2d = None
        
    def create_welcome_screen(self):
        """Улучшенный экран приветствия"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        description = """Хромоматематическое моделирование - это метод анализа числовых закономерностей 
            с использованием цветового кодирования и геометрических представлений данных.

            Основные возможности программы:

            1. Исследование одномерных объектов (1D):
            - Анализ полупростых чисел (произведение двух простых чисел)
            - Визуализации: 
                * Спираль Улама с цветовой маркировкой
                * Круговые диаграммы распределения
            - Применяемые модели:
                - HMM_N: Модульная арифметика
                - HMM_B: Биградиентная группировка

            2. Исследование двумерных объектов (2D):
            - Анализ функции Ker(X*Y - X+Y)
            - Визуализации:
                * Тепловые карты с цветовым кодированием
                * Контурные карты уровней
            - Применяемые модели:
                - HMM_DN: Дискретное преобразование
                - HMM_R: Мультиградиентная модель

            Технические особенности:
            - Автоматическая генерация данных (1000+ значений)
            - Локальное хранение в SQLite базе данных
            - Настраиваемые параметры моделей
            - Интерактивная легенда и пояснения
            - Встроенная справочная система

            Для начала работы воспользуйтесь меню:
            1. Сгенерируйте данные через меню 'Данные'
            2. Откройте нужные формы моделирования
            3. Экспериментируйте с параметрами моделей
        """
        
        text = tk.Text(main_frame, wrap=tk.WORD, font=('Arial', 12), padx=10, pady=10, height=25)
        text.insert(tk.END, description)
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True)

    def create_menu(self):
        """Создание меню"""
        menu = tk.Menu(self)
        
        data_menu = tk.Menu(menu, tearoff=0)
        data_menu.add_command(label="Сгенерировать данные", command=self.generate_data)
        menu.add_cascade(label="Данные", menu=data_menu)
        
        forms_menu = tk.Menu(menu, tearoff=0)
        forms_menu.add_command(label="1D: Полупростые числа", command=self.open_1d)
        forms_menu.add_command(label="2D: Ker(X*Y - X+Y)", command=self.open_2d)
        menu.add_cascade(label="Формы", menu=forms_menu)
        
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        help_menu.add_command(label="Справка", command=self.show_help)
        menu.add_cascade(label="Справка", menu=help_menu)
        
        self.config(menu=menu)

    def generate_data(self):
        """Генерация данных с проверкой"""
        confirm = messagebox.askyesno("Подтверждение", 
            "Генерация новых данных займет некоторое время.\nПродолжить?")
        if not confirm: return
        
        semiprimes = DataHandler.generate_semiprimes(1000)
        self.db.save_semiprimes(semiprimes)
        
        data = []
        for x in range(-50, 50):
            row = []
            for y in range(-50, 50):
                row.append(DataHandler.ker(x*y - (x+y)))
            data.append(row)
        self.db.save_ker_values(data)
        messagebox.showinfo("Успех", "Данные успешно сгенерированы!\nДоступно:\n- 1000 полупростых чисел\n- 100x100 матрица значений Ker")

    # 1D Визуализации
    def open_1d(self):
        """Окно 1D визуализаций с улучшенным UI"""
        if self.window_1d:
            self.window_1d.destroy()
        self.window_1d = tk.Toplevel(self)
        self.window_1d.title("1D: Анализ полупростых чисел")
        
        self.db.cursor.execute("SELECT value FROM semiprimes")
        self.data_1d = [row[0] for row in self.db.cursor.fetchall()]
        
        control_frame = ttk.Frame(self.window_1d)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Модель:").grid(row=0, column=0, padx=5)
        self.model_1d_var = tk.StringVar(value='HMM_N')
        model_combobox = ttk.Combobox(control_frame, textvariable=self.model_1d_var, 
                                    values=['HMM_N', 'HMM_B'], width=15)
        model_combobox.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Параметр:").grid(row=0, column=2, padx=5)
        self.param_1d_entry = ttk.Entry(control_frame, width=10)
        self.param_1d_entry.insert(0, "5" if self.model_1d_var.get() == 'HMM_N' else "100")
        self.param_1d_entry.grid(row=0, column=3, padx=5)
        
        ttk.Button(control_frame, text="Применить", command=self.update_1d_viz).grid(row=0, column=4, padx=5)
        
        self.tab_control_1d = ttk.Notebook(self.window_1d)
        
        self.spiral_frame = ttk.Frame(self.tab_control_1d)
        self.draw_ulam_spiral(self.spiral_frame, self.data_1d)
        self.tab_control_1d.add(self.spiral_frame, text="Спираль Улама")
        
        self.pie_frame = ttk.Frame(self.tab_control_1d)
        self.draw_pie_chart(self.pie_frame, self.data_1d)
        self.tab_control_1d.add(self.pie_frame, text="Распределение")
        
        self.tab_control_1d.pack(expand=1, fill="both", padx=10, pady=10)

    def draw_ulam_spiral(self, parent, data):
        """Улучшенная отрисовка спирали Улама"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame, width=600, height=500, bg='white')
        canvas.pack(pady=10)
        
        x, y = 0, 0
        dx, dy = 0, -1
        step = 10
        max_steps = 1
        steps = 0
        turns = 0
        center = 250

        for num in data:
            is_semiprime = DataHandler.is_semiprime(num)
            color = "#e74c3c" if is_semiprime else "#f0f0f0"
        
            if -center//step < x < center//step and -center//step < y < center//step:
                canvas.create_oval(
                    center + x*step - 3,
                    center + y*step - 3,
                    center + x*step + 3,
                    center + y*step + 3,
                    fill=color, 
                    outline=""
                )
            
            if steps >= max_steps:
                steps = 0
                dx, dy = -dy, dx
                turns += 1
                if turns % 2 == 0:
                    max_steps += 1
            
            x += dx
            y += dy
            steps += 1

        legend_frame = ttk.Frame(main_frame)
        legend_frame.pack(pady=5)
        ttk.Label(legend_frame, text="Легенда:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        color_frame = ttk.Frame(legend_frame)
        color_frame.pack(side=tk.LEFT)
        tk.Canvas(color_frame, width=20, height=20, bg='#e74c3c').pack(side=tk.LEFT, padx=2)
        ttk.Label(color_frame, text="Полупростые числа").pack(side=tk.LEFT)
        
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        text = """Спираль Улама - геометрическое представление чисел, где:
            • Числа располагаются по спирали от центра (0,0)
            • Красные точки обозначают полупростые числа (p*q)
            • Модель HMM_N: цвет зависит от остатка деления на модуль
            • Модель HMM_B: группировка чисел по диапазонам (base)
            • Параметры управления: модуль/база в панели управления
        """
        ttk.Label(desc_frame, text=text, wraplength=580, justify=tk.LEFT).pack()

    def draw_pie_chart(self, parent, data):
        """Улучшенная круговая диаграмма"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame, width=400, height=400, bg='white')
        canvas.pack(pady=10)
        
        mod = 5
        counts = [0]*mod
        for num in data:
            counts[num % mod] += 1
        
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f', '#9b59b6']
        start_angle = 0
        for i, count in enumerate(counts):
            angle = 360 * count / len(data)
            canvas.create_arc(50, 50, 350, 350, start=start_angle, extent=angle, fill=colors[i])
            start_angle += angle
        
        legend_frame = ttk.Frame(main_frame)
        legend_frame.pack(pady=5)
        ttk.Label(legend_frame, text="Распределение по модулю:", font=('Arial', 9, 'bold')).pack()
        for i, color in enumerate(colors[:mod]):
            frame = ttk.Frame(legend_frame)
            frame.pack(side=tk.LEFT, padx=5)
            tk.Canvas(frame, width=20, height=20, bg=color).pack()
            ttk.Label(frame, text=f"mod {i}").pack()
        
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        text = """Круговая диаграмма показывает:
            • Распределение чисел по остаткам от деления
            • Каждый сектор соответствует определенному остатку
            • Размер сектора пропорционален количеству чисел
            • Модель HMM_N: изменение модуля (N) меняет количество секторов
            • Модель HMM_B: группировка чисел по диапазонам (base)
        """
        ttk.Label(desc_frame, text=text, wraplength=580, justify=tk.LEFT).pack()

    # 2D Визуализации
    def open_2d(self):
        """Окно 2D визуализаций с улучшенным UI"""
        if self.window_2d:
            self.window_2d.destroy()
        self.window_2d = tk.Toplevel(self)
        self.window_2d.title("2D: Анализ Ker(X*Y - X+Y)")
        
        self.db.cursor.execute("SELECT x, y, value FROM ker_values")
        raw_data = self.db.cursor.fetchall()
        self.data_2d = [[0]*100 for _ in range(100)]
        for x, y, v in raw_data:
            self.data_2d[x][y] = v
        
        control_frame = ttk.Frame(self.window_2d)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Модель:").grid(row=0, column=0, padx=5)
        self.model_2d_var = tk.StringVar(value='HMM_DN')
        model_combobox = ttk.Combobox(control_frame, textvariable=self.model_2d_var, 
                                     values=['HMM_DN', 'HMM_R'], width=15)
        model_combobox.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Параметр 1:").grid(row=0, column=2, padx=5)
        self.param_a_entry = ttk.Entry(control_frame, width=10)
        self.param_a_entry.insert(0, "10")
        self.param_a_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(control_frame, text="Параметр 2:").grid(row=0, column=4, padx=5)
        self.param_b_entry = ttk.Entry(control_frame, width=10)
        self.param_b_entry.insert(0, "5")
        self.param_b_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(control_frame, text="Применить", command=self.update_2d_viz).grid(row=0, column=6, padx=5)
        
        self.tab_control_2d = ttk.Notebook(self.window_2d)
        
        self.heatmap_frame = ttk.Frame(self.tab_control_2d)
        self.draw_heatmap(self.heatmap_frame, self.data_2d)
        self.tab_control_2d.add(self.heatmap_frame, text="Тепловая карта")
        
        self.contour_frame = ttk.Frame(self.tab_control_2d)
        self.draw_contour(self.contour_frame, self.data_2d)
        self.tab_control_2d.add(self.contour_frame, text="Контуры")
        
        self.tab_control_2d.pack(expand=1, fill="both", padx=10, pady=10)

    def draw_heatmap(self, parent, data):
        """Улучшенная тепловая карта"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame, width=600, height=600, bg='white')
        canvas.pack(pady=10)
        
        color_map = {
            0: '#2ecc71', 1: '#3498db', 2: '#e74c3c',
            3: '#f1c40f', 4: '#9b59b6', 5: '#34495e',
            6: '#FF00FF', 7: '#00FFFF', 8: '#FFA500', 9: '#808080'
        }
        
        cell_size = 6
        for x in range(100):
            for y in range(100):
                value = data[x][y]  
                color = color_map.get(value, '#ffffff')
                canvas.create_rectangle(
                    x*cell_size, y*cell_size,
                    (x+1)*cell_size, (y+1)*cell_size,
                    fill=color, outline=""
                )
        
        legend_frame = ttk.Frame(main_frame)
        legend_frame.pack(pady=5)
        ttk.Label(legend_frame, text="Цветовая карта значений Ker:", 
                 font=('Arial', 9, 'bold')).pack()
        
        row1 = ttk.Frame(legend_frame)
        row1.pack()
        for value in range(5):
            frame = ttk.Frame(row1)
            frame.pack(side=tk.LEFT, padx=2)
            tk.Canvas(frame, width=20, height=20, bg=color_map[value]).pack()
            ttk.Label(frame, text=f"{value}").pack()
        
        row2 = ttk.Frame(legend_frame)
        row2.pack()
        for value in range(5, 10):
            frame = ttk.Frame(row2)
            frame.pack(side=tk.LEFT, padx=2)
            tk.Canvas(frame, width=20, height=20, bg=color_map[value]).pack()
            ttk.Label(frame, text=f"{value}").pack()
        
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        text = """Тепловая карта значений Ker(X*Y - X+Y):
            • Каждая ячейка соответствует паре (X,Y)
            • Цвет определяется значением Ker (0-9)
            • Ker(a) - рекурсивная сумма цифр до однозначного числа
            • HMM_DN: преобразование значений по модулю N
            • HMM_R: линейная комбинация (a*X + b*Y) mod 10
            • Изменяйте параметры для анализа паттернов
        """
        ttk.Label(desc_frame, text=text, wraplength=580, justify=tk.LEFT).pack()

    def draw_contour(self, parent, data):
        """Улучшенная контурная карта"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame, width=600, height=600, bg='white')
        canvas.pack(pady=10)
        
        levels = [0, 2, 4, 6, 8]
        cell_size = 6
        for x in range(100):
            for y in range(100):
                if data[x][y] in levels:
                    canvas.create_rectangle(
                        x*cell_size, y*cell_size,
                        (x+1)*cell_size, (y+1)*cell_size,
                        fill='#2c3e50', outline=""
                    )
        
        legend_frame = ttk.Frame(main_frame)
        legend_frame.pack(pady=5)
        ttk.Label(legend_frame, text="Контурные уровни:", 
                 font=('Arial', 9, 'bold')).pack()
        frame = ttk.Frame(legend_frame)
        frame.pack()
        tk.Canvas(frame, width=20, height=20, bg='#2c3e50').pack(side=tk.LEFT, padx=2)
        ttk.Label(frame, text="Значения: 0, 2, 4, 6, 8").pack(side=tk.LEFT)
        
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        text = """Контурная карта выделяет ключевые уровни:
            • Серым цветом отмечены ячейки со значениями 0,2,4,6,8
            • Позволяет выявить симметрии и закономерности
            • HMM_DN: изменение модуля влияет на уровни
            • HMM_R: коэффициенты a,b меняют распределение
            • Используйте совместно с тепловой картой для анализа
        """
        ttk.Label(desc_frame, text=text, wraplength=580, justify=tk.LEFT).pack()

    def update_1d_viz(self):
        """Обновление 1D визуализаций с проверкой"""
        try:
            model = self.model_1d_var.get()
            param = int(self.param_1d_entry.get())
            
            if model == 'HMM_N':
                if not 2 <= param <= 100:
                    raise ValueError("Модуль должен быть от 2 до 100")
                processed_data = HMM.hmm_n(self.data_1d, param)
            else:
                if param < 1:
                    raise ValueError("База должна быть больше 0")
                processed_data = HMM.hmm_b(self.data_1d, param)
            
            self.draw_ulam_spiral(self.spiral_frame, processed_data)
            self.draw_pie_chart(self.pie_frame, processed_data)
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректный параметр: {str(e)}")

    def update_2d_viz(self):
        """Обновление 2D визуализаций с проверкой"""
        try:
            model = self.model_2d_var.get()
            a = int(self.param_a_entry.get())
            b = int(self.param_b_entry.get()) if model == 'HMM_R' else 0
            
            if model == 'HMM_DN':
                if not 2 <= a <= 100:
                    raise ValueError("Модуль должен быть от 2 до 100")
                processed_data = HMM.hmm_dn(self.data_2d, a)
            else:
                if not (-100 <= a <= 100) or not (-100 <= b <= 100):
                    raise ValueError("Коэффициенты должны быть от -100 до 100")
                processed_data = HMM.hmm_r(self.data_2d, a, b)
            
            self.draw_heatmap(self.heatmap_frame, processed_data)
            self.draw_contour(self.contour_frame, processed_data)
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные параметры: {str(e)}")

    def show_about(self):
        """Информация о программе"""
        about_text = """Хромоматематическое моделирование

            Разработано для исследования числовых закономерностей

            Основные функции:
            - Анализ полупростых чисел (1D)
            - Исследование функции Ker (2D)

            Автор: Купреев С.С.
        """
        messagebox.showinfo("О программе", about_text)

    def show_help(self):
        """Расширенная справка"""
        help_text = """Руководство пользователя

            1. Генерация данных:
            - Нажмите 'Данные -> Сгенерировать данные'
            - Дождитесь завершения процесса (3-5 сек)

            2. Работа с 1D объектами:
            - Откройте 'Формы -> 1D: Полупростые числа'
            - Выберите модель:
                * HMM_N - модульная арифметика
                * HMM_B - биградиентная группировка
            - Введите параметр (модуль или базу)
            - Изучайте спираль Улама и диаграммы

            3. Работа с 2D объектами:
            - Откройте 'Формы -> 2D: Ker(XY-X+Y)'
            - Выберите модель:
                * HMM_DN - дискретное преобразование
                * HMM_R - мультиградиентная модель
            - Введите параметры (модуль или коэффициенты)
            - Анализируйте тепловые и контурные карты

            4. Интерпретация результатов:
            - Красный цвет на 1D - полупростые числа
            - Цветовая карта 2D соответствует значениям Ker
            - Контуры выделяют ключевые уровни

            5. Советы:
            - Начинайте с малых значений параметров
            - Сочетайте разные модели для анализа
            - Используйте легенды для интерпретации
        """
        messagebox.showinfo("Справка", help_text)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()