from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import logging
logger = logging.getLogger(__name__)

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except Exception:
        return AnonymousUser()

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        token = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break
        
        logger.info(f"WebSocket ulanish: query_string={query_string}, token={token}")
        scope['user'] = await get_user_from_token(token) if token else AnonymousUser()
        if scope['user'].is_anonymous:
            logger.error(f"Autentifikatsiya muvaffaqiyatsiz: token={token}")
        else:
            logger.info(f"Foydalanuvchi autentifikatsiya qilindi: user={scope['user'].email}, id={scope['user'].id}")
        return await self.inner(scope, receive, send)