from aiogram import types
from aiogram.filters import Filter

from bot.models import Director, Employee


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


class IsDirector(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message):
        return Director.objects.filter(employee__user__telegram_id=message.from_user.id, is_active=True).exists()


class IsEmployee(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message):
        return Employee.objects.filter(user__telegram_id=message.from_user.id).exists()
