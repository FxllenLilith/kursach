import tkinter as tk
from tkinter import ttk
import sqlite3
import re
import pandas as pd

# Database connection
def connect_db():
    conn = sqlite3.connect('dog_exhibition.db')
    return conn

# Create tables if they don't exist
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    create_tables_query = """
    CREATE TABLE IF NOT EXISTS Exhibitions (
        ExhibitionID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Date DATE NOT NULL,
        Location TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Dogs (
        DogID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Breed TEXT NOT NULL,
        Age INTEGER NOT NULL,
        OwnerID INTEGER,
        FOREIGN KEY (OwnerID) REFERENCES Owners(OwnerID)
    );

    CREATE TABLE IF NOT EXISTS Owners (
        OwnerID INTEGER PRIMARY KEY AUTOINCREMENT,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        Phone TEXT NOT NULL,
        Admin INTEGER NOT NULL,
        Password TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Participation (
        ParticipationID INTEGER PRIMARY KEY AUTOINCREMENT,
        DogID INTEGER NOT NULL,
        ExhibitionID INTEGER NOT NULL,
        Result TEXT,
        FOREIGN KEY (DogID) REFERENCES Dogs(DogID),
        FOREIGN KEY (ExhibitionID) REFERENCES Exhibitions(ExhibitionID),
        UNIQUE (DogID, ExhibitionID)  -- Добавляем уникальное ограничение
    );
    """
    cursor.executescript(create_tables_query)
    conn.commit()
    conn.close()

# Add user function
def add_user(name, lastname, phone, password, admin=0):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Owners WHERE Phone = ?", (phone,))
    existing_user = cursor.fetchone()
    if phone == "1":
        admin = 1
    if existing_user:
        show_error_window("Пользователь с таким номером уже существует.")
    else:
        cursor.execute("INSERT INTO Owners (FirstName, LastName, Phone, Password, Admin) VALUES (?, ?, ?, ?, ?)",
                       (name, lastname, phone, password, admin))
        conn.commit()
        print(f"Пользователь {name} {lastname} добавлен в систему.")
    conn.close()

# Make superuser function
def make_superuser(phone_number):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE Owners SET Admin = 1 WHERE Phone = ?", (phone_number,))
    conn.commit()
    conn.close()
    print(f"Пользователь с телефоном {phone_number} теперь суперпользователь.")

# Register dog function
def register_dog(name, breed, age, ownerid):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Dogs (Name, Breed, Age, OwnerID) VALUES (?, ?, ?, ?)",
                   (name, breed, age, ownerid))
    dogid = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Собака зарегистрирована успешно с ID: {dogid}")

# Fetch owners for combobox
def get_owners():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT OwnerID, FirstName, LastName FROM Owners")
    owners = cursor.fetchall()
    conn.close()
    return owners

