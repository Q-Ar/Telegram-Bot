from django.contrib import admin

# Register your models here.
from .models import Employee, WorkSchedule, TGUser, Division, WorkingGroup, Director, ChangeWorkSchedule, Medical, Vacation, Notification, Activity, ActivityParticipant, Discussion, DiscussionParticipant, VotingForTime


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'surname', 'name', 'patronymic', 'birth_date']


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ['employee', 'deputy_end', 'is_deputy', 'is_active', 'phone_num']


@admin.register(Division)
class AdminDivision(admin.ModelAdmin):
    list_display = ['name', 'higher_division', 'report_chat_id']


@admin.register(Activity)
class AdminActivity(admin.ModelAdmin):
    list_display = ['name', 'description', 'begin_date', 'deadline_date', 'mandatory']


@admin.register(TGUser)
class AdminTGUser(admin.ModelAdmin):
    list_display = ['telegram_id', 'username']


@admin.register(WorkSchedule)
class AdminWorkSchedule(admin.ModelAdmin):
    list_display = ['employee', 'day', 'start_time', 'end_time', 'location']


@admin.register(WorkingGroup)
class AdminWorkingGroup(admin.ModelAdmin):
    list_display = ['name', 'description', 'division']


@admin.register(ChangeWorkSchedule)
class AdminChangeWorkSchedule(admin.ModelAdmin):
    list_display = ['employee', 'day', 'type', 'is_agreed']


@admin.register(Medical)
class AdminMedical(admin.ModelAdmin):
    list_display = ['employee', 'begin', 'end', 'description', 'is_agreed']


@admin.register(Vacation)
class AdminVacation(admin.ModelAdmin):
    list_display = ['employee', 'year', 'begin', 'end', 'is_agreed']


@admin.register(Notification)
class AdminNotification(admin.ModelAdmin):
    list_display = ['name', 'description', 'publication_date', 'is_sent', 'repeat_count', 'repeat_period']


@admin.register(ActivityParticipant)
class AdminActivityParticipant(admin.ModelAdmin):
    list_display = ['employee', 'activity', 'fixation_date', 'is_took_part']


@admin.register(Discussion)
class AdminDiscussion(admin.ModelAdmin):
    list_display = ['carrying', 'issue', 'remind_minute', 'short_result']


@admin.register(DiscussionParticipant)
class AdminDiscussionParticipant(admin.ModelAdmin):
    list_display = ['discussion', 'initiator', 'participant', 'is_cant_on_main_time']


@admin.register(VotingForTime)
class AdminVotingForTime(admin.ModelAdmin):
    list_display = ['discussion', 'employee', 'new_datetime', 'agree', 'disagree', 'total']