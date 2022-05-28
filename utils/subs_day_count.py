from ast import Sub
from datetime import date, datetime

from aiogram import Dispatcher
from db.models import SubDays
from sqlalchemy import select, update


async def select_all_subs(dp: Dispatcher):
    db = dp.bot.get("db")

    async with db() as ssn:
        all_zero_days_query = await ssn.execute(select(SubDays).filter(
            SubDays.sub_days == 0).filter(SubDays.status == "member"))

        for usr in all_zero_days_query.scalars.all():
            await dp.bot.unban_chat_member(usr.group_id, usr.user_id)
            await dp.bot.send_message(usr.user_id, "Ваша подписка на группу истекла. Вы были кикнуты из группы")

        await ssn.execute(update(SubDays).filter(SubDays.sub_days == 0).filter(
            SubDays.status == "member").values(status="left"))

        await ssn.commit()

        all_subs_query = await ssn.execute(select(SubDays).filter(
            SubDays.status == "member").filter(SubDays.sub_days <= 2))

        for sub in all_subs_query.scalars().all():

            if (sub.sub_days == 1) or (sub.sub_days == 2):
                await dp.bot.send_message(sub.user_id, f"У вас остался {sub.sub_days} день(я) подписки!")

        await ssn.execute(update(SubDays).filter(SubDays.status == "member").values(
            sub_days=SubDays.sub_days - 1))
        await ssn.commit()
        await ssn.close()
