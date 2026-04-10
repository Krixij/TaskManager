## Установка проекта TaskManager

### 1. Клонируйте репозиторий:

git clone https://github.com/Krixij/TaskManager.git
#### cd TaskManager

### 2. Создайте виртуальное окружение:
(Если команда python не работает, попробуйте py или python3)
#### python -m venv .venv
#### .venv\Scripts\activate

### 3. Установите зависимости (библиотеки):
#### pip install -r requirements.txt

### 4. Запустите сервер:
#### python manage.py runserver

### 5. Проверка, что всё работает:
После запуска сервера откройте в браузере:
#### (Должна открыться страница с надписью "The install worked successfully! Congratulations!")
#### http://127.0.0.1:8000/

### Важно!
#### База данных уже есть в проекте (db.sqlite3) — миграции запускать не нужно
#### После git pull база данных обновляется автоматически
#### Виртуальное окружение должно быть активировано — в начале строки терминала должно быть (.venv)

### Обновление кода:
#### git pull


## Admin
#### Логин: root
#### Пароль:  root
