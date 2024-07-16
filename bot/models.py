from django.db import models
import datetime

from tgbot.utils.dictionary import get_days_dict, get_types_of_change_w_sch_dict, get_frequency_reminder_dict


class TGUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True, verbose_name='id Telegram', blank=True, null=True)
    username = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return f'Пользователь: {self.username} {self.telegram_id}'


class Division(models.Model):
    name = models.CharField(max_length=50)
    higher_division = models.ForeignKey(to='bot.Division', on_delete=models.CASCADE, blank=True, null=True)
    report_chat_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.name}'


class Employee(models.Model):
    user = models.OneToOneField(to='bot.TGUser', on_delete=models.CASCADE)
    surname = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    birth_date = models.DateField()
    division = models.ForeignKey(to='bot.Division', on_delete=models.CASCADE)

    def __str__(self):
        return f'Сотрудник: {self.surname} {self.name} {self.patronymic}'


class Director(models.Model):
    employee = models.OneToOneField(to='bot.Employee', on_delete=models.CASCADE)
    phone_num = models.CharField(max_length=50)
    deputy_end = models.DateTimeField(blank=True, null=True)
    is_deputy = models.BooleanField()
    is_active = models.BooleanField(default=True)


class WorkingLocation(models.Model):
    location_name = models.CharField(max_length=100, default='')


class WorkSchedule(models.Model):
    employee = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=get_days_dict(), default='MON')
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.ForeignKey(to='bot.WorkingLocation', on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)


class ChangeWorkSchedule(models.Model):
    employee = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE)
    day = models.DateField()
    type = models.CharField(max_length=10, choices=get_types_of_change_w_sch_dict(), default='Distant')
    reason = models.CharField(max_length=150)
    is_agreed = models.BooleanField(default=False, blank=True, null=True)
    rejection_reason = models.CharField(max_length=150, blank=True, null=True)


class Medical(models.Model):
    employee = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE)
    is_official = models.BooleanField(default=False)
    begin = models.DateTimeField()
    end = models.DateTimeField()
    description = models.CharField(max_length=250)
    is_agreed = models.BooleanField(default=False)
    rejection_reason = models.CharField(max_length=150, blank=True, null=True)


class Vacation(models.Model):
    employee = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE)
    YEAR_CHOICES = []
    for r in range(datetime.datetime.now().year, (datetime.datetime.now().year + 3)):
        YEAR_CHOICES.append((r, f'{r} год'))

    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    begin = models.DateField()
    end = models.DateField()
    previos = models.ForeignKey(to='bot.Vacation', on_delete=models.CASCADE, blank=True, null=True)
    change_reason = models.CharField(max_length=150)
    is_agreed = models.BooleanField(default=False)
    rejection_reason = models.CharField(max_length=150, blank=True, null=True)


class Notification(models.Model):
    initiator = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    publication_date = models.DateTimeField(default=datetime.datetime.now())
    is_sent = models.BooleanField(default=False)
    is_notify = models.BooleanField(default=True)
    repeat_count = models.IntegerField(default=0)
    repeat_period = models.IntegerField(choices=get_frequency_reminder_dict(), default=1)


class Activity(models.Model):
    initiator = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    begin_date = models.DateTimeField()
    deadline_date = models.DateTimeField()
    mandatory = models.CharField(max_length=50)
    repeat_period = models.IntegerField(choices=get_frequency_reminder_dict(), default=1)
    is_apply_director = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'


class ActivityParticipant(models.Model):
    activity = models.ForeignKey(to='bot.Activity', on_delete=models.CASCADE)
    employee = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE)
    is_took_part = models.BooleanField(default=False)
    fixation_date = models.DateTimeField(blank=True, null=True)


class Discussion(models.Model):
    carrying = models.CharField(max_length=100)
    issue = models.CharField(max_length=150)
    short_description = models.CharField(max_length=200)
    short_result = models.CharField(max_length=200)
    participants = models.ManyToManyField(to='bot.Employee')
    remind_minute = models.IntegerField()

    def __str__(self):
        return f'{self.carrying}'


class DiscussionParticipant(models.Model):
    discussion = models.ForeignKey(to='bot.Discussion', on_delete=models.CASCADE)
    participant = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE, related_name="discussion_participant")
    initiator = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE, related_name="discussion_initiator")
    is_cant_on_main_time = models.BooleanField(default=False)


class VotingForTime(models.Model):
    discussion = models.ForeignKey(to='bot.Discussion', on_delete=models.CASCADE)
    employee = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE)
    new_datetime = models.DateTimeField()
    agree = models.IntegerField()
    disagree = models.IntegerField()
    total = models.IntegerField()


QUESTION_STATUS = (
        ("new", 'Новый'),
        ("answered", 'С ответом/Решенный'),
    )


class Question(models.Model):
    initiator = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    question = models.CharField(max_length=300)
    status = models.CharField(choices=QUESTION_STATUS, default="new")
    answer = models.CharField(max_length=300, blank=True, null=True)
    criticality_answer = models.IntegerField()
    repeat_count = models.IntegerField(default=0)
    repeat_period = models.IntegerField(choices=get_frequency_reminder_dict(), default=1)


class Notify(models.Model):
    employee = models.ForeignKey(to='bot.Employee', on_delete=models.CASCADE)
    notify_type = models.CharField(max_length=75)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
