from django.db.models import Q
from bot.models import Employee, Question, WorkSchedule, WorkingLocation, Director, ChangeWorkSchedule


def orm_get_all_directors_telegram_id():
    return Director.objects.filter(is_active=True).select_related('employee__user').filter(employee__user__telegram_id__isnull=False).values_list('employee__user__telegram_id', flat=True)


def orm_get_all_employee_telegram_id():
    return Employee.objects.filter(Q(director__isnull=True) | Q(director__is_active=False)).select_related('user').values_list('user__telegram_id', flat=True).exclude(user__telegram_id__isnull=True)


def orm_get_director_division_id(user_id):
    div = Employee.objects.filter(user__telegram_id=user_id).values_list('division_id', flat=True)[0]
    return div


def orm_get_division_employees(division_id):
    employee = Employee.objects.filter(division_id=division_id)
    return employee


def orm_get_employee_full_name(employee_id, abbreviated: bool = False):
    employee = Employee.objects.get(id=employee_id)
    if abbreviated:
        return f'{employee.surname} {employee.name[0:1]}. {employee.patronymic[0:1]}.'
    else:
        return f'{employee.surname} {employee.name} {employee.patronymic}'


def orm_get_working_location():
    return WorkingLocation.objects.all()

# region Questions
def orm_get_division_questions(division_id, status):
    q = Question.objects.filter(initiator__division=division_id, status=status)
    return q


def orm_get_question_employee(question_id):
    employee = Question.objects.select_related('initiator').get(id=question_id).initiator
    return employee


def orm_change_question_status(question_id, status):
    q = Question.objects.get(id=question_id)
    q.status = status
    q.save()


def orm_change_question_answer(question_id, answer):
    q = Question.objects.get(id=question_id)
    q.answer = answer
    q.save()


# endregion Questions


# region WorkSchedules
def orm_get_work_schedules(employee_id):
    w_sch = WorkSchedule.objects.select_related('location').filter(employee=employee_id, is_deleted=False).values('id',
                                                                                                                  'employee_id',
                                                                                                                  'day',
                                                                                                                  'start_time',
                                                                                                                  'end_time',
                                                                                                                  'location__location_name',
                                                                                                                  )
    return w_sch


def orm_get_work_schedule(work_schedule_id):
    w_sch = WorkSchedule.objects.get(id=work_schedule_id, is_deleted=False)
    location = WorkingLocation.objects.get(id=w_sch.location_id)
    return w_sch, location


def orm_delete_work_schedule(work_schedule_id):
    WorkSchedule.objects.get(id=work_schedule_id).delete()


def orm_change_work_schedule_day(work_schedule_id, changed_day):
    WorkSchedule.objects.filter(id=work_schedule_id).update(day=changed_day)


def orm_change_work_schedule_location(work_schedule_id, location_id):
    WorkSchedule.objects.filter(id=work_schedule_id).update(location_id=location_id)


def orm_change_work_schedule_time_start(work_schedule_id, start_time):
    WorkSchedule.objects.filter(id=work_schedule_id).update(start_time=start_time)


def orm_change_work_schedule_time_end(work_schedule_id, end_time):
    WorkSchedule.objects.filter(id=work_schedule_id).update(end_time=end_time)


def orm_add_work_schedule(day, start_time, end_time, location_id, employee_id):
    WorkSchedule.objects.create(day=day, start_time=start_time, end_time=end_time, location_id=location_id, employee_id=employee_id)


# Получение списка "изменения в рабочем графике" по division_id
def orm_get_changes_work_schedule(division_id, is_new: bool = True):
    if is_new:
        return ChangeWorkSchedule.objects.select_related('employee').filter(employee__division_id=division_id, is_agreed=None, rejection_reason=None)
    else:
        return ChangeWorkSchedule.objects.select_related('employee').filter(employee__division_id=division_id, is_agreed__isnull=False)


def orm_get_access_changes_work_schedule(employee_id):
    return ChangeWorkSchedule.objects.filter(employee_id=employee_id, is_agreed=True).order_by('day')

# Получение division_id по id change_work_schedule
def orm_get_division_change_work_schedule(change_work_schedule_id):
    return ChangeWorkSchedule.objects.select_related('employee__division').get(id=change_work_schedule_id).employee.division.id


def orm_get_change_work_schedule(id):
    return ChangeWorkSchedule.objects.get(id=id)


def orm_change_change_work_schedule(change_work_schedule_id, is_agreed: bool = None, rejection_reason: str = None):
    ChangeWorkSchedule.objects.filter(id=change_work_schedule_id).update(is_agreed=is_agreed, rejection_reason=rejection_reason)





# endregion WorkSchedules
