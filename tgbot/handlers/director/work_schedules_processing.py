from tgbot.keyboards.director.inline_work_schedules import get_work_schedules_main_btns, \
    get_work_schedules_employee_list_menu_btns, get_work_schedule_employee_btns, get_work_schedule_employee_change_btns, \
    get_work_schedule_change_btns, get_confirm_delete_btns, get_days_list_to_change_btns, \
    get_work_location_list_to_change_btns, get_time_set_list_btns, get_change_work_schedule_main_btns, \
    get_change_work_schedule_list_btns, get_change_work_schedule_change_btns, get_change_work_schedule_cancel_btns
from tgbot.orm_query.orm_director import orm_get_director_division_id, orm_get_work_schedules, \
    orm_get_employee_full_name, \
    orm_get_work_schedule, orm_delete_work_schedule, orm_change_work_schedule_day, orm_change_work_schedule_location, \
    orm_change_work_schedule_time_start, orm_change_work_schedule_time_end, orm_add_work_schedule, \
    orm_get_change_work_schedule, orm_change_change_work_schedule, orm_get_access_changes_work_schedule
from tgbot.utils.dictionary import get_days_dict, get_types_of_change_w_sch_dict

from datetime import datetime


async def main_work_schedules_menu(level):
    text = "Рабочий график сотрудников"
    kbds = get_work_schedules_main_btns(level=level)

    return text, kbds


async def work_schedules_employees_list(user_id, menu_name):
    division_id = orm_get_director_division_id(user_id)
    text = "Список сотрудников:"
    kbds = get_work_schedules_employee_list_menu_btns(menu_name=menu_name, division_id=division_id)

    return text, kbds


async def get_text_work_schedule(employee_id):
    work_schedules = orm_get_work_schedules(employee_id=employee_id)
    work_schedule_days = {'MON': "<strong>Понедельник:</strong>\n",
                          'TUE': "<strong>Вторник:</strong>\n",
                          'WED': "<strong>Среда:</strong>\n",
                          'THU': "<strong>Четверг:</strong>\n",
                          'FRI': "<strong>Пятница:</strong>\n",
                          'SAT': "<strong>Суббота:</strong>\n",
                          'SUN': "<strong>Воскресенье:</strong>\n",
                          }
    for item in work_schedules:
        work_schedule_days[item['day']] += f"  {item['start_time'].strftime('%H:%M')}-{item['end_time'].strftime('%H:%M')} --> {item['location__location_name']}\n"

    work_schedule_text = f"<strong>Расписание <u>{orm_get_employee_full_name(employee_id=employee_id)}</u></strong>\n\n"
    for key in work_schedule_days:
        if work_schedule_days[key].count("\n") > 1:
            work_schedule_text += work_schedule_days[key]

    changes_work_schedule_text = "\n\n*Изменения в графике работника:\n"
    access_changes_work_shedule = orm_get_access_changes_work_schedule(employee_id)
    if access_changes_work_shedule:
        for item in access_changes_work_shedule:
            if datetime.date(datetime.now()) <= item.day:
                changes_work_schedule_text += f"{get_days_dict(is_short=True)[item.day.strftime('%a').upper()]}: " \
                                              f"{item.day.strftime('%d.%m.%Y')} - {get_types_of_change_w_sch_dict()[item.type]}\n"
    if changes_work_schedule_text != "\n\n*Изменения в графике работника:\n":
        work_schedule_text += changes_work_schedule_text
    return work_schedule_text


async def work_schedule_employee(menu_name, employee_id):
    text = await get_text_work_schedule(employee_id=employee_id)
    kbds = get_work_schedule_employee_btns(menu_name=menu_name, employee_id=employee_id)

    return text, kbds


async def work_schedule_employee_change(menu_name, employee_id, change_type: str | None = None, work_schedule_id: int | None = None):
    if change_type == "delete_confirmed":
        orm_delete_work_schedule(work_schedule_id)
    full_name = orm_get_employee_full_name(employee_id=employee_id)
    text = f"Редактирование рабочего графика <strong><u>{full_name}</u></strong>: "
    kbds = get_work_schedule_employee_change_btns(menu_name=menu_name, employee_id=employee_id)

    return text, kbds


