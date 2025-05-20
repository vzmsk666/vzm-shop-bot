# VZM SHOP Bot

## 🚀 Как запустить

1. Создай бота через @BotFather, получи TOKEN
2. В файле `config.py` вставь свой `BOT_TOKEN`
3. В `OPERATOR_ID` укажи свой Telegram user ID (например, через @userinfobot)
4. Установи зависимости:

```bash
pip install aiogram==3.2.0
```

5. Запусти бота:

```bash
python main.py
```

## 🌐 Хостинг (Render)

1. Зарегистрируйся на https://render.com
2. Создай новый Web Service → Python → укажи GitHub с проектом
3. В `Start command` введи:

```bash
python main.py
```

4. Добавь переменные окружения:
   - `BOT_TOKEN`
   - `OPERATOR_ID`

Готово!