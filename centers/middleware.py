import threading

_thread_local = threading.local()

SUPPORTED_LANGUAGES = ('uz', 'ru', 'en')
DEFAULT_LANGUAGE = 'uz'


def get_current_language():
    return getattr(_thread_local, 'language', DEFAULT_LANGUAGE)


class LanguageMiddleware:
    """
    Accept-Language headeridan tilni aniqlaydi.
    Qo'llab-quvvatlanadigan tillar: uz, ru, en
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.headers.get('Accept-Language', DEFAULT_LANGUAGE)[:2].lower()
        if lang not in SUPPORTED_LANGUAGES:
            lang = DEFAULT_LANGUAGE
        _thread_local.language = lang
        request.language = lang
        response = self.get_response(request)
        response['Content-Language'] = lang
        return response
