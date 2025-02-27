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


## Built with
- [FastAPI](https://fastapi.tiangolo.com/) 
- [python-telegram-bot](https://python-telegram-bot.org/)
- Geocoding by [Geoapify](https://www.geoapify.com/)
- Test places from [European Coffee Trip](https://europeancoffeetrip.com/berlin/)
- [Supabase](https://supabase.com/) with PostGIS

## How to Deploy
Since the app images can be pulled from DockerHub, 
all the files you need in the project dir are:
- `docker-compose.yml`
- `.env`


### Environment variables
#### Required:
- `GEOAPIFY_API_KEY`
- `TG_TOKEN`: Telegram bot token
- `DB_URL`


### Launch
```shell
docker compose up -d
```
