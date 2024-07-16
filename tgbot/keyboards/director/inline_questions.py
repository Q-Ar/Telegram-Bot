from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class QuestionsCallBack(CallbackData, prefix="menu_questions"):
    level: int
    page: int = 1
    menu_name: str
    question_id: int | None = None
    status: str | None = None
    status_text: str | None = None


class AnswerCallBack(CallbackData, prefix="menu_answer"):
    q_id: int | None = None
    previos_page: int = 1


def get_questions_main_btns(*, level: int, sizes: tuple[int] = (1, )):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Новые 🆕": "new",
        "Решенные ✅": "answered",
    }
    for text, menu_name in btns.items():
        if menu_name == 'new':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=QuestionsCallBack(level=1, menu_name=menu_name, status=menu_name, status_text=text).pack()))
        elif menu_name == 'answered':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=QuestionsCallBack(level=1, menu_name=menu_name, status=menu_name, status_text=text).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=QuestionsCallBack(level=level, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_questions_list_menu_btns(
        *,
        level: int,
        page: int | None,
        pagination_btns: dict | None,
        question_id: int | None,
        sizes: tuple[int] = (2,),
        status: str,
        status_text: str | None = None,
        div: int
):
    keyboard = InlineKeyboardBuilder()
    if page:
        if status != 'answered':
            keyboard.add(InlineKeyboardButton(text='Ответить',
                                              callback_data=AnswerCallBack(q_id=question_id, previos_page=page).pack()))
            keyboard.add(InlineKeyboardButton(text='Пометить решенным',
                                              callback_data=QuestionsCallBack(level=level, menu_name='mark_as_done',
                                                                         question_id=question_id, page=page, status=status, status_text="Новые 🆕").pack()))
            keyboard.adjust(*sizes)

        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == "next":
                row.append(InlineKeyboardButton(text=text,
                                                callback_data=QuestionsCallBack(
                                                    level=level,
                                                    menu_name=menu_name,
                                                    page=page + 1,
                                                    div=div,
                                                    status=status,
                                                ).pack()))

            elif menu_name == "previous":
                row.append(InlineKeyboardButton(text=text,
                                                callback_data=QuestionsCallBack(
                                                    level=level,
                                                    menu_name=menu_name,
                                                    div=div,
                                                    status=status,
                                                    page=page - 1).pack()))
        keyboard.row(*row)

        row2 = [
            InlineKeyboardButton(text='Назад ↩️',
                                 callback_data=QuestionsCallBack(
                                     level=0,
                                     menu_name='Вопросы сотрудников').pack())
        ]
        return keyboard.row(*row2).as_markup()
    else:
        keyboard.add(
            InlineKeyboardButton(text='Назад ↩️',
                                 callback_data=QuestionsCallBack(
                                     level=0,
                                     menu_name='Вопросы сотрудников').pack())
        )

        return keyboard.adjust(*sizes).as_markup()
