from enum import StrEnum, auto

import httpx
from loguru import logger
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app import bot_strings
from app.env_settings import Settings
from app.logging_utils import configure_logging
from app.places_client import PlacesClient
from app.schemas import Place


class Dependency(StrEnum):
    API_URL = auto()
    HTTP_CLIENT = auto()


BLANK_BUTTON = KeyboardButton(text=" ", request_location=True)
LOCATION_BUTTON = KeyboardButton(text=bot_strings.REQUEST_LOCATION_TEXT, request_location=True)
ELLIPSIS_BUTTON = KeyboardButton(text="...", request_location=True)

LOCATION_KEYBOARD = ReplyKeyboardMarkup(
    [[BLANK_BUTTON], [LOCATION_BUTTON], [ELLIPSIS_BUTTON]],
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        bot_strings.CREDITS_TEXT,
        disable_web_page_preview=True,
    )
    await update.message.reply_text(
        bot_strings.HELP_TEXT,
        reply_markup=LOCATION_KEYBOARD,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(bot_strings.HELP_TEXT)


async def nearest_places(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api_client = PlacesClient(
        api_url=context.bot_data[Dependency.API_URL],
        http_client=context.bot_data[Dependency.HTTP_CLIENT],
    )
    places: list[Place] = await api_client.get_nearest_places(**update.message.location.to_dict())

    for place in places:
        text = place.create_bot_message()
        if place.image_url:
            message = await update.message.reply_photo(photo=place.image_url, caption=text)
        else:
            message = await update.message.reply_text(text)
        await update.message.reply_location(
            latitude=place.location.latitude, longitude=place.location.longitude, reply_to_message_id=message.id
        )

    logger.info(f"Handled update {update.update_id} from {update.effective_user}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"{update} caused {repr(context.error)}")
    logger.exception(context.error)


async def post_shutdown(app: Application) -> None:
    await app.bot_data[Dependency.HTTP_CLIENT].aclose()
    logger.info("Closed HTTP client.")


def main() -> None:
    settings = Settings()
    configure_logging(settings.log_level)

    application = Application.builder().token(settings.tg_token).post_shutdown(post_shutdown).build()
    dependencies = {
        Dependency.API_URL: settings.api_url,
        Dependency.HTTP_CLIENT: httpx.AsyncClient(),
    }
    application.bot_data.update(dependencies)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.LOCATION, nearest_places))
    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
