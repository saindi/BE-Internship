# Internship
Це навчальний проєкт. Він виконаний із використанням Fastapi + PostgreSQL + Redis + AWS + Unittest + Docker.
<h2>
  Запуск програми 
</h2>

1. Завантажте кодову базу на локальну машину.
```
git clone https://github.com/saindi/internship.git
```
2. Встановіть залежності за допомогою pip або poetry:
   - pip:
   ```
   pip install -r requirements.txt
   ```
   - poetry:
   ```
   poetry install
   ```
3. Налаштуйте змінні оточення з файлу `.env.sample`
4. Запустіть файл `app.main`. Вихідні дані повинні мати такий вигляд:
```
INFO:     Will watch for changes in these directories: ['D:\\Internship\\app']
INFO:     Uvicorn running on http://127.0.0.1:5000 (Press CTRL+C to quit)
INFO:     Started reloader process [5144] using StatReload
INFO:     Started server process [8832]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
 ```

<h2>
  Запуск тестів 
</h2>

Для виконання текстів відкрийте консоль і введіть команду:

```
python -m pytest
```

<h2>
  Docker 
</h2>

<h3>
  Запуск програми в Docker 
</h3>

1. Для запуску програми в Docker створіть Docker Image:

```
docker build . -t fastapi_app
```

2. Запустіть контейнер:

```
docker run -p 5000:5000 --name fastapi fastapi_app
```

<h3>
  Запуск тестів у Docker
</h3>

1. Для запуску текстів спочатку дізнайтеся `CONTAINER_ID`:

```
docker ps
```

2. Виконайте команду для запусків тестів:

```
docker exec [CONTAINER_ID] python -m pytest
```

<h2>
  Міграції
</h2>

Для запуску міграцій виконайте цю команду, вказавши потрібну `revision` бази даних:

```
alembic upgrade [revision]
```

або виконайте найостаннішу ревізію:

```
alembic upgrade head
```