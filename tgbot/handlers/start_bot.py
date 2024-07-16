import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ.update({'DJANGO_ALLOW_ASYNC_UNSAFE': "true"})
django.setup()

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.models import TGUser


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    users = TGUser.objects.filter(username=message.from_user.username)
    if(users.exists()):
        for user in users:
            if user.telegram_id == None:
                user.telegram_id = int(message.from_user.id)
                user.save()
                await message.answer("Вы успешно добавлены в систему")
            else:
                await message.answer("Вы в системе")
    else:
        await message.answer(f"Ваши данные не найдены. Обратитесь к руководителю и сообщите ему:\n"
                             f"'<code>{message.from_user.username}:{message.from_user.id}</code>'")