# Login function
def login_user(phone, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Owners WHERE Phone = ? AND Password = ?", (phone, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        print(f"Вход выполнен успешно! Добро пожаловать, {user[1]} {user[2]}.")
        return user  # Возвращаем данные пользователя
    else:
        print("Неверный телефон или пароль.")
        return None

# Функция для закрытия окна
def go_back(window):
    window.destroy()

# Функция для проверки ввода только букв
def validate_letters(P):
    if P == "":  # Пустая строка разрешена
        return True
    if re.match("^[a-zA-Zа-яА-Я\s-]*$", P):  # Разрешены только буквы, пробелы и дефисы
        return True
    return False

# Функция для проверки ввода только цифр
def validate_numbers(P):
    if P == "":  # Пустая строка разрешена
        return True
    if re.match("^[0-9]*$", P):  # Разрешены только цифры
        return True
    return False

# Функция для проверки ввода номера телефона
def validate_phone(P):
    if P == "":  # Пустая строка разрешена
        return True
    if re.match(r"^\+?\d{0,1}\s?\(?\d{0,3}\)?\s?-?\d{0,3}-?\d{0,4}$", P):  # Разрешены +, (), - и цифры
        return True
    return False

# Функция для проверки формата даты
def validate_date(date):
    try:
        # Проверяем, что дата в формате YYYY-MM-DD
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            return True
        else:
            return False
    except:
        return False

# Функция для проверки формата возраста
def validate_age(age):
    try:
        age = int(age)
        if age > 0:
            return True
        else:
            return False
    except:
        return False

# Функция для отображения окна с сообщением об ошибке
def show_error_window(message):
    error_win = tk.Toplevel()
    error_win.title("Ошибка")

    error_label = ttk.Label(error_win, text=message)
    error_label.pack(padx=20, pady=20)

    ok_button = ttk.Button(error_win, text="OK", command=lambda: error_win.destroy())
    ok_button.pack(padx=10, pady=10)

# Окно для добавления пользователя
def add_user_window():
    add_user_win = tk.Toplevel()
    add_user_win.title("Регистрация")

    # Проверка ввода только букв для имени и фамилии
    vcmd_letters = (add_user_win.register(validate_letters), '%P')
    vcmd_numbers = (add_user_win.register(validate_numbers), '%P')
    vcmd_phone = (add_user_win.register(validate_phone), '%P')

    name_label = ttk.Label(add_user_win, text="Имя:")
    name_label.grid(row=0, column=0)
    name_entry = ttk.Entry(add_user_win, validate="key", validatecommand=vcmd_letters)
    name_entry.grid(row=0, column=1)

    lastname_label = ttk.Label(add_user_win, text="Фамилия:")
    lastname_label.grid(row=1, column=0)
    lastname_entry = ttk.Entry(add_user_win, validate="key", validatecommand=vcmd_letters)
    lastname_entry.grid(row=1, column=1)

    phone_label = ttk.Label(add_user_win, text="Телефон:")
    phone_label.grid(row=2, column=0)
    phone_entry = ttk.Entry(add_user_win, validate="key", validatecommand=vcmd_phone)
    phone_entry.grid(row=2, column=1)

    password_label = ttk.Label(add_user_win, text="Пароль:")
    password_label.grid(row=3, column=0)
    password_entry = ttk.Entry(add_user_win, show="*")
    password_entry.grid(row=3, column=1)

    def add_user_db():
        name = name_entry.get()
        lastname = lastname_entry.get()
        phone = phone_entry.get()
        password = password_entry.get()

        # Проверка на обязательные поля
        if not name or not lastname or not phone or not password:
            show_error_window("Пожалуйста, заполните все поля.")
            return

        # Проверка на существование пользователя с таким номером
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Owners WHERE Phone = ?", (phone,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            show_error_window("Пользователь с таким номером уже существует.")
        else:
            add_user(name, lastname, phone, password)
            add_user_win.destroy()

    add_button = ttk.Button(add_user_win, text="Регистрация", command=add_user_db)
    add_button.grid(row=4, column=0, columnspan=2)

    # Кнопка "Назад"
    back_button = ttk.Button(add_user_win, text="Назад", command=lambda: go_back(add_user_win))
    back_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Окно для добавления админа
def make_superuser_window():
    make_superuser_win = tk.Toplevel()
    make_superuser_win.title("Добавить админа")

    vcmd_phone = (make_superuser_win.register(validate_phone), '%P')

    phone_label = ttk.Label(make_superuser_win, text="Телефон:")
    phone_label.grid(row=0, column=0)
    phone_entry = ttk.Entry(make_superuser_win, validate="key", validatecommand=vcmd_phone)
    phone_entry.grid(row=0, column=1)

    def make_superuser_db():
        phone_number = phone_entry.get()
        if not phone_number:
            show_error_window("Пожалуйста, введите номер телефона.")
            return

        make_superuser(phone_number)
        make_superuser_win.destroy()

    make_superuser_button = ttk.Button(make_superuser_win, text="Добавить админа", command=make_superuser_db)
    make_superuser_button.grid(row=1, column=0, columnspan=2)

    # Кнопка "Назад"
    back_button = ttk.Button(make_superuser_win, text="Назад", command=lambda: go_back(make_superuser_win))
    back_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Окно для регистрации собаки
def register_dog_window(owner_id):  # Передаем OwnerID текущего пользователя
    register_dog_win = tk.Toplevel()
    register_dog_win.title("Регистрация собаки")

    vcmd_letters = (register_dog_win.register(validate_letters), '%P')
    vcmd_numbers = (register_dog_win.register(validate_numbers), '%P')

    dog_name_label = ttk.Label(register_dog_win, text="Кличка:")
    dog_name_label.grid(row=0, column=0)
    dog_name_entry = ttk.Entry(register_dog_win, validate="key", validatecommand=vcmd_letters)
    dog_name_entry.grid(row=0, column=1)

    breed_label = ttk.Label(register_dog_win, text="Порода:")
    breed_label.grid(row=1, column=0)
    breed_entry = ttk.Entry(register_dog_win, validate="key", validatecommand=vcmd_letters)
    breed_entry.grid(row=1, column=1)

    age_label = ttk.Label(register_dog_win, text="Возраст:")
    age_label.grid(row=2, column=0)
    age_entry = ttk.Entry(register_dog_win, validate="key", validatecommand=vcmd_numbers)
    age_entry.grid(row=2, column=1)

    def register_dog_db():
        dog_name = dog_name_entry.get()
        breed = breed_entry.get()
        age = age_entry.get()

        if not dog_name or not breed or not age:
            show_error_window("Пожалуйста, заполните все поля.")
            return

        if not validate_age(age):
            show_error_window("Неверный формат возраста. Используйте только цифры.")
            return

        register_dog(dog_name, breed, age, owner_id)
        register_dog_win.destroy()

    register_button = ttk.Button(register_dog_win, text="Регистрация собаки", command=register_dog_db)
    register_button.grid(row=3, column=0, columnspan=2)

    # Кнопка "Назад"
    back_button = ttk.Button(register_dog_win, text="Назад", command=lambda: go_back(register_dog_win))
    back_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Окно для регистрации на мероприятие
def register_event_window(owner_id):
    register_event_win = tk.Toplevel()
    register_event_win.title("Регистрация на мероприятие")

    # Получаем список мероприятий
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ExhibitionID, Name, Date, Location FROM Exhibitions")
    exhibitions = cursor.fetchall()
    conn.close()

    # Получаем список собак пользователя
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DogID, Name FROM Dogs WHERE OwnerID = ?", (owner_id,))
    dogs = cursor.fetchall()
    conn.close()

    # Выбор мероприятия
    exhibition_label = ttk.Label(register_event_win, text="Выберите мероприятие:")
    exhibition_label.grid(row=0, column=0, padx=10, pady=10)
    exhibition_combobox = ttk.Combobox(register_event_win, values=[f"{e[1]} ({e[2]})" for e in exhibitions])
    exhibition_combobox.grid(row=0, column=1, padx=10, pady=10)

    # Выбор собаки
    dog_label = ttk.Label(register_event_win, text="Выберите собаку:")
    dog_label.grid(row=1, column=0, padx=10, pady=10)
    dog_combobox = ttk.Combobox(register_event_win, values=[d[1] for d in dogs])
    dog_combobox.grid(row=1, column=1, padx=10, pady=10)

    def register_event_db():
        selected_exhibition = exhibition_combobox.get()
        selected_dog = dog_combobox.get()

        if not selected_exhibition or not selected_dog:
            show_error_window("Пожалуйста, выберите мероприятие и собаку.")
            return

        # Получаем ID мероприятия и собаки
        exhibition_id = exhibitions[exhibition_combobox.current()][0]
        dog_id = dogs[dog_combobox.current()][0]

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Participation (DogID, ExhibitionID) VALUES (?, ?)", (dog_id, exhibition_id))
            conn.commit()
            print(f"Регистрация на мероприятие {selected_exhibition} успешно выполнена.")
        except sqlite3.IntegrityError:
            show_error_window("Вы уже зарегистрированы на это мероприятие с этой собакой.")
        conn.close()

    register_button = ttk.Button(register_event_win, text="Зарегистрироваться", command=register_event_db)
    register_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    # Кнопка "Назад"
    back_button = ttk.Button(register_event_win, text="Назад", command=lambda: go_back(register_event_win))
    back_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Окно для просмотра информации об администрации
def view_admin_info_window():
    view_admin_win = tk.Toplevel()
    view_admin_win.title("Информация об администрации")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT FirstName, LastName, Phone FROM Owners WHERE Admin = 1")
    admins = cursor.fetchall()
    conn.close()

    admin_listbox = tk.Listbox(view_admin_win, width=50)
    admin_listbox.pack(padx=10, pady=10)

    for admin in admins:
        admin_listbox.insert(tk.END, f"{admin[0]} {admin[1]} (Телефон: {admin[2]})")

    # Кнопка "Назад"
    back_button = ttk.Button(view_admin_win, text="Назад", command=lambda: go_back(view_admin_win))
    back_button.pack(padx=10, pady=10)

# Окно для просмотра информации о зарегистрированных собаках
def view_dogs_info_window():
    view_dogs_win = tk.Toplevel()
    view_dogs_win.title("Информация о зарегистрированных собаках")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Breed, Age, OwnerID FROM Dogs")
    dogs = cursor.fetchall()
    conn.close()

    dogs_listbox = tk.Listbox(view_dogs_win, width=50)
    dogs_listbox.pack(padx=10, pady=10)

    for dog in dogs:
        dogs_listbox.insert(tk.END, f"Кличка: {dog[0]}, Порода: {dog[1]}, Возраст: {dog[2]}, Владелец ID: {dog[3]}")

    # Кнопка "Назад"
    back_button = ttk.Button(view_dogs_win, text="Назад", command=lambda: go_back(view_dogs_win))
    back_button.pack(padx=10, pady=10)

# Окно для создания мероприятия (только для администраторов)
def create_event_window():
    create_event_win = tk.Toplevel()
    create_event_win.title("Создание мероприятия")

    name_label = ttk.Label(create_event_win, text="Название мероприятия:")
    name_label.grid(row=0, column=0)
    name_entry = ttk.Entry(create_event_win)
    name_entry.grid(row=0, column=1)

    date_label = ttk.Label(create_event_win, text="Дата мероприятия (YYYY-MM-DD):")
    date_label.grid(row=1, column=0)
    date_entry = ttk.Entry(create_event_win)
    date_entry.grid(row=1, column=1)

    location_label = ttk.Label(create_event_win, text="Место проведения:")
    location_label.grid(row=2, column=0)
    location_entry = ttk.Entry(create_event_win)
    location_entry.grid(row=2, column=1)

    def create_event_db():
        name = name_entry.get()
        date = date_entry.get()
        location = location_entry.get()

        if not name or not date or not location:
            show_error_window("Пожалуйста, заполните все поля.")
            return

        if not validate_date(date):
            show_error_window("Неверный формат даты. Используйте формат YYYY-MM-DD.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Exhibitions (Name, Date, Location) VALUES (?, ?, ?)", (name, date, location))
        conn.commit()
        conn.close()
        print(f"Мероприятие '{name}' создано.")
        create_event_win.destroy()

    create_button = ttk.Button(create_event_win, text="Создать мероприятие", command=create_event_db)
    create_button.grid(row=3, column=0, columnspan=2)

    # Кнопка "Назад"
    back_button = ttk.Button(create_event_win, text="Назад", command=lambda: go_back(create_event_win))
    back_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Окно для просмотра всех пользователей (только для администраторов)
def view_users_window():
    view_users_win = tk.Toplevel()
    view_users_win.title("Список пользователей")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT FirstName, LastName, Phone, Admin FROM Owners")
    users = cursor.fetchall()
    conn.close()

    users_listbox = tk.Listbox(view_users_win, width=50)
    users_listbox.pack(padx=10, pady=10)

    for user in users:
        admin_status = "Администратор" if user[3] == 1 else "Пользователь"
        users_listbox.insert(tk.END, f"{user[0]} {user[1]} (Телефон: {user[2]}) - {admin_status}")

    # Кнопка "Назад"
    back_button = ttk.Button(view_users_win, text="Назад", command=lambda: go_back(view_users_win))
    back_button.pack(padx=10, pady=10)

# Окно для изменения результатов выставок
def edit_results_window():
    edit_results_win = tk.Toplevel()
    edit_results_win.title("Изменить результаты выставок")

    # Ввод ID собаки
    dog_id_label = ttk.Label(edit_results_win, text="ID собаки:")
    dog_id_label.grid(row=0, column=0, padx=10, pady=10)
    dog_id_entry = ttk.Entry(edit_results_win)
    dog_id_entry.grid(row=0, column=1, padx=10, pady=10)

    # Ввод ID выставки
    exhibition_id_label = ttk.Label(edit_results_win, text="ID выставки:")
    exhibition_id_label.grid(row=1, column=0, padx=10, pady=10)
    exhibition_id_entry = ttk.Entry(edit_results_win)
    exhibition_id_entry.grid(row=1, column=1, padx=10, pady=10)

    # Выбор результата
    result_label = ttk.Label(edit_results_win, text="Результат:")
    result_label.grid(row=2, column=0, padx=10, pady=10)
    result_combobox = ttk.Combobox(edit_results_win, values=[
        "Best in Show", "Reserve Best in Show", "Best Puppy", "Best Junior", "Best Veteran", "Champion", "Grand Champion"
    ])
    result_combobox.grid(row=2, column=1, padx=10, pady=10)

    def update_result_db():
        dog_id = dog_id_entry.get()
        exhibition_id = exhibition_id_entry.get()
        result = result_combobox.get()

        if not dog_id or not exhibition_id or not result:
            show_error_window("Пожалуйста, заполните все поля.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Dogs WHERE DogID = ?", (dog_id,))
        dog = cursor.fetchone()
        cursor.execute("SELECT * FROM Exhibitions WHERE ExhibitionID = ?", (exhibition_id,))
        exhibition = cursor.fetchone()
        conn.close()

        if not dog or not exhibition:
            show_error_window("Неверный ID собаки или выставки.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Participation (DogID, ExhibitionID, Result)
            VALUES (?, ?, ?)
            ON CONFLICT(DogID, ExhibitionID) DO UPDATE SET Result = ?
        """, (dog_id, exhibition_id, result, result))
        conn.commit()
        conn.close()
        print(f"Результат обновлен для собаки с ID {dog_id} на выставке с ID {exhibition_id}.")
        edit_results_win.destroy()

    update_button = ttk.Button(edit_results_win, text="Обновить результат", command=update_result_db)
    update_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    # Кнопка "Назад"
    back_button = ttk.Button(edit_results_win, text="Назад", command=lambda: go_back(edit_results_win))
    back_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Окно для просмотра результатов выставок
def view_participation_window():
    view_participation_win = tk.Toplevel()
    view_participation_win.title("Просмотр результатов выставок")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Dogs.Name, Exhibitions.Name, Participation.Result
        FROM Participation
        JOIN Dogs ON Participation.DogID = Dogs.DogID
        JOIN Exhibitions ON Participation.ExhibitionID = Exhibitions.ExhibitionID
    """)
    results = cursor.fetchall()
    conn.close()

    results_listbox = tk.Listbox(view_participation_win, width=50)
    results_listbox.pack(padx=10, pady=10)

    for result in results:
        results_listbox.insert(tk.END, f"Собака: {result[0]}, Выставка: {result[1]}, Результат: {result[2]}")

    # Кнопка "Назад"
    back_button = ttk.Button(view_participation_win, text="Назад", command=lambda: go_back(view_participation_win))
    back_button.pack(padx=10, pady=10)

# Окно для просмотра мероприятий, на которые зарегистрирован пользователь
def view_registered_events_window(owner_id):
    view_events_win = tk.Toplevel()
    view_events_win.title("Зарегистрированные мероприятия")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Exhibitions.Name, Exhibitions.Date, Exhibitions.Location, Dogs.Name AS DogName
        FROM Participation
        JOIN Exhibitions ON Participation.ExhibitionID = Exhibitions.ExhibitionID
        JOIN Dogs ON Participation.DogID = Dogs.DogID
        WHERE Dogs.OwnerID = ?
    """, (owner_id,))
    events = cursor.fetchall()
    conn.close()

    events_listbox = tk.Listbox(view_events_win, width=80)
    events_listbox.pack(padx=10, pady=10)

    for event in events:
        events_listbox.insert(tk.END, f"Мероприятие: {event[0]}, Дата: {event[1]}, Место: {event[2]}, Собака: {event[3]}")

    # Кнопка "Назад"
    back_button = ttk.Button(view_events_win, text="Назад", command=lambda: go_back(view_events_win))
    back_button.pack(padx=10, pady=10)

# Главное окно
def main_window():
    main_win = tk.Tk()
    main_win.title("Выставка собак")

    # Регистрация пользователя
    add_user_button = ttk.Button(main_win, text="Регистрация", command=add_user_window)
    add_user_button.grid(row=0, column=0, padx=10, pady=10)

    # Вход в систему
    login_frame = ttk.LabelFrame(main_win, text="Вход")
    login_frame.grid(row=1, column=0, padx=10, pady=10)

    phone_label = ttk.Label(login_frame, text="Телефон:")
    phone_label.grid(row=0, column=0)
    phone_entry = ttk.Entry(login_frame)
    phone_entry.grid(row=0, column=1)

    password_label = ttk.Label(login_frame, text="Пароль:")
    password_label.grid(row=1, column=0)
    password_entry = ttk.Entry(login_frame, show="*")
    password_entry.grid(row=1, column=1)

    def login_user_db():
        phone = phone_entry.get()
        password = password_entry.get()
        user = login_user(phone, password)
        if user:
            main_win.destroy()  # Закрываем главное окно после успешного входа
            if user[4] == 1:  # Если пользователь - администратор
                admin_window(user)
            else:
                user_window(user)
        else:
            show_error_window("Неверный телефон или пароль. Попробуйте снова.")

    login_button = ttk.Button(login_frame, text="Вход", command=login_user_db)
    login_button.grid(row=2, column=0, columnspan=2)

    main_win.mainloop()

# Окно пользователя (для обычных пользователей)
def user_window(user):
    user_win = tk.Tk()  # Используем tk.Tk() для создания нового главного окна
    user_win.title("Интерфейс пользователя")

    # Кнопка для регистрации собаки
    register_dog_button = ttk.Button(user_win, text="Регистрация собаки", command=lambda: register_dog_window(user[0]))  # Передаем OwnerID
    register_dog_button.grid(row=0, column=0, padx=10, pady=10)

    # Кнопка для регистрации на мероприятие
    register_event_button = ttk.Button(user_win, text="Регистрация на мероприятие", command=lambda: register_event_window(user[0]))
    register_event_button.grid(row=1, column=0, padx=10, pady=10)

    # Кнопка для просмотра информации об администрации
    view_admin_button = ttk.Button(user_win, text="Информация об администрации", command=view_admin_info_window)
    view_admin_button.grid(row=2, column=0, padx=10, pady=10)

    # Кнопка для просмотра информации о зарегистрированных собаках
    view_dogs_button = ttk.Button(user_win, text="Информация о собаках", command=view_dogs_info_window)
    view_dogs_button.grid(row=3, column=0, padx=10, pady=10)

    # Кнопка для просмотра мероприятий, на которые зарегистрирован пользователь
    view_events_button = ttk.Button(user_win, text="Просмотр зарегистрированных мероприятий", command=lambda: view_registered_events_window(user[0]))
    view_events_button.grid(row=4, column=0, padx=10, pady=10)

    # Кнопка "Назад"
    back_button = ttk.Button(user_win, text="Назад", command=lambda: go_back(user_win))
    back_button.grid(row=5, column=0, padx=10, pady=10)

    user_win.mainloop()

# Окно администратора (для пользователей с admin=1)
def admin_window(user):
    admin_win = tk.Tk()  # Используем tk.Tk() для создания нового главного окна
    admin_win.title("Интерфейс администратора")

    # Кнопка для создания мероприятия
    create_event_button = ttk.Button(admin_win, text="Создать мероприятие", command=create_event_window)
    create_event_button.grid(row=0, column=0, padx=10, pady=10)

    # Кнопка для просмотра всех пользователей
    view_users_button = ttk.Button(admin_win, text="Просмотр пользователей", command=view_users_window)
    view_users_button.grid(row=1, column=0, padx=10, pady=10)

    # Кнопка для изменения результатов выставок
    edit_results_button = ttk.Button(admin_win, text="Изменить результаты выставок", command=edit_results_window)
    edit_results_button.grid(row=2, column=0, padx=10, pady=10)

    # Кнопка для просмотра результатов выставок
    view_participation_button = ttk.Button(admin_win, text="Просмотр результатов выставок", command=view_participation_window)
    view_participation_button.grid(row=3, column=0, padx=10, pady=10)

    # Кнопка для добавления администратора
    add_admin_button = ttk.Button(admin_win, text="Добавить администратора", command=make_superuser_window)
    add_admin_button.grid(row=4, column=0, padx=10, pady=10)

    # Кнопка для регистрации собаки (администратор тоже может регистрировать собак)
    register_dog_button = ttk.Button(admin_win, text="Регистрация собаки", command=lambda: register_dog_window(user[0]))  # Передаем OwnerID
    register_dog_button.grid(row=5, column=0, padx=10, pady=10)

    # Кнопка для изменения данных о собаке
    edit_dog_button = ttk.Button(admin_win, text="Изменить данные о собаке", command=edit_dog_window)
    edit_dog_button.grid(row=6, column=0, padx=10, pady=10)

    # Кнопка для экспорта данных в Excel
    export_excel_button = ttk.Button(admin_win, text="Экспорт в Excel", command=export_to_excel)
    export_excel_button.grid(row=7, column=0, padx=10, pady=10)

    # Кнопка "Назад"
    back_button = ttk.Button(admin_win, text="Назад", command=lambda: go_back(admin_win))
    back_button.grid(row=8, column=0, padx=10, pady=10)

    admin_win.mainloop()

# Функция для изменения данных о собаке
def edit_dog_window():
    edit_dog_win = tk.Toplevel()
    edit_dog_win.title("Изменить данные о собаке")

    # Получаем список всех собак
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DogID, Name, Breed, Age, OwnerID FROM Dogs")
    dogs = cursor.fetchall()
    conn.close()

    # Создаем список собак для выбора
    dog_listbox = tk.Listbox(edit_dog_win, width=50)
    dog_listbox.pack(padx=10, pady=10)

    for dog in dogs:
        dog_listbox.insert(tk.END, f"ID: {dog[0]}, Кличка: {dog[1]}, Порода: {dog[2]}, Возраст: {dog[3]}, Владелец ID: {dog[4]}")

    # Поле для ввода новой клички
    new_name_label = ttk.Label(edit_dog_win, text="Новая кличка:")
    new_name_label.pack()
    new_name_entry = ttk.Entry(edit_dog_win)
    new_name_entry.pack()

    # Поле для ввода новой породы
    new_breed_label = ttk.Label(edit_dog_win, text="Новая порода:")
    new_breed_label.pack()
    new_breed_entry = ttk.Entry(edit_dog_win)
    new_breed_entry.pack()

    # Поле для ввода нового возраста
    new_age_label = ttk.Label(edit_dog_win, text="Новый возраст:")
    new_age_label.pack()
    new_age_entry = ttk.Entry(edit_dog_win)
    new_age_entry.pack()

    # Поле для ввода нового владельца
    new_owner_label = ttk.Label(edit_dog_win, text="Новый владелец ID:")
    new_owner_label.pack()
    new_owner_entry = ttk.Entry(edit_dog_win)
    new_owner_entry.pack()

    def update_dog_data():
        selected_dog = dog_listbox.curselection()
        if not selected_dog:
            show_error_window("Пожалуйста, выберите собаку.")
            return

        dog_id = dogs[selected_dog[0]][0]  # Получаем ID выбранной собаки
        new_name = new_name_entry.get()
        new_breed = new_breed_entry.get()
        new_age = new_age_entry.get()
        new_owner = new_owner_entry.get()

        if not new_name or not new_breed or not new_age or not new_owner:
            show_error_window("Пожалуйста, заполните все поля.")
            return

        if not validate_age(new_age):
            show_error_window("Неверный формат возраста. Используйте только цифры.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Dogs
            SET Name = ?, Breed = ?, Age = ?, OwnerID = ?
            WHERE DogID = ?
        """, (new_name, new_breed, new_age, new_owner, dog_id))
        conn.commit()
        conn.close()
        print(f"Данные о собаке с ID {dog_id} обновлены.")
        edit_dog_win.destroy()

    # Кнопка для обновления данных
    update_button = ttk.Button(edit_dog_win, text="Обновить данные", command=update_dog_data)
    update_button.pack(padx=10, pady=10)

    # Кнопка "Назад"
    back_button = ttk.Button(edit_dog_win, text="Назад", command=lambda: go_back(edit_dog_win))
    back_button.pack(padx=10, pady=10)

# Функция для экспорта данных в Excel
def export_to_excel():
    conn = connect_db()
    query = "SELECT * FROM Exhibitions"
    exhibitions_df = pd.read_sql_query(query, conn)

    query = "SELECT * FROM Dogs"
    dogs_df = pd.read_sql_query(query, conn)

    query = "SELECT * FROM Owners"
    owners_df = pd.read_sql_query(query, conn)

    query = "SELECT * FROM Participation"
    participation_df = pd.read_sql_query(query, conn)

    conn.close()

    with pd.ExcelWriter("dog_exhibition_data.xlsx", engine="xlsxwriter") as writer:
        exhibitions_df.to_excel(writer, sheet_name="Exhibitions", index=False)
        dogs_df.to_excel(writer, sheet_name="Dogs", index=False)
        owners_df.to_excel(writer, sheet_name="Owners", index=False)
        participation_df.to_excel(writer, sheet_name="Participation", index=False)

    show_error_window("Данные успешно экспортированы в файл dog_exhibition_data.xlsx")

# Создание таблиц и запуск главного окна
create_tables()
main_window()