from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from .models import Banner, Craftsmanship, Craftsmanshiplist, OurTeam, SocialMediaLink, AboutUs, FeatureItem, CraftsmanshipFeature

# Inline modellar uchun TranslationTabularInline ishlatamiz
class FeatureItemInline(TranslationTabularInline):
    model = FeatureItem
    extra = 1

class CraftsmanshipFeatureInline(TranslationTabularInline):
    model = CraftsmanshipFeature
    extra = 1
    show_change_link = True

@admin.register(Banner)
class BannerAdmin(TranslationAdmin):
    list_display = ['name', 'author', 'created']
    search_fields = ['name_uz', 'name_en', 'name_ru', 'name_qq', 'text_uz', 'author_uz']

@admin.register(OurTeam)
class OurTeamAdmin(TranslationAdmin):
    list_display = ['name', 'profession']
    search_fields = ['name_uz', 'name_en', 'name_ru', 'name_qq', 'text_uz', 'profession_uz']

@admin.register(Craftsmanship)
class CraftsmanshipAdmin(TranslationAdmin):
    list_display = ['title']
    search_fields = ['title_uz', 'title_en', 'title_ru', 'title_qq', 'text_uz']

@admin.register(Craftsmanshiplist)
class CraftsmanshiplistAdmin(TranslationAdmin):
    list_display = ['title', 'category']
    search_fields = ['title_uz', 'title_en', 'title_ru', 'title_qq', 'text_uz']
    inlines = [CraftsmanshipFeatureInline]

@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(TranslationAdmin):
    list_display = ['name', 'url']
    search_fields = ['name_uz', 'name_en', 'name_ru', 'name_qq']

@admin.register(AboutUs)
class AboutUsAdmin(TranslationAdmin):
    list_display = ['title']
    search_fields = ['title_uz', 'title_en', 'title_ru', 'title_qq', 'mission_uz', 'history_uz']

@admin.register(CraftsmanshipFeature)
class CraftsmanshipFeatureAdmin(TranslationAdmin):
    list_display = ['craftsmanship', 'key']
    search_fields = ['key_uz', 'key_en', 'key_ru', 'key_qq']
    inlines = [FeatureItemInline]