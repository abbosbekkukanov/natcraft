from django.contrib import admin
from .models import Workshop, WorkshopImage360, WorkshopRating

# WorkshopImage360 uchun Inline model
class WorkshopImage360Inline(admin.TabularInline):
    model = WorkshopImage360
    extra = 1  # Bo'sh qatorlar soni (foydalanuvchi qo'shishi uchun)

# WorkshopRating uchun Inline model
class WorkshopRatingInline(admin.TabularInline):
    model = WorkshopRating
    extra = 0  # Baholar avtomatik qo'shilmaydi, faqat mavjudlar ko'rsatiladi
    readonly_fields = ('user', 'rating', 'created_at')  # Ushbu maydonlarni faqat o'qish uchun qilamiz

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'address', 'average_rating', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'address', 'user__username')
    inlines = [WorkshopImage360Inline, WorkshopRatingInline]

    # O'rtacha reytingni ko'rsatish uchun metod
    def average_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings.exists():
            return round(sum(rating.rating for rating in ratings) / ratings.count(), 1)
        return 0
    average_rating.short_description = "O'rtacha reyting"

@admin.register(WorkshopImage360)
class WorkshopImage360Admin(admin.ModelAdmin):
    list_display = ('workshop', 'image_360')
    list_filter = ('workshop',)
    search_fields = ('workshop__name',)

@admin.register(WorkshopRating)
class WorkshopRatingAdmin(admin.ModelAdmin):
    list_display = ('workshop', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('workshop__name', 'user__username')