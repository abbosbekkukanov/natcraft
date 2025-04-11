from django.contrib import admin
from .models import Chat, Message, MessageImage, Reaction


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'seller', 'buyer', 'created_at')
    search_fields = ('product__name', 'seller__email', 'buyer__email')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


class MessageImageInline(admin.TabularInline):
    model = MessageImage
    extra = 0


class ReactionInline(admin.TabularInline):
    model = Reaction
    extra = 0


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'short_content', 'is_read', 'created_at')
    list_display_links = ('id', 'chat', 'short_content')
    search_fields = ('sender__email', 'chat__product__name', 'content')
    list_filter = ('is_read', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageImageInline, ReactionInline]

    def short_content(self, obj):
        return (obj.content[:50] + '...') if obj.content else '(No text)'
    short_content.short_description = 'Content'


@admin.register(MessageImage)
class MessageImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 100px;" />'
        return "(No image)"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'reaction', 'created_at')
    search_fields = ('user__email', 'reaction', 'message__content')
    list_filter = ('reaction', 'created_at')
    readonly_fields = ('created_at',)