async def work_schedule_change_menu(level, menu_name, employee_id, work_schedule_id, change_type, time_type):
    if change_type:
        if change_type.startswith("day_"):
            changed_day = change_type.split("_")[-1]
            orm_change_work_schedule_day(work_schedule_id=work_schedule_id, changed_day=changed_day)
        elif change_type.startswith("location_"):
            changed_location = change_type.split("_")[-1]
            orm_change_work_schedule_location(work_schedule_id=work_schedule_id, location_id=changed_location)
        elif change_type.startswith("time_") and time_type == "em":
            changed_time = change_type.split("_")
            start_time = f"{changed_time[1][:2]}:{changed_time[1][2:]}"
            end_time = f"{changed_time[2][:2]}:{changed_time[2][2:]}"
            orm_change_work_schedule_time_start(work_schedule_id=work_schedule_id, start_time=start_time)
            orm_change_work_schedule_time_end(work_schedule_id=work_schedule_id, end_time=end_time)

    work_schedule, location = orm_get_work_schedule(work_schedule_id=work_schedule_id)
    full_name = orm_get_employee_full_name(employee_id=employee_id)
    text = f"<strong>Редактирование рабочего графика</strong>\n" \
           f"У работника: <strong><u>{full_name}</u></strong>\n" \
           f"График работы:\n   {get_days_dict()[work_schedule.day]} {work_schedule.start_time.strftime('%H:%M')}-{work_schedule.end_time.strftime('%H:%M')} -> {location.location_name}"
    kbds = get_work_schedule_change_btns(menu_name=menu_name, employee_id=employee_id, work_schedule_id=work_schedule_id, level=level)

    return text, kbds


async def work_schedule_make_change(level, menu_name, employee_id, work_schedule_id, change_type, time_type):
    work_schedule, location = orm_get_work_schedule(work_schedule_id=work_schedule_id)
    full_name = orm_get_employee_full_name(employee_id=employee_id)
    if change_type == "delete":
        text = f"<strong>Подтвердите удаление</strong>\n" \
               f"У работника: <strong><u>{full_name}</u></strong>\n" \
               f"График работы: {work_schedule.day} {work_schedule.start_time.strftime('%H:%M')}-{work_schedule.end_time.strftime('%H:%M')} --> {location.location_name}"
        kbds = get_confirm_delete_btns(level=level, menu_name=menu_name, employee_id=employee_id, work_schedule_id=work_schedule_id)
        return text, kbds

    elif change_type == "day":
        text = f"<strong>Изменение дня графика</strong>\n" \
               f"У работника: <strong><u>{full_name}</u></strong>\n" \
               f"График работы: <strong><u>{work_schedule.day}</u></strong> {work_schedule.start_time.strftime('%H:%M')}-{work_schedule.end_time.strftime('%H:%M')} --> {location.location_name}\n" \
               f"На новый день графика:"
        kbds = get_days_list_to_change_btns(level=4, menu_name=menu_name, employee_id=employee_id, work_schedule_id=work_schedule_id)
        return text, kbds

    elif change_type == "location":
        text = f"<strong>Изменение дня графика</strong>\n" \
               f"У работника: <strong><u>{full_name}</u></strong>\n" \
               f"График работы: {work_schedule.day} {work_schedule.start_time.strftime('%H:%M')}-{work_schedule.end_time.strftime('%H:%M')} --> <strong><u>{location.location_name}</u></strong>\n" \
               f"На новое место графика:"
        kbds = get_work_location_list_to_change_btns(level=4, menu_name=menu_name, employee_id=employee_id, work_schedule_id=work_schedule_id)
        return text, kbds

    elif change_type.startswith("time_"):
        text = f"<strong>Изменение времени</strong>\n" \
               f"У работника: <strong><u>{full_name}</u></strong>\n" \
               f"Старый график работы: {work_schedule.day} <strong><u>{work_schedule.start_time.strftime('%H:%M')}-{work_schedule.end_time.strftime('%H:%M')}</u></strong> --> {location.location_name}\n"
        if time_type == "sh":
            text += "\n Выберите час начала графика"
        elif time_type == "sm":
            text += "\n Выберите минуту начала графика"
        elif time_type == "eh":
            text += "\n Выберите час конца графика"
        elif time_type == "em":
            text += "\n Выберите минуту конца графика"

        kbds = get_time_set_list_btns(level=5, menu_name=menu_name, employee_id=employee_id, work_schedule_id=work_schedule_id, time_type=time_type, change_type=change_type)
        return text, kbds


