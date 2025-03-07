from django.contrib import admin
from .models import Workshop

class WorkshopAdmin(admin.ModelAdmin):
    # Ko'rsatiladigan ustunlar ro'yxati
    list_display = ('name', 'user', 'address', 'created_at', 'updated_at', 'image_360_preview')
    
    # Qidiruv panelida qaysi maydonlarda qidirish mumkinligini belgilash
    search_fields = ('name', 'description', 'address')
    
    # Workshop yaratishda ko'rsatiladigan maydonlar
    fields = ('user', 'name', 'description', 'image_360', 'address')
    
    # Tasvirlarni boshqarish uchun maxsus metod (preview uchun)
    def image_360_preview(self, obj):
        if obj.image_360:
            return f'<img src="{obj.image_360.url}" width="100" height="100" />'
        return 'No Image'
    image_360_preview.allow_tags = True  # HTML tasvirini ko'rsatish imkoniyati
    image_360_preview.short_description = '360 Image Preview'

# Admin panelida Workshop modelini ro'yxatga olish
admin.site.register(Workshop, WorkshopAdmin)
