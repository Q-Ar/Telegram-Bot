from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.orm_query.orm_director import orm_get_division_employees, orm_get_work_schedules, orm_get_work_schedule, \
    orm_get_working_location, orm_get_changes_work_schedule, \
    orm_get_employee_full_name, orm_get_change_work_schedule
from tgbot.utils.dictionary import get_days_dict, get_types_of_change_w_sch_dict
from tgbot.utils.time_btns import time_h_btns, time_m_btns


class WorkSchedulesCallBack(CallbackData, prefix="W_Sch"):
    level: int
    menu_name: str
    work_schedule_id: int | None = None
    change_type: str | None = None
    time_type: str | None = None  # sh-start hour; sm-start minutes; eh-end hour; em-end minutes;
    employee_id: int | None = None
    day: str | None = None
    time: str | None = None
    location_id: int | None = None


# Кнопки главного меню вкладки графики работы
def get_work_schedules_main_btns(*, level: int, sizes: tuple[int] = (1, )):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Расписания 📅": "work_schedules",
        "Изменения 🔄": "w_sch_chang",
    }
    for text, menu_name in btns.items():
        if menu_name == 'work_schedules':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(
                                                  level=1, menu_name=menu_name
                                              ).pack()))
        elif menu_name == 'w_sch_chang':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(
                                                  level=7, menu_name=menu_name
                                              ).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(
                                                  level=level, menu_name=menu_name
                                              ).pack()))

    return keyboard.adjust(*sizes).as_markup()


# Кнопки для выбора сотрудника
def get_work_schedules_employee_list_menu_btns(
        *,
        division_id: int,
        sizes: tuple[int] = (2,),
        menu_name: str,
):
    keyboard = InlineKeyboardBuilder()

    employees = orm_get_division_employees(division_id)

    if employees:
        for employee in employees:
            keyboard.add(InlineKeyboardButton(text=f'{employee.surname} {employee.name[0:1]}. {employee.patronymic[0:1]}.',
                                              callback_data=WorkSchedulesCallBack(
                                                  level=2, menu_name=menu_name, employee_id=employee.id
                                              ).pack()))
        keyboard.adjust(*sizes)

        # region Шаблон кнопок пагинатора
        # row = []
        # for text, menu_name in pagination_btns.items():
        #     if menu_name == "next":
        #         row.append(InlineKeyboardButton(text=text,
        #                                         callback_data=WorkSchedulesCallBack(
        #                                             level=level,
        #                                             menu_name=menu_name,
        #                                             page=page + 1,
        #                                         ).pack()))
        #
        #     elif menu_name == "previous":
        #         row.append(InlineKeyboardButton(text=text,
        #                                         callback_data=WorkSchedulesCallBack(
        #                                             level=level,
        #                                             menu_name=menu_name,
        #                                             page=page - 1).pack()))
        # keyboard.row(*row)
        # endregion Шаблон кнопок пагинатора

        row2 = [
            InlineKeyboardButton(text='Назад ↩️',
                                 callback_data=WorkSchedulesCallBack(
                                     level=0,
                                     menu_name='main').pack())
        ]
        return keyboard.row(*row2).as_markup()

    else:
        keyboard.add(
            InlineKeyboardButton(text='Назад ↩️',
                                 callback_data=WorkSchedulesCallBack(
                                     level=0,
                                     menu_name='main').pack())
        )

        return keyboard.adjust(*sizes).as_markup()


