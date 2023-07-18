# Internship

This is a training project. It was made using _Fastapi_ + _PostgreSQL_ + _Redis_ + _AWS_ + _Unittest_ + _Docker_.

<h2>
  Starting the program
</h2>

1. Download the code base to your local machine:

```
git clone https://github.com/saindi/internship.git
```

2. Set dependencies using pip or poetry:
   
   - pip:
   
   ```
   pip install -r requirements.txt
   ```
   
   - poetry:
   
   ```
   poetry install
   ```
   
3. Configure environment variables from a file `.env.sample`

4. Run the file `app.main`. The output should look like this:

```
INFO:     Will watch for changes in these directories: ['D:\\Internship\\app']
INFO:     Uvicorn running on http://127.0.0.1:5000 (Press CTRL+C to quit)
INFO:     Started reloader process [5144] using StatReload
INFO:     Started server process [8832]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
 ```

<h2>
  Run tests
</h2>

To execute texts, open the console and enter the command:

```
python -m pytest
```

<h2>
  Docker 
</h2>

<h3>
  Running programs in Docker
</h3>

1. To run the program in Docker, create Docker Image:

```
docker build . -t fastapi_app
```

2. Start the container:

```
docker run -p 5000:5000 --name fastapi fastapi_app
```

<h3>
  Running tests in Docker
</h3>

1. To run texts, first find out `CONTAINER_ID`:

```
docker ps
```

2. Run the command to run the tests:

```
docker exec [CONTAINER_ID] python -m pytest
```

<h2>
  Migration
</h2>

To start migrations, run this command, specifying the desired `revision` of the database:

```
alembic upgrade [revision]
```

or perform the most recent audit:

```
alembic upgrade head
```