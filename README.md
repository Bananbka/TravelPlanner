### How to run:

```bash
docker compose up --build -d
```

## Local Run

### Example of .env for local testing:
```env
DB_NAME=travel_planer
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5432
DB_HOST=localhost
```

Run

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

## Docker run

### Example of .env.docker for container testing:

```env
DB_NAME=travel_planer
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```