# Кнопки для меню просмотра графиков сотрудника
def get_work_schedule_employee_btns(
        *,
        menu_name: str,
        sizes: tuple[int] = (2,),
        employee_id: int,
):
    keyboard = InlineKeyboardBuilder()
    if menu_name == 'work_schedules':
        keyboard.add(InlineKeyboardButton(text='Редактировать',
                                          callback_data=WorkSchedulesCallBack(
                                              level=3, employee_id=employee_id,
                                              menu_name=menu_name,
                                          ).pack()))
        keyboard.adjust(*sizes)
        row2 = [
            InlineKeyboardButton(text='К списку сотрудников ↩️',
                                 callback_data=WorkSchedulesCallBack(
                                     level=1,
                                     menu_name=menu_name).pack())
        ]
        return keyboard.row(*row2).as_markup()
    else:
        keyboard.add(
            InlineKeyboardButton(text='К списку сотрудников ↩️',
                                 callback_data=WorkSchedulesCallBack(
                                     level=1,
                                     menu_name='Список сотрудников').pack())
        )

        return keyboard.adjust(*sizes).as_markup()


# Кнопки для выбора или создания определенного графика работы сотрудника
def get_work_schedule_employee_change_btns(
        *,
        menu_name: str,
        sizes: tuple[int] = (2,),
        employee_id: int | None = None,
):
    keyboard = InlineKeyboardBuilder()
    work_schedule = orm_get_work_schedules(employee_id=employee_id)
    if work_schedule:
        for item in work_schedule:
            keyboard.add(InlineKeyboardButton(text=f"{get_days_dict(is_short=True)[item['day']]}. {item['start_time'].strftime('%H:%M')}-{item['end_time'].strftime('%H:%M')} -> {item['location__location_name']}",
                                              callback_data=WorkSchedulesCallBack(
                                                  level=4, menu_name=menu_name, employee_id=employee_id,
                                                  work_schedule_id=item['id']
                                              ).pack()))
        keyboard.adjust(*sizes)

        row = [
            InlineKeyboardButton(text='Добавить ➕',
                                 callback_data=WorkSchedulesCallBack(
                                     level=6, menu_name="add", employee_id=employee_id
                                 ).pack())
        ]

        keyboard.row(*row)

        row2 = [
            InlineKeyboardButton(text='Назад ↩️',
                                 callback_data=WorkSchedulesCallBack(
                                     level=2,
                                     menu_name='work_schedules', employee_id=employee_id
                                 ).pack())
        ]
        return keyboard.row(*row2).as_markup()

    else:
        row = [
            InlineKeyboardButton(text='Добавить ➕',
                                 callback_data=WorkSchedulesCallBack(
                                     level=6, menu_name="add", employee_id=employee_id
                                 ).pack())
        ]

        keyboard.row(*row)

        row2 = [
            InlineKeyboardButton(text='Назад ↩️',
                                 callback_data=WorkSchedulesCallBack(
                                     level=2,
                                     menu_name='work_schedules', employee_id=employee_id
                                 ).pack())
        ]
        return keyboard.row(*row2).as_markup()


# Кнопки для меню редактирования определенного графика работы сотрудника
def get_work_schedule_change_btns(
        *,
        level: int,
        menu_name: str,
        sizes: tuple[int] = (2,),
        employee_id: int | None = None,
        work_schedule_id: int | None = None
):
    keyboard = InlineKeyboardBuilder()

    btns = {
        "День 🗓️": "day",
        "Время 🕒": "time_",
        "Место 📍": "location",
        "Удалить ❌": "delete",
    }
    for text, btn_name in btns.items():
        if btn_name == 'day':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(
                                                  level=5, menu_name=menu_name, change_type=btn_name,
                                                  work_schedule_id=work_schedule_id, employee_id=employee_id
                                              ).pack()))
        elif btn_name == 'time_':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(
                                                  level=5, menu_name=menu_name, change_type=btn_name, time_type="sh",
                                                  work_schedule_id=work_schedule_id, employee_id=employee_id
                                              ).pack()))
        elif btn_name == 'location':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(
                                                  level=5, menu_name=menu_name, change_type=btn_name,
                                                  work_schedule_id=work_schedule_id, employee_id=employee_id
                                              ).pack()))
        elif btn_name == 'delete':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(
                                                  level=5, menu_name=menu_name, change_type=btn_name,
                                                  work_schedule_id=work_schedule_id, employee_id=employee_id
                                              ).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(
                                                  level=level, menu_name=menu_name, change_type=btn_name
                                              ).pack()))

    keyboard.adjust(*sizes)

    row = [
        InlineKeyboardButton(text='Назад ↩️',
                             callback_data=WorkSchedulesCallBack(
                                 level=3,
                                 menu_name='work_schedules', employee_id=employee_id
                             ).pack())
    ]
    return keyboard.row(*row).as_markup()


