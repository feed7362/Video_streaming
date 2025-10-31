import json
import logging
from pathlib import Path
from uuid import NAMESPACE_DNS, uuid5

from sqlalchemy.dialects.postgresql import insert

from src.infrastructure.database import async_session_maker
from src.models import (
    Category,
    PrivacyStatus,
    ReactionType,
    Role,
    UserStatus,
    VideoStatus,
)

SEED_FILE = Path(__file__).parent / "initial_data.json"


def deterministic_uuid(scope: str, name: str):
    """Generate deterministic UUID5 using a scope prefix."""
    return uuid5(NAMESPACE_DNS, f"{scope}:{name.lower()}")


async def seed_initial_data():
    """Seed initial system data into the database safely (idempotent)."""
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    async with async_session_maker() as session:
        # ---- Roles ----
        roles = [
            {
                "id": deterministic_uuid("user_role", i["name"]),
                "name": i["name"],
                "description": i["description"],
            }
            for i in data.get("roles", [])
        ]
        await session.execute(
            insert(Role).values(roles).on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- Reaction Types ----
        reactions = [
            {
                "id": deterministic_uuid("reaction_type", i["name"]),
                "name": i["name"],
                "path": i["path"],
            }
            for i in data.get("reaction_types", [])
        ]
        await session.execute(
            insert(ReactionType)
            .values(reactions)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- Categories ----
        categories = [
            {
                "id": deterministic_uuid("video_category", i["name"]),
                "name": i["name"],
            }
            for i in data.get("categories", [])
        ]
        await session.execute(
            insert(Category)
            .values(categories)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- Privacy Statuses ----
        privacy_statuses = [
            {
                "id": deterministic_uuid("privacy_status", i["name"]),
                "name": i["name"],
            }
            for i in data.get("privacy_statuses", [])
        ]
        await session.execute(
            insert(PrivacyStatus)
            .values(privacy_statuses)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- User Statuses ----
        user_statuses = [
            {
                "id": deterministic_uuid("user_status", i["value"]),
                "value": i["value"],
            }
            for i in data.get("user_statuses", [])
        ]
        await session.execute(
            insert(UserStatus)
            .values(user_statuses)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        # ---- Video Statuses ---- ✅ fixed
        video_statuses = [
            {
                "id": deterministic_uuid("video_status", i["value"]),
                "value": i["value"],
            }
            for i in data.get("video_statuses", [])
        ]
        await session.execute(
            insert(VideoStatus)
            .values(video_statuses)
            .on_conflict_do_nothing(index_elements=["id"])
        )

        await session.commit()
        logging.info("✅ Initial data seeded successfully.")
