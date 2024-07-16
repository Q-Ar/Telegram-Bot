from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from tgbot.filters.chat_types import IsDirector, ChatTypeFilter
from tgbot.handlers.director.questions_menu_processing import get_menu_questions_content
from tgbot.handlers.director.work_schedules_processing import get_menu_work_schedules_content
from tgbot.keyboards.director.inline_questions import QuestionsCallBack, AnswerCallBack
from tgbot.keyboards.director.inline_work_schedules import WorkSchedulesCallBack

from tgbot.keyboards.reply import get_keyboard
from tgbot.orm_query.orm_director import orm_change_question_answer, orm_change_question_status, \
    orm_change_change_work_schedule

director_router = Router()
director_router.message.filter(IsDirector(), ChatTypeFilter(["private"]))


MAIN_DIRECTOR_KB = get_keyboard(
    "Сотрудники",
    "Мероприятия",
    "Уведомления",
    placeholder="Выберите интересующее",
    sizes=(1, 1, 1),
)


EMPLOYEE_DIRECTOR_KB = get_keyboard(
    "Вопросы",
    "Рабочие графики",
    "Больничные",
    "Отпуска",
    "Главная",
    placeholder="Выберите интересующее",
    sizes=(2, 2, 1),
)


@director_router.message(Command("director"))
@director_router.callback_query(F.data == 'director')
@director_router.message(F.text.lower() == "главная")
async def main_menu_director(message: types.Message):
    await message.answer("Главное меню директора", reply_markup=MAIN_DIRECTOR_KB)
    

@director_router.message(StateFilter(None), F.text == "Сотрудники")
async def director_employees(message: types.Message):
    await message.answer("Вкладка сотрудников", reply_markup=EMPLOYEE_DIRECTOR_KB)


# region Вопросы от сотрудников
@director_router.message(StateFilter(None), F.text == "Вопросы")
async def director_questions(message: types.Message):
    text, reply_markup = await get_menu_questions_content(level=0, menu_name="Вопросы сотрудников")
    await message.answer(text, reply_markup=reply_markup)


# region FSM (give answer to question)
class AddAnswer(StatesGroup):
    answer = State()
    question_id = State()
    user_id = State()
    previos_page = State()


@director_router.callback_query(StateFilter(None), AnswerCallBack.filter())
async def add_answer(callback: types.CallbackQuery, callback_data: AnswerCallBack, state: FSMContext):
    await state.update_data(question_id=callback_data.q_id)
    await state.update_data(user_id=callback.from_user.id)
    await state.update_data(previos_page=callback_data.previos_page)
    await callback.message.answer(f'Введите ответ на вопрос: ')
    await state.set_state(AddAnswer.answer)


@director_router.message(AddAnswer.answer, F.text)
async def load_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question_id = data.get('question_id')
    user_id = data.get('user_id')
    page = data.get('previos_page')
    if page > 1:
        page -= 1
    orm_change_question_answer(question_id=question_id, answer=message.text)
    orm_change_question_status(question_id=question_id, status="answered")
    await state.clear()
    text, reply_markup = await get_menu_questions_content(level=1, page=page, menu_name="answered", status="new", status_text="Новые 🆕", user_id=user_id, question_id=question_id)
    await message.answer(text, reply_markup=reply_markup)

# endregion FSM (give answer to question)


@director_router.callback_query(QuestionsCallBack.filter())
async def director_questions_menu(callback: types.CallbackQuery, callback_data: QuestionsCallBack):
    text, reply_markup = await get_menu_questions_content(
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        page=callback_data.page,
        user_id=callback.from_user.id,
        status=callback_data.status,
        status_text=callback_data.status_text,
        question_id=callback_data.question_id
    )

    await callback.message.edit_text(text=text, reply_markup=reply_markup)
    await callback.answer()

# endregion Вопросы от сотрудников


# region Рабочие графики

@director_router.message(F.text == "Рабочие графики")
async def director_work_schedules(message: types.Message):
    text, reply_markup = await get_menu_work_schedules_content(level=0)
    await message.answer(text, reply_markup=reply_markup)


# region FSM (получения причины отказа в изменении графика)
class AddRejectionReason(StatesGroup):
    answer = State()
    change_work_schedule_id = State()
    menu_name = State()


@director_router.callback_query(StateFilter(None), WorkSchedulesCallBack.filter(F.change_type =="disagr_reas"))
async def add_answer(callback: types.CallbackQuery, callback_data: WorkSchedulesCallBack, state: FSMContext):
    await state.update_data(change_work_schedule_id=callback_data.work_schedule_id)
    await state.update_data(menu_name=callback_data.menu_name)
    text, reply_markup = await get_menu_work_schedules_content(
        level=9,
        menu_name=callback_data.menu_name,
        work_schedule_id=callback_data.work_schedule_id,
        change_type="answ"
    )
    text += f'\n\n\n' \
            f'➤ Для отказа напишите причину отказа\n' \
            f'➤ Для отмены нажмите на кнопку "Отмена" ниже'
    await callback.message.edit_text(text=text, reply_markup=reply_markup)
    await state.set_state(AddRejectionReason.answer)


@director_router.callback_query(StateFilter('*'), WorkSchedulesCallBack.filter(F.change_type =="cancel"))
async def cancel_answer(callback: types.CallbackQuery, callback_data: WorkSchedulesCallBack, state: FSMContext):
    text, reply_markup = await get_menu_work_schedules_content(
        level=9,
        menu_name=callback_data.menu_name,
        work_schedule_id=callback_data.work_schedule_id,
        change_type=None
    )
    await state.clear()
    await callback.message.edit_text(text=text, reply_markup=reply_markup)


@director_router.message(AddRejectionReason.answer, F.text)
async def load_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    change_work_schedule_id = data.get('change_work_schedule_id')
    menu_name = data.get('menu_name')
    level = 8
    orm_change_change_work_schedule(change_work_schedule_id=change_work_schedule_id,
                                    is_agreed=False, rejection_reason=message.text)
    await state.clear()
    text, reply_markup = await get_menu_work_schedules_content(level=level, menu_name=menu_name, user_id=message.from_user.id,
                                                               work_schedule_id=None, change_type=None)
    await message.answer(text, reply_markup=reply_markup)

# endregion FSM (получения причины отказа в изменении графика)


@director_router.callback_query(WorkSchedulesCallBack.filter())
async def director_work_schedules_menu(callback: types.CallbackQuery, callback_data: WorkSchedulesCallBack):
    print(callback_data)
    text, reply_markup = await get_menu_work_schedules_content(
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        user_id=callback.from_user.id,
        employee_id=callback_data.employee_id,
        work_schedule_id=callback_data.work_schedule_id,
        change_type=callback_data.change_type,
        time_type=callback_data.time_type,
        time=callback_data.time,
        day=callback_data.day,
        location_id=callback_data.location_id
    )
    await callback.message.edit_text(text=text, reply_markup=reply_markup)
    await callback.answer()
# endregion Рабочие графики


@director_router.message()
async def main_menu_director(message: types.Message):
    await message.answer("Неизвестная команда")