# Кнопки для подтверждения удаления
def get_confirm_delete_btns(
        *,
        level: int,
        menu_name: str,
        sizes: tuple[int] = (2,),
        employee_id: int | None = None,
        work_schedule_id: int | None = None,
):
    keyboard = InlineKeyboardBuilder()
    row = [
        InlineKeyboardButton(text='ДА ✅',
                             callback_data=WorkSchedulesCallBack(
                                 level=3, menu_name=menu_name, employee_id=employee_id,
                                 work_schedule_id=work_schedule_id, change_type="delete_confirmed"
                             ).pack()),
        InlineKeyboardButton(text='НЕТ ❌',
                             callback_data=WorkSchedulesCallBack(
                                 level=4, menu_name=menu_name, employee_id=employee_id,
                                 work_schedule_id=work_schedule_id
                             ).pack())
    ]
    return keyboard.row(*row).as_markup()


# Кнопки для редактирования дня
def get_days_list_to_change_btns(
        *,
        level: int,
        menu_name: str,
        sizes: tuple[int] = (1,),
        employee_id: int | None = None,
        work_schedule_id: int | None = None,
        type: str = "change"
):
    keyboard = InlineKeyboardBuilder()

    for btn_name, text in get_days_dict().items():
        if type != "add":
            w_sch, location = orm_get_work_schedule(work_schedule_id=work_schedule_id)
            day = w_sch.day
            if day != btn_name:
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=WorkSchedulesCallBack(
                                                      level=level, menu_name=menu_name, change_type="day_"+btn_name,
                                                      work_schedule_id=work_schedule_id, employee_id=employee_id
                                                  ).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(
                                                  level=level, menu_name=menu_name, time_type="sh", day=btn_name,
                                                  work_schedule_id=work_schedule_id, employee_id=employee_id
                                              ).pack()))

    keyboard.adjust(*sizes)

    callback_data_cancel = CallbackData()
    if type != "add":
        callback_data_cancel = WorkSchedulesCallBack(
                                 level=level, menu_name='work_schedules',
                                 employee_id=employee_id, work_schedule_id=work_schedule_id
                             )
    else:
        callback_data_cancel = WorkSchedulesCallBack(
                                 level=3, menu_name='work_schedules',
                                 employee_id=employee_id)
    row = [
        InlineKeyboardButton(text='Отмена 🚫',
                             callback_data=callback_data_cancel.pack())
    ]
    return keyboard.row(*row).as_markup()


# Кнопки для редактирования локации
def get_work_location_list_to_change_btns(
        *,
        level: int,
        menu_name: str,
        sizes: tuple[int] = (1,),
        employee_id: int | None = None,
        work_schedule_id: int | None = None,
        type: str = "change",
        time: str | None = None,
        day: str | None = None,
):
    keyboard = InlineKeyboardBuilder()
    locations = orm_get_working_location()
    for location in locations:
        if type != "add":
            w_sch, loc = orm_get_work_schedule(work_schedule_id=work_schedule_id)
            if location.id != loc.id:
                keyboard.add(InlineKeyboardButton(text=location.location_name,
                                                  callback_data=WorkSchedulesCallBack(
                                                      level=level, menu_name=menu_name, change_type="location_" + str(location.id),
                                                      work_schedule_id=work_schedule_id, employee_id=employee_id
                                                  ).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=location.location_name,
                                              callback_data=WorkSchedulesCallBack(
                                                  level=level, menu_name=menu_name,
                                                  employee_id=employee_id,
                                                  day=day,
                                                  time=time,
                                                  location_id=location.id,
                                              ).pack()))

    keyboard.adjust(*sizes)
    callback_data_cancel = CallbackData()
    if type != "add":
        callback_data_cancel = WorkSchedulesCallBack(
                                 level=level, menu_name='work_schedules',
                                 employee_id=employee_id, work_schedule_id=work_schedule_id
                             )
    else:
        callback_data_cancel = WorkSchedulesCallBack(
                                 level=3, menu_name='work_schedules',
                                 employee_id=employee_id)
    row = [
        InlineKeyboardButton(text='Отмена 🚫',
                             callback_data=callback_data_cancel.pack())
    ]
    return keyboard.row(*row).as_markup()


