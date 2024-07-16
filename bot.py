import asyncio, django, logging, os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommandScopeAllPrivateChats

from environs import Env


from tgbot.handlers.start_bot import router
from tgbot.handlers.director.director import director_router
from tgbot.utils.menu_commands import set_commands

logger = logging.getLogger(__name__)


def setup_django():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "core.settings"
    )
    os.environ.update({'DJANGO_ALLOW_ASYNC_UNSAFE': "true"})
    django.setup()


async def main():
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    # setup_django()

    bot = Bot(token=env.str('TOKEN_BOT'), parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)
    dp.include_router(director_router)

    # start
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await set_commands(bot)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        session = await bot.get_session()
        await session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
