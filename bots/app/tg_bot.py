import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import bot_strings
from models import Place
from places_client import PlacesClient
from settings import Settings


settings = Settings()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger('tg_bot')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(bot_strings.START_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(bot_strings.HELP_TEXT)


async def nearest_places(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    client: PlacesClient = context.bot_data['places_client']
    places: list[Place] = client.get_nearest_places(**update.message.location.to_dict())
    for place in places:
        text = place.create_bot_message()
        if place.photo_url:
            message = await update.message.reply_photo(photo=place.photo_url, caption=text)
        else:
            message = await update.message.reply_text(text)
        await update.message.reply_location(latitude=place.location.latitude, longitude=place.location.longitude,
                                            reply_to_message_id=message.id)


def main() -> None:
    application = Application.builder().token(settings.tg_token).build()
    application.bot_data['places_client'] = PlacesClient(settings.api_url)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.LOCATION, nearest_places))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