# Кнопки для редактирования времени
def get_time_set_list_btns(
        *,
        level: int,
        menu_name: str,
        sizes_h: tuple[int] = (6,),
        sizes_m: tuple[int] = (3,),
        employee_id: int | None = None,
        work_schedule_id: int | None = None,
        change_type: str | None = None,
        time_type: str,
        type: str = "change",
        time: str = "",
        day: str | None = None,

):
    keyboard = InlineKeyboardBuilder()

    btns_h = time_h_btns()
    btns_m = time_m_btns()

    if time_type == "sh" or time_type == "eh":
        if time_type == "sh":
            time_type = "sm"
        elif time_type == "eh":
            time_type = "em"

        for text, btn_name in btns_h.items():
            if type != "add":
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=WorkSchedulesCallBack(
                                                      level=level, menu_name=menu_name,
                                                      change_type=change_type + btn_name, time_type=time_type,
                                                      work_schedule_id=work_schedule_id, employee_id=employee_id
                                                  ).pack()))
            else:
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=WorkSchedulesCallBack(
                                                      level=level, menu_name=menu_name,
                                                      employee_id=employee_id, time_type=time_type,
                                                      day=day, time=str(time) + btn_name
                                                  ).pack()))

        keyboard.adjust(*sizes_h)
    elif time_type == "sm" or time_type == "em":
        if time_type == "sm":
            time_type = "eh"

        if time_type == "em":
            if type != "add":
                level = level - 1
            else:
                menu_name = "add_location"
        elif time_type == "sm":
            if type != "add":
                level = level - 1

        for text, btn_name in btns_m.items():
            if type != "add":
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=WorkSchedulesCallBack(
                                                      level=level, menu_name=menu_name,
                                                      change_type=change_type + f"{btn_name}_", time_type=time_type,
                                                      work_schedule_id=work_schedule_id, employee_id=employee_id
                                                  ).pack()))
            else:
                keyboard.add(InlineKeyboardButton(text=text,
                                                  callback_data=WorkSchedulesCallBack(
                                                      level=level, menu_name=menu_name,
                                                      time_type=time_type, employee_id=employee_id,
                                                      day=day, time=time + f"{btn_name}_",
                                                  ).pack()))
        keyboard.adjust(*sizes_m)

    callback_data_cancel = CallbackData()
    if type != "add":
        callback_data_cancel = WorkSchedulesCallBack(
                                 level=4, menu_name='work_schedules',
                                 employee_id=employee_id, work_schedule_id=work_schedule_id
                             )
    else:
        callback_data_cancel = WorkSchedulesCallBack(
            level=3, menu_name='work_schedules',
            employee_id=employee_id)

    row = [
        InlineKeyboardButton(text='Отмена 🚫',
                             callback_data=callback_data_cancel.pack())
    ]
    return keyboard.row(*row).as_markup()