async def work_schedule_add(
        menu_name,
        change_type: str | None = None,
        time_type: str | None = None,
        employee_id: int | None = None,
        day: str | None = None,
        time: str = "",
        location_id: int | None = None,
):
    full_name = orm_get_employee_full_name(employee_id=employee_id)
    # Добавление даты
    if menu_name == "add":
        menu_next_name = "add_time"
        text = f"<strong>Выбор дня графика для добавления</strong>\n" \
               f"У работника: <strong><u>{full_name}</u></strong>\n\n" \
               f"Выбор дня:"
        kbds = get_days_list_to_change_btns(level=6,
                                            menu_name=menu_next_name,
                                            type="add",
                                            employee_id=employee_id,)
        return text, kbds

    # Добавление времени
    elif menu_name == "add_time":
        text = f"<strong>Выбор времени</strong>\n" \
               f"У работника: <strong><u>{full_name}</u></strong>\n\n"
        if time_type == "sh":
            text += "\n Выберите час начала графика"
        elif time_type == "sm":
            text += "\n Выберите минуту начала графика"
        elif time_type == "eh":
            text += "\n Выберите час конца графика"
        elif time_type == "em":
            text += "\n Выберите минуту конца графика"
        kbds = get_time_set_list_btns(level=6,
                                      type="add",
                                      menu_name=menu_name,
                                      employee_id=employee_id,
                                      time_type=time_type,
                                      change_type=change_type,
                                      time=time,
                                      day=day
                                      )
        return text, kbds
    # Добавление места
    elif menu_name == "add_location":
        text = f"<strong>Изменение дня графика</strong>\n" \
               f"У работника: <strong><u>{full_name}</u></strong>\n\n"\
               f"Выбор нового места графика:"
        kbds = get_work_location_list_to_change_btns(level=6,
                                                     type="add",
                                                     menu_name="all_data_collect",
                                                     employee_id=employee_id,
                                                     time=time,
                                                     day=day
                                                     )
        return text, kbds

    # Добавление даты, времени, места в БД / Выход
    elif menu_name == "all_data_collect" or menu_name == "Cancel":
        if menu_name == "all_data_collect":
            time = time.replace("None", "")
            time = time.split("_")
            start_time = f"{time[0][:2]}:{time[0][2:]}"
            end_time = f"{time[1][:2]}:{time[1][2:]}"
            orm_add_work_schedule(day=day, start_time=start_time, end_time=end_time, location_id=location_id, employee_id=employee_id)
        text = f"Редактирование рабочего графика <strong><u>{full_name}</u></strong>: "
        kbds = get_work_schedule_employee_change_btns(menu_name="work_schedules", employee_id=employee_id)
        return text, kbds


async def change_work_schedule_menu(level):
    text = f"<strong>Выберите тип</strong>: "
    kbds = get_change_work_schedule_main_btns(level=level)
    return text, kbds


async def change_work_schedule_list(level, user_id, menu_name, change_type, work_schedule_id):
    if change_type == "agree":
        orm_change_change_work_schedule(change_work_schedule_id=work_schedule_id, is_agreed= True)
    elif change_type == "disagree_nr":
        orm_change_change_work_schedule(change_work_schedule_id=work_schedule_id, is_agreed=False)

    div = orm_get_director_division_id(user_id)
    text = f"Список <strong><u>" \
           f"{'новых' if menu_name == 'new' else 'решенных' if menu_name == 'resolved' else ''}" \
           f"</u></strong> запросов на изменение рабочего графика"
    kbds = get_change_work_schedule_list_btns(level=level, division_id=div, menu_name=menu_name)
    return text, kbds


