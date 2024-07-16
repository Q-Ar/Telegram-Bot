from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeAllPrivateChats, BotCommandScopeChat

from tgbot.orm_query.orm_director import orm_get_all_directors_telegram_id, orm_get_all_employee_telegram_id

directors_list = orm_get_all_directors_telegram_id()
employees_list = orm_get_all_employee_telegram_id()


async def set_commands(bot: Bot):
    commands_employee = [
        BotCommand(
            command='start',
            description='Начало работы'
        ),
        BotCommand(
            command='help',
            description='Подсказка'
        ),
        BotCommand(
            command='employee',
            description='Меню работника'
        ),
    ]
    commands_director = [
            BotCommand(
                command='start',
                description='Начало работы'
            ),
            BotCommand(
                command='help',
                description='Подсказка'
            ),
            BotCommand(
                command='director',
                description='Меню директора'
            ),
        ]

    for director in directors_list:
        await bot.set_my_commands(commands=commands_director, scope=BotCommandScopeChat(chat_id=director))
    for employee in employees_list:
        await bot.set_my_commands(commands=commands_employee, scope=BotCommandScopeChat(chat_id=employee))
