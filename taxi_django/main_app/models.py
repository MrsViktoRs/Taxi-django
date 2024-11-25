from django.db import models

class Users(models.Model):
    chat_id = models.BigIntegerField()
    name = models.CharField(max_length=255, null=True)
    surname = models.CharField(max_length=255, null=True)
    patronymic = models.CharField(max_length=255, null=True, blank=True)
    phone = models.BigIntegerField(null=True)
    address = models.CharField(max_length=255, null=True)
    permission_number = models.CharField(max_length=255, null=True)
    auth_status = models.BooleanField(default=False)
    res_status = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.name} {self.surname}"


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
