from django.db import models
from django.utils.timezone import now


class CarMake(models.Model):

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=320)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    SEDAN = 'sedan'
    SUV = 'suv'
    WAGON = 'wagon'
    CAR_TYPES = [
        (SEDAN, 'Sedan'),
        (SUV, 'Suv'),
        (WAGON, 'Wagon')
    ]

    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    dealer_id = models.IntegerField()
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CAR_TYPES)
    year = models.DateField()

    def __str__(self):
        return self.name
