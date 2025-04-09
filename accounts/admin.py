from django.contrib import admin
from .models import CustomUser, UserProfile, Profession, EmailConfirmation, PasswordResetCode

# Custom User Admin
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'is_active', 'is_verified', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'is_verified')
    list_filter = ('is_active', 'is_verified', 'is_staff', 'date_joined')
    ordering = ('-date_joined',)

admin.site.register(CustomUser, CustomUserAdmin)

# Profession Admin
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)

admin.site.register(Profession, ProfessionAdmin)

# UserProfile Admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profession', 'bio', 'phone_number', 'experience', 'mentees', 'award', 'created_at', 'updated_at')
    search_fields = ('user__email', 'bio', 'phone_number')
    list_filter = ('profession', 'experience', 'mentees')
    ordering = ('-created_at',)

admin.site.register(UserProfile, UserProfileAdmin)

# EmailConfirmation Admin
class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('email', 'confirmation_code', 'created_at', 'is_confirmed')
    search_fields = ('email',)
    list_filter = ('is_confirmed',)
    ordering = ('-created_at',)

admin.site.register(EmailConfirmation, EmailConfirmationAdmin)

# PasswordResetCode Admin
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__email', 'code')
    ordering = ('-created_at',)

admin.site.register(PasswordResetCode, PasswordResetCodeAdmin)
