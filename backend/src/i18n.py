import gettext
from _contextvars import ContextVar
from functools import lru_cache
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

LOCALES_DIR = "src/translations"
DEFAULT_LANG = "en"

translation_ctx: ContextVar[gettext.NullTranslations] = ContextVar("translation_ctx")


def get_language(request: Request) -> str:
    header = request.headers.get("accept-language", DEFAULT_LANG)
    return header.split(",")[0].split("-")[0]


@lru_cache(maxsize=32)
def get_translation(lang: str):
    return gettext.translation(
        "messages",
        localedir=LOCALES_DIR,
        languages=[lang],
        fallback=True,
    )


class InternationalizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Determine language
        lang = get_language(request)
        translation = get_translation(lang)

        # Set context variables
        token_trans = translation_ctx.set(translation)

        try:
            return await call_next(request)
        finally:
            translation_ctx.reset(token_trans)


def _(message: str) -> str:
    translation = translation_ctx.get(None)
    if translation is None:
        return message
    return translation.gettext(message)


# pybabel extract -o ./translations/messages.pot .

# pybabel init -i ./translations/messages.pot -d ./translations -l en
# pybabel init -i ./translations/messages.pot -d ./translations -l uk

# pybabel compile -d ./translations
