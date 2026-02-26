### How to run:

```docker compose up --build -d```

## Example of .env for local testing:
DB_NAME=travel_planer
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5432
DB_HOST=localhost

## Example of .env.docker for container testing:
DB_NAME=travel_planer
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432