# Кнопки главного меню для меню "запрос на изменение графика работы"
def get_change_work_schedule_main_btns(*, level: int, sizes: tuple[int] = (2, )):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Новые 🆕": "new",
        "Решенные ✅": "resolved",
    }
    for text, menu_name in btns.items():
        if menu_name == 'new':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == 'resolved':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(level=level+1, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=WorkSchedulesCallBack(level=level, menu_name=menu_name).pack()))

    keyboard.adjust(*sizes)

    row2 = [
        InlineKeyboardButton(text='Назад ↩️',
                             callback_data=WorkSchedulesCallBack(
                                 level=0,
                                 menu_name='main').pack())
    ]
    return keyboard.row(*row2).as_markup()


# Кнопки выбора экземпляра запроса на изменение графика работы
def get_change_work_schedule_list_btns(
        *,
        level: int,
        menu_name: str,
        division_id: int,
        sizes: tuple[int] = (1, )

):
    keyboard = InlineKeyboardBuilder()

    changes_work_schedule = orm_get_changes_work_schedule(division_id=division_id, is_new=True if menu_name == "new" else False)
    for item in changes_work_schedule:
        full_name = orm_get_employee_full_name(employee_id=item.employee_id,abbreviated=True)
        keyboard.add(InlineKeyboardButton(
            text=f"{full_name} {item.day.strftime('%d.%m.%y')}  {get_types_of_change_w_sch_dict()[item.type]} ",
            callback_data=WorkSchedulesCallBack(
                level=level+1, menu_name=menu_name,
                work_schedule_id=item.id
            ).pack()))
    keyboard.adjust(*sizes)

    row2 = [
        InlineKeyboardButton(text='Назад ↩️',
                             callback_data=WorkSchedulesCallBack(
                                 level=level-1,
                                 menu_name='main').pack())
    ]
    return keyboard.row(*row2).as_markup()


def get_change_work_schedule_change_btns(
        *,
        level: int,
        menu_name: str,
        work_schedule_id: int,
        sizes: tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()
    change_work_schedule = orm_get_change_work_schedule(id=work_schedule_id)
    if change_work_schedule.is_agreed == False or change_work_schedule.is_agreed == None:
        keyboard.add(InlineKeyboardButton(text='Одобрить ✅',
                                          callback_data=WorkSchedulesCallBack(
                                              level=level - 1, menu_name=menu_name,
                                              work_schedule_id=work_schedule_id, change_type="agree"
                                          ).pack()))

    if change_work_schedule.is_agreed == True or change_work_schedule.is_agreed == None:
        keyboard.add(InlineKeyboardButton(text='Отклонить ❌',
                                          callback_data=WorkSchedulesCallBack(
                                              level=level - 1, menu_name=menu_name,
                                              change_type="disagree_nr",
                                              work_schedule_id=work_schedule_id,
                                          ).pack()))

    keyboard.adjust(*sizes)

    if change_work_schedule.is_agreed == True or change_work_schedule.is_agreed == None:
        row = [
            InlineKeyboardButton(text='Отклонить с пояснением причины ✍️❌',
                                 callback_data=WorkSchedulesCallBack(
                                     level=10, menu_name=menu_name, change_type="disagr_reas",
                                     work_schedule_id=work_schedule_id
                                 ).pack())
            ]
        keyboard.row(*row)



    row2 = [
        InlineKeyboardButton(text='Назад ↩️',
                             callback_data=WorkSchedulesCallBack(
                                 level=level-1,
                                 menu_name=menu_name).pack())
    ]
    return keyboard.row(*row2).as_markup()


def get_change_work_schedule_cancel_btns(
        *,
        level: int,
        menu_name: str,
        work_schedule_id: int,
        sizes: tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()
    row2 = [
        InlineKeyboardButton(text='Отмена ❌',
                             callback_data=WorkSchedulesCallBack(
                                 level=9, menu_name=menu_name,
                                 work_schedule_id=work_schedule_id, change_type="cancel").pack())
    ]
    return keyboard.row(*row2).as_markup()
