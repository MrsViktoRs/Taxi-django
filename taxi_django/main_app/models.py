from django.db import models
from django.db.models import CharField, ForeignKey
from django.contrib.auth.hashers import check_password as django_check_password


class Tariffs(models.Model):
    serviceid = models.CharField(null=True, blank=True)
    name = models.CharField(null=True, blank=True)
    is_enabled = models.BooleanField(null=True, blank=True)


class Users(models.Model):
    chat_id = models.BigIntegerField()
    name = models.CharField(max_length=255, null=True)
    surname = models.CharField(max_length=255, null=True)
    patronymic = models.CharField(max_length=255, null=True, blank=True)
    phone = models.BigIntegerField(null=True)
    permission_number = models.CharField(max_length=255, null=True)
    active_stocks = models.CharField(max_length=500, null=True, blank=True) # нужно записывать вкаких акциях он участвует
    auth_status = models.BooleanField(default=False)
    res_status = models.BooleanField(default=False)
    self_worker = models.BooleanField(null=True, blank=True)
    fleetid = models.CharField(max_length=255, null=True, blank=True)
    card_number = models.CharField(max_length=300, null=True, blank=True)
    tariff = models.ForeignKey(Tariffs, on_delete=models.CASCADE, related_name='tariffs', null=True, blank=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.name} {self.surname}"


class UserCredentials(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)

    def check_password(self, raw_password):
        return django_check_password(raw_password, self.password)

    class Meta:
        verbose_name = "User Credentials"
        verbose_name_plural = "User Credentials"


class Role(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='roles', null=True, blank=True)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name


class Cars(models.Model):
    model = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    gos_number = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='cars', null=True, blank=True)

    class Meta:
        verbose_name = "Car"
        verbose_name_plural = "Cars"

    def __str__(self):
        return f"{self.model} {self.gos_number}"


class WorkingShifts(models.Model):
    work_date = models.DateField(null=True, blank=True)
    begin_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    all_time = models.DurationField(null=True, blank=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='working_shifts', null=True, blank=True)

    class Meta:
        verbose_name = "Working Shift"
        verbose_name_plural = "Working Shifts"

    def __str__(self):
        return f"Shift for {self.user.name} on {self.work_date}"


class Shares(models.Model):
    name = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='shares', null=True, blank=True)

    class Meta:
        verbose_name = "Share"
        verbose_name_plural = "Shares"

    def __str__(self):
        return f"Share for {self.name}"


class RefKey(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    key = models.CharField(unique=True, null=True, blank=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='ref_keys', blank=True, null=True)
    count_invite = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Reference Key"
        verbose_name_plural = "Reference Keys"

    def __str__(self):
        return f"{self.name} - {self.key}"


class RefUsers(models.Model):
    who_invited = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='invited_users', null=True, blank=True)
    visiting_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='visitors', null=True, blank=True)
    dt = models.DateField()

    class Meta:
        verbose_name = "Referral User"
        verbose_name_plural = "Referral Users"

    def __str__(self):
        return f"{self.visiting_user.name} invited by {self.who_invited.name}"


class Stocks(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    on_text = models.CharField(max_length=2048, null=True, blank=True)
    off_text = models.CharField(max_length=2048, null=True, blank=True)
    status = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        verbose_name = "Stocks"
        verbose_name_plural = "Stocks"


class Appeals(models.Model):
    message = models.CharField(max_length=2048) # текст сообщения
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='appeals_mess', null=True, blank=True) # от кого сообщения
    dt = models.DateTimeField(auto_now_add=True) # дата
    status = models.BooleanField(default=True) # статус активности
    role = models.CharField(max_length=255) # тут либо appeal(обращение) либо help(помощь) потом возмодно добавим orders...

    class Meta:
        verbose_name = "Appeals"
        verbose_name_plural = "Appeals"


class Messages(models.Model):
    message_id = CharField(null=True, blank=True)
    user = ForeignKey(Users, on_delete=models.CASCADE, related_name='user_message')

    class Meta:
        verbose_name = 'Messages'
        verbose_name_plural = "Messages"


class YourTaxiPark(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='your_taxipark', null=True, blank=True)
    count_money = models.IntegerField(null=True, blank=True)
    count_invite = models.IntegerField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

class VeryGoodDriver(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='VeryGoodDriver')
    count_drive = models.IntegerField()
    date = models.DateField()

# для отправки сообщений
class ActiveMessage (models.Model):
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    whom = models.CharField(max_length=300)
    message = CharField(max_length=2048)
