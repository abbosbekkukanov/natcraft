from django.shortcuts import redirect

class BypassAuthForSwaggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # /swagger/ va /redoc/ uchun autentifikatsiyani chetlab o'tish
        if request.path.startswith('/swagger/') or request.path.startswith('/redoc/'):
            return self.get_response(request)
        return self.get_response(request)