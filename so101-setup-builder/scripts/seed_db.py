#!/usr/bin/env python3
"""Seed the database with initial component and vendor data."""

import asyncio
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import get_settings
from app.db.database import Base
from app.db.models import Category, Component, Vendor, ComponentPrice

settings = get_settings()


async def seed_database():
    """Main seeding function."""
    # Create engine
    database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Load seed data
        data_dir = Path(__file__).parent.parent / "data" / "seed"

        with open(data_dir / "components.json") as f:
            components_data = json.load(f)

        with open(data_dir / "vendors.json") as f:
            vendors_data = json.load(f)

        # Seed categories
        print("Seeding categories...")
        category_map = {}
        for cat_data in components_data["categories"]:
            # Check if exists
            result = await session.execute(
                select(Category).where(Category.slug == cat_data["slug"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                category_map[cat_data["slug"]] = existing.id
                print(f"  Category '{cat_data['name']}' already exists")
            else:
                category = Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data.get("description"),
                    icon=cat_data.get("icon"),
                    sort_order=cat_data.get("sort_order", 0),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(category)
                await session.flush()
                category_map[cat_data["slug"]] = category.id
                print(f"  Created category: {cat_data['name']}")

        # Seed vendors
        print("\nSeeding vendors...")
        vendor_map = {}
        for vendor_data in vendors_data["vendors"]:
            result = await session.execute(
                select(Vendor).where(Vendor.slug == vendor_data["slug"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                vendor_map[vendor_data["slug"]] = existing.id
                print(f"  Vendor '{vendor_data['name']}' already exists")
            else:
                vendor = Vendor(
                    name=vendor_data["name"],
                    slug=vendor_data["slug"],
                    website_url=vendor_data.get("website_url"),
                    description=vendor_data.get("description"),
                    is_active=vendor_data.get("is_active", True),
                    ships_to_us=vendor_data.get("ships_to_us", True),
                    ships_to_eu=vendor_data.get("ships_to_eu", True),
                    typical_shipping_days=vendor_data.get("typical_shipping_days"),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(vendor)
                await session.flush()
                vendor_map[vendor_data["slug"]] = vendor.id
                print(f"  Created vendor: {vendor_data['name']}")

        # Seed components
        print("\nSeeding components...")
        component_map = {}
        for comp_data in components_data["components"]:
            result = await session.execute(
                select(Component).where(Component.slug == comp_data["slug"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                component_map[comp_data["slug"]] = existing.id
                print(f"  Component '{comp_data['name']}' already exists")
            else:
                category_id = category_map.get(comp_data["category_slug"])
                if not category_id:
                    print(f"  Warning: Category '{comp_data['category_slug']}' not found for component '{comp_data['name']}'")
                    continue

                component = Component(
                    name=comp_data["name"],
                    slug=comp_data["slug"],
                    category_id=category_id,
                    description=comp_data.get("description"),
                    specifications=comp_data.get("specifications", {}),
                    is_default_for_so101=comp_data.get("is_default_for_so101", False),
                    quantity_per_arm=comp_data.get("quantity_per_arm", 1),
                    arm_type=comp_data.get("arm_type"),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(component)
                await session.flush()
                component_map[comp_data["slug"]] = component.id
                print(f"  Created component: {comp_data['name']}")

        # Seed sample prices
        print("\nSeeding sample prices...")
        for price_data in vendors_data.get("sample_prices", []):
            component_id = component_map.get(price_data["component_slug"])
            vendor_id = vendor_map.get(price_data["vendor_slug"])

            if not component_id or not vendor_id:
                print(f"  Skipping price for {price_data['component_slug']} @ {price_data['vendor_slug']}")
                continue

            # Check if price exists
            result = await session.execute(
                select(ComponentPrice).where(
                    ComponentPrice.component_id == component_id,
                    ComponentPrice.vendor_id == vendor_id,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  Price already exists for {price_data['component_slug']} @ {price_data['vendor_slug']}")
            else:
                price = ComponentPrice(
                    component_id=component_id,
                    vendor_id=vendor_id,
                    price=Decimal(str(price_data["price"])),
                    currency="USD",
                    product_url=price_data.get("product_url"),
                    in_stock=True,
                    price_fetched_at=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(price)
                print(f"  Created price: ${price_data['price']} for {price_data['component_slug']} @ {price_data['vendor_slug']}")

        await session.commit()
        print("\nSeeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())
