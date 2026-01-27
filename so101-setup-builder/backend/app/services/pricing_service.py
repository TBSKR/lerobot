from datetime import datetime
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.api.v1.schemas.pricing import PricingSearchResult
from app.db.models import ComponentPrice, Vendor

settings = get_settings()


class PricingService:
    """Service for price fetching and comparison."""

    def __init__(self):
        self.tavily_api_key = settings.tavily_api_key
        self.serpapi_key = settings.serpapi_key

    async def search_prices(
        self,
        component_name: str,
        vendor_preference: str | None = None,
        include_shipping: bool = True,
    ) -> list[PricingSearchResult]:
        """Search for real-time prices using web search APIs."""
        results = []

        # Build search query
        query = f"{component_name} buy price"
        if vendor_preference:
            query += f" site:{self._get_vendor_domain(vendor_preference)}"

        # Try Tavily first
        if self.tavily_api_key:
            tavily_results = await self._search_tavily(query)
            results.extend(tavily_results)

        # Fall back to SerpAPI if available and needed
        if not results and self.serpapi_key:
            serp_results = await self._search_serpapi(query)
            results.extend(serp_results)

        return results

    async def refresh_prices(
        self,
        component_id: int,
        db: AsyncSession,
    ) -> list[dict[str, Any]]:
        """Refresh prices for a component from all vendors."""
        # Get existing prices for component
        query = select(ComponentPrice).where(ComponentPrice.component_id == component_id)
        result = await db.execute(query)
        existing_prices = result.scalars().all()

        updated = []
        for price in existing_prices:
            if price.product_url:
                # Try to fetch updated price from URL
                new_price = await self._fetch_price_from_url(price.product_url)
                if new_price:
                    price.price = new_price
                    price.price_fetched_at = datetime.utcnow()
                    updated.append({
                        "vendor_id": price.vendor_id,
                        "old_price": float(price.price),
                        "new_price": float(new_price),
                    })

        await db.commit()
        return updated

    async def _search_tavily(self, query: str) -> list[PricingSearchResult]:
        """Search using Tavily API."""
        if not self.tavily_api_key:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_api_key,
                        "query": query,
                        "search_depth": "basic",
                        "include_domains": [
                            "aliexpress.com",
                            "amazon.com",
                            "waveshare.com",
                            "robotshop.com",
                        ],
                        "max_results": 5,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("results", []):
                    price = self._extract_price(item.get("content", ""))
                    if price:
                        results.append(
                            PricingSearchResult(
                                source="tavily",
                                title=item.get("title", "Unknown"),
                                price=price,
                                currency="USD",
                                url=item.get("url", ""),
                                seller=self._extract_seller(item.get("url", "")),
                                shipping=None,
                                fetched_at=datetime.utcnow(),
                            )
                        )
                return results

        except Exception:
            return []

    async def _search_serpapi(self, query: str) -> list[PricingSearchResult]:
        """Search using SerpAPI."""
        if not self.serpapi_key:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://serpapi.com/search",
                    params={
                        "api_key": self.serpapi_key,
                        "engine": "google_shopping",
                        "q": query,
                        "num": 5,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("shopping_results", []):
                    price_str = item.get("price", "")
                    price = self._parse_price_string(price_str)
                    if price:
                        results.append(
                            PricingSearchResult(
                                source="serpapi",
                                title=item.get("title", "Unknown"),
                                price=price,
                                currency="USD",
                                url=item.get("link", ""),
                                seller=item.get("source", None),
                                shipping=item.get("delivery", None),
                                fetched_at=datetime.utcnow(),
                            )
                        )
                return results

        except Exception:
            return []

    async def _fetch_price_from_url(self, url: str) -> Decimal | None:
        """Attempt to fetch current price from a product URL."""
        # This would ideally use a web scraping service
        # For now, return None (prices updated manually)
        return None

    def _extract_price(self, text: str) -> Decimal | None:
        """Extract price from text content."""
        import re

        # Match common price patterns
        patterns = [
            r"\$(\d+(?:\.\d{2})?)",
            r"USD\s*(\d+(?:\.\d{2})?)",
            r"(\d+(?:\.\d{2})?)\s*(?:USD|dollars?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return Decimal(match.group(1))
                except (ValueError, decimal.InvalidOperation):
                    continue

        return None

    def _parse_price_string(self, price_str: str) -> Decimal | None:
        """Parse a price string like '$19.99'."""
        import re

        match = re.search(r"[\$]?([\d,]+(?:\.\d{2})?)", price_str.replace(",", ""))
        if match:
            try:
                return Decimal(match.group(1))
            except Exception:
                pass
        return None

    def _extract_seller(self, url: str) -> str | None:
        """Extract seller/vendor from URL."""
        if "aliexpress" in url.lower():
            return "AliExpress"
        elif "amazon" in url.lower():
            return "Amazon"
        elif "waveshare" in url.lower():
            return "Waveshare"
        elif "robotshop" in url.lower():
            return "RobotShop"
        return None

    def _get_vendor_domain(self, vendor: str) -> str:
        """Get domain for vendor filtering."""
        domains = {
            "aliexpress": "aliexpress.com",
            "amazon": "amazon.com",
            "waveshare": "waveshare.com",
            "robotshop": "robotshop.com",
        }
        return domains.get(vendor.lower(), "")
