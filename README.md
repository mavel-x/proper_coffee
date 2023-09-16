# proper_coffee
Find good coffee nearby.

Send your location to the chat bot and receive the nearest places which serve
[third-wave coffee](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwj49tH2ga2BAxWrR_EDHZxGB_oQFnoECBEQAQ&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FThird-wave_coffee&usg=AOvVaw1dza8W2LTjiHghzvif1AvW&opi=89978449). 

Example Telegram bot: https://t.me/ProperCoffeeBot

## Project structure
This project consists of separate services 
designed to run in their own containers: 
- API
- Chat bots
- Under construction: admin panel

## Built with
- [FastAPI](https://fastapi.tiangolo.com/) 
- [SQLModel](https://sqlmodel.tiangolo.com/)
- Official [PostgreSQL Docker image](https://hub.docker.com/_/postgres/)
- [python-telegram-bot](https://python-telegram-bot.org/)
- Geocoding by [Geoapify](https://www.geoapify.com/)
- Test places from [European Coffee Trip](https://europeancoffeetrip.com/berlin/)

## How to Deploy
Since the app images can be pulled from DockerHub, 
all the files you need in the project dir are:
- `docker-compose.yml`
- `.env`
- optional: `places_dump.sql` to populate the database (not provided)

### Environment variables
#### Required:
- `GEO_API`: Geoapify key
- `TG_TOKEN`: Telegram bot token
- `POSTGRES_USER` 
- `POSTGRES_PASSWORD`

#### Optional:
- `POSTGRES_PORT` (default `5432`)
- `POSTGRES_DB` (default `places`)
- `DB_TYPE`: either `sqlite` or `prod`, defaults to `prod`


### Load data
If you have a `places_dump.sql` file, use it to populate the database before 
you launch the services:
```shell
docker compose up -d db
cat places_dump.sql | docker compose exec -T db psql -U postgres -d places
```

### Launch
```shell
docker compose up -d
```
