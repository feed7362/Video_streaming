from typing import Any, Dict, List, Optional

from elasticsearch import ApiError, AsyncElasticsearch, TransportError

from src.errors.search import VideoHintsError, VideoSearchError


class SearchService:
    def __init__(self, es: AsyncElasticsearch):
        self.es = es

    async def get_video_hints(self, query: str, size: int = 10) -> List[str]:
        try:
            suggest_query = {
                "video-suggest": {
                    "prefix": query,
                    "completion": {
                        "field": "suggest_name",
                        "skip_duplicates": True,
                        "fuzzy": {"fuzziness": 1},
                        "size": size,
                    },
                }
            }

            response = await self.es.search(index="videos", suggest=suggest_query)

            options = response["suggest"]["video-suggest"][0]["options"]
            hints = [
                opt.get("_source", {}).get("name") or opt.get("text") for opt in options
            ]
            return [h for h in hints if h]

        except (ApiError, TransportError, KeyError, IndexError) as ex:
            raise VideoHintsError(query=query, cause=ex)

    async def search_video(
        self,
        query: str,
        query_vector: Optional[List[float]] = None,
        category: Optional[str] = None,
        min_views: Optional[int] = None,
        max_views: Optional[int] = None,
        limit: int = 10,
        smart_search: bool = False,
        has_description: bool = False,
    ) -> dict:
        try:
            # ─── Build the base text query ────────────────────────────────
            must_query = {
                "multi_match": {
                    "query": query,
                    "fields": ["name^3", "description^2"],
                    "fuzziness": "AUTO",
                }
            }

            filters: List[Dict[str, Any]] = []

            if category:
                filters.append({"term": {"category": category}})
            if min_views is not None or max_views is not None:
                range_filter: Dict[str, Any] = {"range": {"views": {}}}
                if min_views is not None:
                    range_filter["range"]["views"]["gte"] = min_views
                if max_views is not None:
                    range_filter["range"]["views"]["lte"] = max_views
                filters.append(range_filter)
            if has_description:
                filters.append({"exists": {"field": "description"}})

            text_query = {"bool": {"must": [must_query], "filter": filters}}

            # ─── Text-only search ───────────────────────────────────────
            if not smart_search or not query_vector:
                result = await self.es.search(
                    index="videos", query=text_query, size=limit
                )
                return {
                    "hits": [
                        {"id": hit["_id"], **hit["_source"], "score": hit.get("_score")}
                        for hit in result["hits"]["hits"]
                    ]
                }

            # ─── Hybrid vector + text search ────────────────────────────
            result = await self.es.search(
                index="videos",
                knn={
                    "field": "video_embedding",
                    "query_vector": query_vector,
                    "k": limit,
                    "num_candidates": 100,
                },
                _source=["id", "name", "description", "views", "category"],
                query=text_query,
                rank={"rrf": {}},
            )

            return {
                "hits": [
                    {**hit["_source"], "score": hit.get("_score")}
                    for hit in result["hits"]["hits"]
                ]
            }
        except (ApiError, TransportError, KeyError, IndexError) as ex:
            raise VideoSearchError(query=query, cause=ex)
