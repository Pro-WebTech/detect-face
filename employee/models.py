from django.db import models

# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=50)
    emp_image = models.FileField(upload_to='images/')

class Client(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=255, default='c4ca4238a0b923820dcc509a6f75849b')

    class Meta:
        db_table = 'employee_client'