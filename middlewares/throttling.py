import asyncio
from typing import Union

from aiogram import Dispatcher, types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


def rate_limit(limit: int, key=None):

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func
    return decorator


class ThrottlingMiddleware(BaseMiddleware):

    def __init__(self, limit=1, key_prefix="antiflood_"):
        self.limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def throttle(self, target: Union[types.Message, types.CallbackQuery]):
        handler = current_handler.get()
        if not handler:
            return

        dp = Dispatcher.get_current()
        limit = getattr(handler, "throttling_rate_limit", self.limit)
        key = getattr(handler, "throttling_key",
                      f"{self.prefix}_{handler.__name__}")
        try:
            await dp.throttle(key, rate=limit)
        except Throttled as t:
            await self.target_throttled(target, t, dp, key)
            raise CancelHandler()

    @staticmethod
    async def target_throttled(target: Union[types.Message, types.CallbackQuery],
                               throttled: Throttled, dispatcher: Dispatcher, key: str):
        msg = target.message if isinstance(
            target, types.CallbackQuery) else target
        delta = throttled.rate - throttled.delta
        # if throttled.exceeded_count == 2:
        #     await msg.reply("Dont spam")
        #     return

        # elif throttled.exceeded_count == 3:
        #     await msg.reply(f"{delta}")
        #     return

        await asyncio.sleep(delta)

        # thr = await dispatcher.check_key(key)
        # if thr.exceeded_count == throttled.exceeded_count:
        #     await msg.reply("OK")

    async def on_process_message(self, message, data):
        await self.throttle(message)

    async def on_process_callback_query(self, call, data):
        await self.throttle(call)
