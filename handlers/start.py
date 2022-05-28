from aiogram import Dispatcher, types
from db.models import SubDays
from middlewares.throttling import rate_limit
from sqlalchemy import update

link = "https://t.me/+vxtp7ccNo7ZmZDYy"


@rate_limit(limit=1)
async def start_cmd(m: types.Message):

    await m.answer(link)


async def chat_join_req(req: types.ChatJoinRequest):
    token = req.bot.get("pay")
    gid = req.chat.id
    uid = req.from_user.id
    ggid = -1001755813658

    payload = f"buysubon_{gid}"
    prices = [types.LabeledPrice(label="Подписка на месяц", amount="3000")]
    buy_sub = {
        "chat_id": uid,
        "title": "Подписка на канал",
        "description": "Оплатите подписку, чтобы получить доступ в группу",
        "payload": payload,
        "provider_token": token,
        "currency": "uah",
        "prices": prices
    }

    await req.bot.send_invoice(**buy_sub)


async def renew_sub(m: types.Message):
    token = m.bot.get("pay")

    payload = f"renew_-1001755813658"
    prices = [types.LabeledPrice(
        label="Продлить подписку на месяц", amount="3000")]
    buy_sub = {
        "chat_id": m.from_user.id,
        "title": "Переподписка на канал",
        "description": "Оплатите подписку, чтобы получить доступ в группу",
        "payload": payload,
        "provider_token": token,
        "currency": "uah",
        "prices": prices
    }

    await m.bot.send_invoice(**buy_sub)


async def accept_checkout(q: types.PreCheckoutQuery):
    await q.bot.answer_pre_checkout_query(q.id, ok=True, error_message="ERROR")


async def successsful(m: types.Message):
    db = m.bot.get("db")
    payload = m.successful_payment.invoice_payload.split("_")

    if payload[0] == "buysubon":
        async with db() as ssn:
            await ssn.merge(SubDays(
                user_id=m.chat.id,
                group_id=int(payload[1]),
                sub_days=30,
                status="member"
            ))
            await ssn.commit()
            await ssn.close()

        await m.bot.approve_chat_join_request(-1001755813658, m.chat.id)
        await m.bot.send_message(m.chat.id, "Ваша заявка одобрена")

    elif payload[0] == "renew":
        async with db() as ssn:
            await ssn.execute(update(SubDays).filter(
                SubDays.user_id == m.chat.id).values(sub_days=SubDays.sub_days + 30))
            await ssn.commit()
            await ssn.close()

        await m.answer("Вы продлили подписку на 30 дней")


def start_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands="start")
    dp.register_pre_checkout_query_handler(accept_checkout)
    dp.register_message_handler(
        successsful, content_types="successful_payment")
    dp.register_chat_join_request_handler(chat_join_req)
    dp.register_message_handler(renew_sub, commands="renew")
