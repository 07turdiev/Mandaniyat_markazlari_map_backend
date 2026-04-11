import threading

_thread_local = threading.local()

SUPPORTED_LANGUAGES = ('uz', 'uz-cyrl', 'ru')
DEFAULT_LANGUAGE = 'uz'


def get_current_language():
    return getattr(_thread_local, 'language', DEFAULT_LANGUAGE)


class LanguageMiddleware:
    """
    Accept-Language headeridan tilni aniqlaydi.
    Qo'llab-quvvatlanadigan tillar: uz, uz-cyrl, ru, en
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang_header = request.headers.get('Accept-Language', DEFAULT_LANGUAGE).lower().strip()
        # uz-cyrl ni to'liq qo'llab-quvvatlash
        if lang_header.startswith('uz-cyrl'):
            lang = 'uz-cyrl'
        else:
            lang = lang_header[:2]
        if lang not in SUPPORTED_LANGUAGES:
            lang = DEFAULT_LANGUAGE
        _thread_local.language = lang
        request.language = lang
        response = self.get_response(request)
        response['Content-Language'] = lang
        return response
