import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import (BotCommandScopeAllPrivateChats,
                                             BotCommandScopeDefault)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config_loader import Config, load_config
from db.base import Base
from handlers.start import start_handlers
from middlewares.private_chat import CheckChatType
from middlewares.throttling import ThrottlingMiddleware
from updatesworker import get_handled_updates_list
from utils.subs_day_count import select_all_subs


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Команда Start"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    config: Config = load_config()

    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.db_name}",
        future=True
    )
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    storage = MemoryStorage()
    bot = Bot(config.bot.token, parse_mode="HTML")
    bot["db"] = async_sessionmaker
    bot["pay"] = config.pay_provider.pay_provider

    dp = Dispatcher(bot, storage=storage)
    sheduler = AsyncIOScheduler()
    sheduler.add_job(select_all_subs, "cron", second="01",
                     minute="55", hour="23", args=(dp,))
    sheduler.start()

    # dp.middleware.setup(CheckChatType())
    # dp.middleware.setup(ThrottlingMiddleware())

    start_handlers(dp)

    await set_bot_commands(bot)

    try:
        await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logging.error("Bot stopped!")
