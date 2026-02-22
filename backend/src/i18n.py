import gettext
from _contextvars import ContextVar
from datetime import datetime
from functools import lru_cache
from typing import Callable

import pytz
from babel.dates import format_date, format_datetime, format_time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# ----------------------
# Constants / ContextVars
# ----------------------
LOCALES_DIR = "src/translations"
DEFAULT_LANG = "en"

# For string translations
translation_ctx: ContextVar[gettext.NullTranslations] = ContextVar("translation_ctx")

# For datetime localization
locale_ctx: ContextVar[str] = ContextVar("locale_ctx")
timezone_ctx: ContextVar[str] = ContextVar("timezone_ctx", default="UTC")


def set_locale(locale: str):
    """Set the current request locale."""
    locale_ctx.set(locale)


def set_timezone(tz: str):
    """Set the current request timezone."""
    timezone_ctx.set(tz)


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

        tzname = request.headers.get("X-Timezone", "UTC")

        # Set context variables
        token_trans = translation_ctx.set(translation)
        token_locale = locale_ctx.set(lang)
        token_tz = timezone_ctx.set(tzname)

        try:
            return await call_next(request)
        finally:
            translation_ctx.reset(token_trans)
            locale_ctx.reset(token_locale)
            timezone_ctx.reset(token_tz)


def _(message: str) -> str:
    translation = translation_ctx.get(None)
    if translation is None:
        return message
    return translation.gettext(message)


def ldt(
    dt: datetime,
    format_type: str = "datetime",
    tzinfo: str | None = None,
    pattern: str | None = None,
) -> str:
    """
    Format a datetime object into a localized string representation based on the given format type or pattern.

    This function allows flexible formatting of datetime objects according to specified
    locale, timezone information, and either a predefined format type or a custom pattern.
    It defaults to rendering a full datetime representation if no specific type or pattern is provided.

    Parameters:
        dt (datetime): The datetime object to be formatted. Must be a valid datetime instance.
        format_type (str): Specifies the formatting type. Options include 'datetime', 'date',
            or 'time'. Defaults to 'datetime'.
        tzinfo (str | None): The timezone into which the datetime is to be converted.
            If not provided, it defaults to 'UTC'.
        pattern (str | None): Custom formatting pattern following localization rules.
            Overrides format_type when provided.
    """
    if dt is None:
        return ""

    # Get locale and timezone from context
    locale = locale_ctx.get("en")  # fallback to English
    tzname = tzinfo or timezone_ctx.get("UTC")

    # Convert datetime to the target timezone
    tz = pytz.timezone(tzname)
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    dt_local = dt.astimezone(tz)

    # Format based on type
    if pattern:
        return format_datetime(dt_local, format=pattern, locale=locale)
    elif format_type == "date":
        return format_date(dt_local, locale=locale)
    elif format_type == "time":
        return format_time(dt_local, locale=locale)
    else:
        return format_datetime(dt_local, locale=locale)


# pybabel extract -o ./translations/messages.pot .

# pybabel init -i ./translations/messages.pot -d ./translations -l en
# pybabel init -i ./translations/messages.pot -d ./translations -l uk

# pybabel compile -d ./translations
