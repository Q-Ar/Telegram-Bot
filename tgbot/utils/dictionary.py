DAY_CHOICES = {
    'MON': ['Понедельник', 'Пн'],
    'TUE': ['Вторник', 'Вт'],
    'WED': ['Среда', 'Ср'],
    'THU': ['Четверг', 'Чт'],
    'FRI': ['Пятница', 'Пт'],
    'SAT': ['Суббота', 'Сб'],
    'SUN': ['Воскресенье', 'Вc'],
}


def get_days_dict(is_short=False):
    return {key: values[1 if is_short else 0] for key, values in DAY_CHOICES.items()}


TYPE_OF_CHANGE_WORK_SCHEDULE = {
    'Distant': 'Удаленный день',
    'Offline': 'Очный день',
    'TotalOut': 'Полное отсутствие',
    'PartAv': 'Частичная доступность',
    'EarlyGo': 'Ранний уход',
}


def get_types_of_change_w_sch_dict():
    return TYPE_OF_CHANGE_WORK_SCHEDULE


FREQUENCY_REMINDER = {
    1: 'Каждый час',
    3: 'Каждые три часа',
    24: 'Каждый день',
    48: 'Каждые два дня',
    168: 'Каждую неделю'
}


def get_frequency_reminder_dict():
    return FREQUENCY_REMINDER
