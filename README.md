# 🧠 Wikipedia Summary API

Проект на **FastAPI** для:

- 🔁 Рекурсивного парсинга статей из **Wikipedia** (до 5 уровней вложенности)
- 💾 Сохранения данных в **PostgreSQL**
- 🤖 Генерации **summary основной статьи** через AI (используется OpenRouter API)

---

## 🚀 Технологии

| Категория        | Используется                         |
|------------------|--------------------------------------|
| Backend          | FastAPI                              |
| Асинхронность    | Asyncio, asyncpg, SQLAlchemy         |
| БД               | PostgreSQL                           |
| Миграции         | Alembic                              |
| Контейнеризация  | Docker + Docker Compose              |
| Валидация        | Pydantic                             |
| AI               | OpenRouter API (GPT-подобная модель) |

---

## ⚙️ Установка и запуск

### 1. 📥 Клонируйте репозиторий
```bash
git clone https://github.com/Anach0ret/parserwiki.git
cd parserwiki
```
### 2. 🧪 Создайте .env файл
```bash
cp .env.example .env
```
Задайте ваш AI API ключ в переменной AI_API_KEY (получить можно на [OpenRouter.ai](https://openrouter.ai))
3. 🐳 Запуск с Docker Compose
```bash
docker-compose up --build
```
📌 Приложение будет доступно по адресу: http://localhost:8000

---
📖 Документация

    Swagger UI: http://localhost:8000/docs

    ReDoc: http://localhost:8000/redoc
