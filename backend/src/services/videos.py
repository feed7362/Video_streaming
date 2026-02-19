from typing import List, Tuple
from uuid import NAMESPACE_DNS, UUID, uuid5

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.pagination import paginate_query
from ..errors.videos import (
    InvalidPrivacyError,
    VideoNotFoundError,
    VideoPrivacyUpdateForbidden,
)
from ..models import Category, Channel, PrivacyStatus, Video, VideoReaction, VideoView
from ..schemas.video import map_video_to_playback, to_video_preview
from ..services.reactions import toggle_reaction


class VideoService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_playback(self, video_id: UUID, user_id: UUID | None):
        video = await self._get_video_with_details(video_id)

        if user_id:
            await self._record_view(video.id, user_id)

        resolutions = [f"{r.height}p" for r in video.resolutions]
        return map_video_to_playback(video, resolutions)

    async def list_videos(self, page: int, size: int, category: str | None = None):
        """
        Retrieves public, ready videos. Optionally filters by category.
        """
        filters = [
            Video.privacy_id == uuid5(NAMESPACE_DNS, "privacy_status:public"),
            Video.status_id == uuid5(NAMESPACE_DNS, "video_status:ready"),
        ]

        if category:
            category_id = uuid5(NAMESPACE_DNS, f"video_category:{category}")
            filters.append(Video.category_id == category_id)

        preload = [
            selectinload(Video.channel),
            selectinload(Video.privacy),
            selectinload(Video.resolutions),
        ]

        return await paginate_query(
            session=self.session,
            model=Video,
            page=page,
            size=size,
            filters=filters,
            preload=preload,
            order_by=Video.created_at.desc(),
            mapper=to_video_preview,
        )

    async def list_categories(self) -> List[str]:
        result = await self.session.execute(
            select(Category.name)
            .join(Video, Category.id == Video.category_id)
            .distinct()
            .order_by(Category.name)
        )
        return [str(name) for name in result.scalars().all()]

    async def react(self, video_id: UUID, user_id: UUID, reaction_name: str) -> dict:
        return await toggle_reaction(
            session=self.session,
            user_id=user_id,
            target_model=VideoReaction,
            target_field=VideoReaction.video_id,
            target_id=video_id,
            reaction_name=reaction_name,
        )

    async def update_privacy(
        self, video_id: UUID, user_id: UUID, privacy_name: str
    ) -> Tuple[str, str]:
        # Validate Privacy Level
        privacy = await self.session.scalar(
            select(PrivacyStatus).where(PrivacyStatus.name == privacy_name)
        )
        if not privacy:
            raise InvalidPrivacyError(privacy_name)

        # Validate Ownership and Existence
        video = await self.session.scalar(
            select(Video)
            .join(Channel)
            .options(selectinload(Video.privacy))
            .where(Video.id == video_id, Channel.user_id == user_id)
        )
        if not video:
            raise VideoPrivacyUpdateForbidden()

        old_privacy = video.privacy.name if video.privacy else "unknown"

        # Update
        video.privacy_id = privacy.id
        await self.session.commit()

        return old_privacy, privacy.name

    # --- Internal Helpers ---

    async def _get_video_with_details(self, video_id: UUID) -> Video:
        result = await self.session.execute(
            select(Video)
            .options(
                selectinload(Video.channel),
                selectinload(Video.privacy),
                selectinload(Video.resolutions),
            )
            .where(Video.id == video_id)
        )
        video = result.scalar_one_or_none()
        if not video:
            raise VideoNotFoundError(video_id)
        return video

    async def _record_view(self, video_id: UUID, user_id: UUID) -> None:
        exists = await self.session.scalar(
            select(VideoView.id).where(
                VideoView.video_id == video_id, VideoView.user_id == user_id
            )
        )
        if not exists:
            self.session.add(VideoView(video_id=video_id, user_id=user_id))
            await self.session.execute(
                update(Video)
                .where(Video.id == video_id)
                .values(views_count=Video.views_count + 1)
            )
            await self.session.commit()
