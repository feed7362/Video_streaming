from src.schemas.metric import VIDEO_SEARCH_TOTAL


def video_search_metrics(smart_search: bool, category: str | None = None):
    VIDEO_SEARCH_TOTAL.labels(
        smart_search=str(smart_search), category=category or "none"
    ).inc()
    return True
