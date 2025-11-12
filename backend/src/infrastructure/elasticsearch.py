from elasticsearch import AsyncElasticsearch

from ..config import get_elastic_settings

settings = get_elastic_settings()

es_client = AsyncElasticsearch(
    hosts=[settings.ELASTIC_HOST],
    basic_auth=("elastic", settings.ELASTIC_PASSWORD),
    http_compress=True,
    request_timeout=10,
    max_retries=5,
    retry_on_timeout=True,
)


async def get_es_client() -> AsyncElasticsearch:
    """Provide the shared ElasticSearch instance for dependency injection."""

    return es_client
