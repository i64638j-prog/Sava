import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class ExpenseTracker:
    def __init__(self, window):
        self.window = window
        self.window.title("Expense Tracker - Трекер расходов")
        self.window.geometry("900x700")
        
        self.expenses = []
        self.current_file = None
        
        self.setup_ui()
        self.create_table()
        
    def setup_ui(self):
        # Frame для ввода данных
        input_frame = ttk.LabelFrame(self.window, text="Добавление расхода", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Сумма
        ttk.Label(input_frame, text="Сумма (₽):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, width=15)
        self.category_combo['values'] = ('Еда', 'Транспорт', 'Развлечения', 'Коммунальные услуги', 
                                          'Здоровье', 'Одежда', 'Образование', 'Другое')
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set('Выберите категорию')
        
        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить расход", command=self.add_expense).grid(row=0, column=6, padx=10, pady=5)
        
        # Frame для фильтров и подсчёта
        control_frame = ttk.LabelFrame(self.window, text="Фильтрация и статистика", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по категории
        ttk.Label(control_frame, text="Фильтр по категории:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category = ttk.Combobox(control_frame, width=15)
        self.filter_category['values'] = ('Все', 'Еда', 'Транспорт', 'Развлечения', 
                                           'Коммунальные услуги', 'Здоровье', 'Одежда', 
                                           'Образование', 'Другое')
        self.filter_category.set('Все')
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)
        
        # Фильтр по дате (период)
        ttk.Label(control_frame, text="Дата с (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_from = ttk.Entry(control_frame, width=12)
        self.filter_date_from.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(control_frame, text="по (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.filter_date_to = ttk.Entry(control_frame, width=12)
        self.filter_date_to.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопки фильтрации
        ttk.Button(control_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(control_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=7, padx=5, pady=5)
        
        # Отображение суммы
        self.total_label = ttk.Label(control_frame, text="Сумма за период: 0.00 ₽", font=('Arial', 10, 'bold'))
        self.total_label.grid(row=1, column=0, columnspan=8, pady=10)
        
        # Frame для кнопок файловых операций
        file_frame = ttk.Frame(self.window, padding=5)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(file_frame, text="Сохранить в JSON", command=self.save_to_json).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Загрузить из JSON", command=self.load_from_json).pack(side="left", padx=5)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(self.window, text="Информация", padding=5)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.info_label = ttk.Label(info_frame, text="Всего записей: 0 | Общая сумма: 0.00 ₽", font=('Arial', 9))
        self.info_label.pack()
        
    def create_table(self):
        # Таблица для отображения расходов
        table_frame = ttk.Frame(self.window)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("#", "Дата", "Категория", "Сумма (₽)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("#", text="#")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма (₽)", text="Сумма (₽)")
        
        self.tree.column("#", width=50, anchor="center")
        self.tree.column("Дата", width=120, anchor="center")
        self.tree.column("Категория", width=150, anchor="center")
        self.tree.column("Сумма (₽)", width=120, anchor="e")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_amount(self, amount_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                return False, None
            return True, amount
        except ValueError:
            return False, None
    
    def add_expense(self):
        amount_str = self.amount_entry.get().strip()
        category = self.category_var.get().strip()
        date = self.date_entry.get().strip()
        
        # Валидация
        valid_amount, amount = self.validate_amount(amount_str)
        if not valid_amount:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
            return
        
        if not category or category == 'Выберите категорию':
            messagebox.showerror("Ошибка", "Выберите категорию")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        expense = {
            "amount": amount,
            "category": category,
            "date": date
        }
        
        self.expenses.append(expense)
        self.refresh_table()
        self.update_info()
        
        # Очистка полей
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set('Выберите категорию')
        
        messagebox.showinfo("Успех", "Расход добавлен")
    
    def refresh_table(self, filtered_expenses=None):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        expenses_to_show = filtered_expenses if filtered_expenses is not None else self.expenses
        
        # Сортировка по дате
        expenses_to_show = sorted(expenses_to_show, key=lambda x: x['date'])
        
        for i, expense in enumerate(expenses_to_show, 1):
            self.tree.insert("", "end", values=(
                i,
                expense["date"],
                expense["category"],
                f"{expense['amount']:.2f}"
            ))
    
    def calculate_total(self, expenses_list):
        return sum(expense["amount"] for expense in expenses_list)
    
    def update_info(self):
        total = self.calculate_total(self.expenses)
        self.info_label.config(text=f"Всего записей: {len(self.expenses)} | Общая сумма: {total:.2f} ₽")
    
    def apply_filter(self):
        filter_category = self.filter_category.get()
        filter_date_from = self.filter_date_from.get().strip()
        filter_date_to = self.filter_date_to.get().strip()
        
        filtered = self.expenses.copy()
        
        # Фильтр по категории
        if filter_category and filter_category != 'Все':
            filtered = [e for e in filtered if e["category"] == filter_category]
        
        # Фильтр по периоду дат
        if filter_date_from:
            if not self.validate_date(filter_date_from):
                messagebox.showerror("Ошибка", "Неверный формат начальной даты")
                return
            filtered = [e for e in filtered if e["date"] >= filter_date_from]
        
        if filter_date_to:
            if not self.validate_date(filter_date_to):
                messagebox.showerror("Ошибка", "Неверный формат конечной даты")
                return
            filtered = [e for e in filtered if e["date"] <= filter_date_to]
        
        # Обновление таблицы
        self.refresh_table(filtered)
        
        # Подсчёт суммы за период
        period_total = self.calculate_total(filtered)
        self.total_label.config(text=f"Сумма за период: {period_total:.2f} ₽")
        
        if filtered:
            messagebox.showinfo("Фильтр", f"Найдено {len(filtered)} записей на сумму {period_total:.2f} ₽")
        else:
            messagebox.showinfo("Фильтр", "Записей не найдено")
    
    def reset_filter(self):
        self.filter_category.set('Все')
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()
        self.total_label.config(text="Сумма за период: 0.00 ₽")
    
    def save_to_json(self):
        if not self.expenses:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить расходы"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.expenses, f, ensure_ascii=False, indent=4)
                self.current_file = file_path
                messagebox.showinfo("Успех", f"Данные сохранены в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def load_from_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Загрузить расходы"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_expenses = json.load(f)
                
                # Валидация загруженных данных
                for expense in loaded_expenses:
                    if not all(k in expense for k in ("amount", "category", "date")):
                        raise ValueError("Неверный формат данных в файле")
                    if expense["amount"] <= 0:
                        raise ValueError("Сумма должна быть положительной")
                
                self.expenses = loaded_expenses
                self.current_file = file_path
                self.refresh_table()
                self.update_info()
                self.reset_filter()
                messagebox.showinfo("Успех", f"Загружено {len(self.expenses)} записей из {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")


if __name__ == "__main__":
    # Проверка наличия tkinter
    try:
        window = tk.Tk()
        app = ExpenseTracker(window)
        window.mainloop()
    except ImportError:
        print("Ошибка: Tkinter не установлен.")
        print("На Linux установите: sudo apt-get install python3-tk")
        input("Нажмите Enter для выхода...")
