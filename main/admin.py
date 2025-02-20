from django.contrib import admin
from .models import Banner, Craftsmanship, Craftsmanshiplist, OurTeam, SocialMediaLink, AboutUs, FeatureItem, CraftsmanshipFeature
# Register your models here.

class FeatureItemInline(admin.TabularInline):
    model = FeatureItem
    extra = 1

class CraftsmanshipFeatureInline(admin.TabularInline):
    model = CraftsmanshipFeature
    extra = 1
    show_change_link = True

class BannerAdmin(admin.ModelAdmin):
    list_display = ['name', 'img', 'video', 'text', 'author']

class OurTeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'text', 'img', 'profession'] 

class CraftsmanshipAdmin(admin.ModelAdmin):
    list_display = ['title', 'text', 'img']

class CraftsmanshipListAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'text', 'img'] 
    inlines = [CraftsmanshipFeatureInline]

class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'icon']

class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['title', 'mission', 'history']

# Craftsmanship Feature Admin Paneli (yangi)
class CraftsmanshipFeatureAdmin(admin.ModelAdmin):
    list_display = ['craftsmanship', 'key']
    inlines = [FeatureItemInline] 

admin.site.register(Craftsmanship, CraftsmanshipAdmin)
admin.site.register(CraftsmanshipFeature, CraftsmanshipFeatureAdmin)
admin.site.register(Craftsmanshiplist, CraftsmanshipListAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(OurTeam, OurTeamAdmin)
admin.site.register(SocialMediaLink, SocialMediaLinkAdmin)
admin.site.register(AboutUs, AboutUsAdmin)



