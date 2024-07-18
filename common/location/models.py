from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    """
    Model to store country related information
    """
    name = models.CharField(_('Country Name'), max_length=50, unique=True)

    def __str__(self):
        return f"{self.pk}, {self.name}"

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('name', )


class State(models.Model):
    """
    Model to store state related information
    """
    name = models.CharField(_('State Name'), max_length=100)

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')

    def __str__(self):
        return f"{self.pk}, {self.name}"

    class Meta:
        ordering = ('name', )


class City(models.Model):
    """
    Model to store city related information
    """
    name = models.CharField(_('City Name'), max_length=100)

    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return f"{self.pk}, {self.name}"

    class Meta:
        verbose_name_plural = 'Cities'
        ordering = ('name', )