async def change_work_schedule_show_and_change(level, menu_name, work_schedule_id, change_type, user_id: int = None):
    change_work_schedule = orm_get_change_work_schedule(id=work_schedule_id)
    full_name = orm_get_employee_full_name(change_work_schedule.employee_id)
    text = f"Запрос от <strong>{full_name}</strong>\n" \
           f"День: <strong>{change_work_schedule.day.strftime('%d.%m.%Y')}</strong>\n" \
           f"Тип: <strong>{get_types_of_change_w_sch_dict()[change_work_schedule.type]}</strong>\n" \
           f"Причина: <strong>{change_work_schedule.reason}</strong>\n"
    if change_work_schedule.is_agreed == True:
        text += f"\nОдобренное ✅"
    elif change_work_schedule.is_agreed == False:
        text += f"\nОтклоненное ❌"
        if change_work_schedule.rejection_reason:
            text += f"\nПричина отказа:\n<strong>{change_work_schedule.rejection_reason}</strong>"
    if change_type == "answ":
        kbds = get_change_work_schedule_cancel_btns(level=level, menu_name=menu_name, work_schedule_id=work_schedule_id)
        return text, kbds
    else:
        kbds = get_change_work_schedule_change_btns(level=level, menu_name=menu_name, work_schedule_id=work_schedule_id)
        return text, kbds


async def get_menu_work_schedules_content(
    # Основные параметры
    level: int,
    page: int | None = None,
    menu_name: str | None = None,
    user_id: int | None = None,
    employee_id: int | None = None,
    work_schedule_id: int | None = None,
    change_type: str | None = None,
    time_type: str | None = None,

    # Для добавления нового графика работы
    day: str | None = None,
    time: str = "",
    location_id: int | None = None,

    # Для согласования изменения рабочего графика в определенный день
    # day
    type_change: str | None = None,
    reason_change: str | None = None,
    is_agree: bool | None = None,
    rejection_reason: str | None = None,
):
    # Уровень главного меню рабочего графика
    if level == 0:
        return await main_work_schedules_menu(level=level)
    # Уровень выбора сотрудника для получения его графиков
    elif level == 1:
        return await work_schedules_employees_list(user_id=user_id, menu_name=menu_name)
    # Уровень просмотра полного графика сотрудника и возможность его отредактировать
    elif level == 2:
        return await work_schedule_employee(menu_name=menu_name, employee_id=employee_id)
    # Уровень выбора определенного графика для редактирования или добавления нового
    elif level == 3:
        return await work_schedule_employee_change(menu_name=menu_name, employee_id=employee_id, change_type=change_type, work_schedule_id=work_schedule_id)
    # Уровень выбора параметра для редактирования графика и внесения их в базу
    elif level == 4:
        return await work_schedule_change_menu(level=level, menu_name=menu_name, employee_id=employee_id, work_schedule_id=work_schedule_id, change_type=change_type, time_type=time_type)
    # Уровень внесения изменения в график
    elif level == 5:
        return await work_schedule_make_change(level=level, menu_name=menu_name, employee_id=employee_id, work_schedule_id=work_schedule_id, change_type=change_type, time_type=time_type)
    # Уровень добавления нового рабочего графика:
    elif level == 6:
        return await work_schedule_add(menu_name=menu_name, change_type=change_type, time_type=time_type, employee_id=employee_id, day=day, time=time, location_id=location_id)
    # Уровень выбора списка запросов на изменения графика
    elif level == 7:
        return await change_work_schedule_menu(level=level)
    # Уровень выбора запроса на изменение графика из списка запросов
    elif level == 8:
        return await change_work_schedule_list(level=level, user_id=user_id, menu_name=menu_name, change_type=change_type, work_schedule_id=work_schedule_id)
    # Уровень выбора действия с запросом на изменение графика
    elif level == 9:
        return await change_work_schedule_show_and_change(level=level, menu_name=menu_name, work_schedule_id=work_schedule_id, change_type=change_type, user_id=user_id)
