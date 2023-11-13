'''
Django application configuration for the CityGrid app.

This module defines the configuration for the CityGrid app using the AppConfig
class from the django.apps module. It specifies the default auto field,
the app name, and the verbose name for better human-readable representation
in the Django admin.

Attributes:
    default_auto_field (str): The default auto field for models within the app,
    set to 'django.db.models.BigAutoField'.
    name (str): The name of the app, set to 'city_grid'.
    verbose_name (str): The human-readable name of the app, set to
    'Городская сетка' for better clarity in the Django admin.
'''

from django.apps import AppConfig


class CityGridConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'city_grid'
    verbose_name = 'Городская сетка'
