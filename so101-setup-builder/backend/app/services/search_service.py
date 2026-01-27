from typing import Any

import httpx

from app.config import get_settings

settings = get_settings()


class SearchService:
    """Service for web search functionality."""

    def __init__(self):
        self.tavily_api_key = settings.tavily_api_key

    async def search(
        self,
        query: str,
        search_depth: str = "basic",
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        max_results: int = 5,
    ) -> dict[str, Any]:
        """Perform a web search using Tavily API."""
        if not self.tavily_api_key:
            return {
                "results": [],
                "error": "Search API key not configured",
            }

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "search_depth": search_depth,
                    "max_results": max_results,
                }

                if include_domains:
                    payload["include_domains"] = include_domains
                if exclude_domains:
                    payload["exclude_domains"] = exclude_domains

                response = await client.post(
                    "https://api.tavily.com/search",
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            return {
                "results": [],
                "error": f"Search request failed: {str(e)}",
            }
        except Exception as e:
            return {
                "results": [],
                "error": f"Search error: {str(e)}",
            }

    async def search_component_info(
        self,
        component_name: str,
        info_type: str = "specifications",
    ) -> dict[str, Any]:
        """Search for specific component information."""
        queries = {
            "specifications": f"{component_name} specifications datasheet",
            "reviews": f"{component_name} review robotics",
            "alternatives": f"{component_name} alternatives similar products",
            "tutorials": f"{component_name} tutorial guide how to use",
        }

        query = queries.get(info_type, f"{component_name} {info_type}")

        return await self.search(
            query=query,
            search_depth="advanced",
            max_results=5,
        )

    async def search_lerobot_docs(
        self,
        query: str,
    ) -> dict[str, Any]:
        """Search specifically in LeRobot documentation."""
        return await self.search(
            query=f"site:huggingface.co/docs/lerobot {query}",
            search_depth="basic",
            max_results=5,
        )
