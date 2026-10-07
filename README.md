# SkinsReviewBot
#### Курсовий проєкт на тему: *«Система управління внутрішніми товарами у грі CS2»*

Telegram-бот для перегляду та оцінки скінів CS2, розроблений на базі **aiogram 3** та **Google Firebase Firestore** *(**PostgreSQL**)*.

## 🚀 Встановлення та налаштування

### 1. Клонування репозиторію
```bash
git clone https://github.com/Dimon4ik-525/SkinsReviewBot.git
cd SkinsReviewBot
```

### 2. Створення та активація віртуального середовища
- **Створення:**
  ```bash
  python -m venv venv
  ```
- **Активація (Windows):**
  ```powershell
  venv\Scripts\activate
  ```
- **Активація (Linux / macOS):**
  ```bash
  source venv/bin/activate
  ```

### 3. Встановлення залежностей
```bash
pip install -r requirements.txt
```

### 4. Налаштування оточення
1. Створіть файл `.env` у корені проєкту та вкажіть конфігурацію:
   ```env
   BOT_TOKEN=ваш_токен_бота_від_BotFather
   FIREBASE_KEY_PATH=firebase_key.json
   ADMIN_ID=ваш_telegram_id
   ```
2. Помістіть JSON-файл ключа сервісного акаунта Firebase у корінь проєкту (за замовчуванням `firebase_key.json`).

---

## ▶️ Запуск проєкту

- **Запуск бота:**
  ```bash
  python main.py
  ```
- **Зупинка бота:** натисніть у терміналі `Ctrl + C`
- **Деактивація віртуального середовища:**
  ```bash
  deactivate
  ```
