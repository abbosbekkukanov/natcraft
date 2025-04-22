from django.conf.locale import LANG_INFO

def add_custom_languages():
    LANG_INFO.update({
        'kaa': {
            'bidi': False,
            'code': 'kaa',
            'name': 'Qoraqalpoq',
            'name_local': 'Qaraqalpaq',
        },
    })
