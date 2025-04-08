from django.db import models
from django.conf import settings
from products.models import Product
    
class Chat(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='chats')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_chats')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('seller', 'buyer')  # Har bir chatda faqat bitta sotuvchi va xaridor bo'lishi kerak
        ordering = ['-created_at']  # Yangi chatlar yuqorida ko‘rsatiladi   
        

    def __str__(self):
        return f"Chat for {self.product.name} between {self.seller.email} and {self.buyer.email}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)  # Matn ixtiyoriy bo‘ladi, chunki rasm yuborish ham mumkin
    voice = models.FileField(upload_to='chat_voices/', null=True, blank=True)   # Ovozni yuborish uchun maydon
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')  # Javob xabari
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.email} in {self.chat}"
    
class MessageImage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='chat_images/')

    def __str__(self):
        return f"Image for message {self.message.id}"
    

class Reaction(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10)  # Masalan, "❤️", "👍", "😂"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')  # Har bir foydalanuvchi xabarga faqat bitta reaktsiya qo‘ya oladi

    def __str__(self):
        return f"{self.user.email} reacted {self.reaction} to {self.message}"