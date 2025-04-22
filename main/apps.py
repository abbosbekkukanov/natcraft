from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language_info

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        if not hasattr(get_language_info, 'cache'):
            get_language_info.cache = {}

        get_language_info.cache['kaa'] = {
            'code': 'kaa',
            'name': 'Qoraqalpoq',
            'name_local': 'Qaraqalpaq',
            'bidi': False,
            'name_translated': _('Qoraqalpoq'),
        }