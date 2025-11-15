"""SearxNG + Redis client for Hermes"""

import httpx
import redis.asyncio as redis
from typing import List, Optional
from loguru import logger
import hashlib
import json

from hermes_cli.models.search import SearchResponse, SearchResult


class SearxNGClient:
    """SearxNG + Redis クライアント"""

    def __init__(self, searxng_url: str, redis_url: str, cache_ttl: int = 3600):
        self.searxng_url = searxng_url.rstrip("/")
        self.cache_ttl = cache_ttl
        self.http_client = httpx.AsyncClient(timeout=30)
        self.redis_client = redis.from_url(redis_url, decode_responses=True)

    def _cache_key(self, query: str, category: str = "general") -> str:
        """キャッシュキー生成"""
        key_str = f"searxng:{category}:{query}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    async def search(
        self,
        query: str,
        category: str = "general",
        num_results: int = 10,
        use_cache: bool = True,
    ) -> SearchResponse:
        """検索実行"""
        # キャッシュチェック
        cache_key = self._cache_key(query, category)
        if use_cache:
            cached = await self.redis_client.get(cache_key)
            if cached:
                logger.info(
                    f"Cache hit for query: {query}", extra={"category": "WEB"}
                )
                data = json.loads(cached)
                return SearchResponse(**data)

        # SearxNG検索
        try:
            logger.info(f"Searching: {query}", extra={"category": "WEB"})

            params = {
                "q": query,
                "format": "json",
                "categories": category,
                "pageno": 1,
            }

            response = await self.http_client.get(
                f"{self.searxng_url}/search", params=params
            )
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("results", [])[:num_results]:
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        engine=item.get("engine"),
                        score=item.get("score"),
                    )
                )

            search_response = SearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time=data.get("search_time", 0.0),
                cached=False,
            )

            # キャッシュ保存
            await self.redis_client.setex(
                cache_key, self.cache_ttl, search_response.model_dump_json()
            )

            logger.info(
                f"Search completed: {len(results)} results",
                extra={"category": "WEB", "query": query},
            )

            return search_response

        except Exception as e:
            logger.error(
                f"Search failed: {e}", extra={"category": "WEB", "query": query}
            )
            raise

    async def health_check(self) -> bool:
        """ヘルスチェック"""
        try:
            # SearxNG
            response = await self.http_client.get(f"{self.searxng_url}/")
            response.raise_for_status()

            # Redis
            await self.redis_client.ping()

            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}", extra={"category": "DOCKER"})
            return False

    async def close(self):
        """クライアントクローズ"""
        await self.http_client.aclose()
        await self.redis_client.close()
