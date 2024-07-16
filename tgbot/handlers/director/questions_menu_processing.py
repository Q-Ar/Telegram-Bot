
from tgbot.keyboards.director.inline_questions import get_questions_main_btns, get_questions_list_menu_btns
from tgbot.orm_query.orm_director import orm_get_division_questions, orm_get_director_division_id, orm_change_question_status, \
    orm_get_question_employee, orm_change_question_answer
from tgbot.utils.paginator import Paginator
from tgbot.utils.paginator_btns import paginator_btns


async def main_questions_menu(level, menu_name):
    text = menu_name
    kbds = get_questions_main_btns(level=level)

    return text, kbds


async def questions(level, menu_name, status, page, user_id, status_text, question_id):
    if menu_name == "mark_as_done":
        orm_change_question_status(question_id, "answered")
        orm_change_question_answer(question_id, "Решён ✅")
        if page > 1:
            page -= 1

    div = orm_get_director_division_id(user_id)
    questions = orm_get_division_questions(status=status, division_id=div)
    if not questions:
        kbds = get_questions_list_menu_btns(
            question_id=None,
            level=level,
            page=None,
            pagination_btns=None,
            status=status,
            div=div,
        )
        text = f"Список вопросов \"{status_text}\" - пуст"
        return text, kbds
    else:
        paginator = Paginator(questions, page=page)
        question = paginator.get_page()[0]
        employee = orm_get_question_employee(question.id)
        text = f"<strong>от: {employee.surname} {employee.name} {employee.patronymic}</strong>\n"\
               f"<strong>тема: {question.title}</strong>\n" \
               f"<strong>вопрос:</strong> {question.question}\n\n" \
               f"{'<strong>ответ:</strong> '+question.answer if question.answer else ''}\n\n" \
               f"<strong>Вопрос {paginator.page} из {paginator.pages}</strong>"

        pagination_btns = paginator_btns(paginator)

        kbds = get_questions_list_menu_btns(
            question_id=question.id,
            level=level,
            page=page,
            pagination_btns=pagination_btns,
            status=status,
            div=div,
        )
        return text, kbds


async def get_menu_questions_content(
    level: int,
    menu_name: str,
    page: int | None = None,
    user_id: int | None = None,
    status: str | None = None,
    status_text: str | None = None,
    question_id: int | None = None
):
    if level == 0:
        return await main_questions_menu(level, menu_name)
    elif level == 1:
        return await questions(level, menu_name, status, page, user_id, status_text, question_id)

