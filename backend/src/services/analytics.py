from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Channel, Video, VideoView
from src.models.comments import Comment
from src.models.subscription import Subscription
from src.schemas.analytics import (
    AudienceResponse,
    ContentResponse,
    DailyMetric,
    OverviewResponse,
    TopVideo,
    VideoStat,
)


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_channel(self, user_id: UUID) -> Channel | None:
        result = await self.session.execute(
            select(Channel).where(Channel.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_overview(self, channel: Channel) -> OverviewResponse:
        channel_id = channel.id
        since = datetime.now(timezone.utc) - timedelta(days=30)

        # Total views across all channel videos (from denormalized counter)
        total_views_result = await self.session.execute(
            select(func.coalesce(func.sum(Video.views_count), 0)).where(
                Video.channel_id == channel_id
            )
        )
        total_views = int(total_views_result.scalar())

        # Total likes
        total_likes_result = await self.session.execute(
            select(func.coalesce(func.sum(Video.likes_count), 0)).where(
                Video.channel_id == channel_id
            )
        )
        total_likes = int(total_likes_result.scalar())

        # Total comments
        total_comments_result = await self.session.execute(
            select(func.count(Comment.id))
            .join(Video, Comment.video_id == Video.id)
            .where(Video.channel_id == channel_id)
        )
        total_comments = int(total_comments_result.scalar())

        # Views per day (last 30 days from video_views table)
        views_per_day_result = await self.session.execute(
            select(
                func.date(VideoView.viewed_at).label("day"),
                func.count(VideoView.id).label("cnt"),
            )
            .join(Video, VideoView.video_id == Video.id)
            .where(Video.channel_id == channel_id, VideoView.viewed_at >= since)
            .group_by(func.date(VideoView.viewed_at))
            .order_by(func.date(VideoView.viewed_at))
        )
        views_per_day = [
            DailyMetric(date=str(row.day), count=row.cnt)
            for row in views_per_day_result.all()
        ]

        # Top 5 videos by views_count with comment count
        top_videos_result = await self.session.execute(
            select(
                Video.id,
                Video.name,
                Video.thumbnail_path,
                Video.views_count,
                Video.likes_count,
                func.count(Comment.id).label("comments_count"),
            )
            .outerjoin(Comment, Comment.video_id == Video.id)
            .where(Video.channel_id == channel_id)
            .group_by(Video.id)
            .order_by(Video.views_count.desc())
            .limit(5)
        )
        top_videos = [
            TopVideo(
                id=row.id,
                title=row.name,
                thumbnail=row.thumbnail_path or "",
                views_count=row.views_count,
                likes_count=row.likes_count,
                comments_count=row.comments_count,
            )
            for row in top_videos_result.all()
        ]

        return OverviewResponse(
            total_views=total_views,
            total_subscribers=channel.subscribers_count,
            total_likes=total_likes,
            total_comments=total_comments,
            views_per_day=views_per_day,
            top_videos=top_videos,
        )

    async def get_content(self, channel: Channel) -> ContentResponse:
        from uuid import NAMESPACE_DNS, uuid5

        channel_id = channel.id
        public_id = uuid5(NAMESPACE_DNS, "privacy_status:public")

        result = await self.session.execute(
            select(
                Video.id,
                Video.name,
                Video.thumbnail_path,
                Video.privacy_id,
                Video.views_count,
                Video.likes_count,
                Video.dislikes_count,
                Video.created_at,
                func.count(Comment.id).label("comments_count"),
            )
            .outerjoin(Comment, Comment.video_id == Video.id)
            .where(Video.channel_id == channel_id)
            .group_by(Video.id)
            .order_by(Video.created_at.desc())
        )

        videos = [
            VideoStat(
                id=row.id,
                title=row.name,
                thumbnail=row.thumbnail_path or "",
                privacy="public" if row.privacy_id == public_id else "private",
                views_count=row.views_count,
                likes_count=row.likes_count,
                dislikes_count=row.dislikes_count,
                comments_count=row.comments_count,
                created_at=row.created_at,
            )
            for row in result.all()
        ]

        return ContentResponse(videos=videos)

    async def get_audience(self, channel: Channel) -> AudienceResponse:
        channel_id = channel.id
        since = datetime.now(timezone.utc) - timedelta(days=30)

        # Subscribers gained per day (last 30 days)
        subs_result = await self.session.execute(
            select(
                func.date(Subscription.created_at).label("day"),
                func.count(Subscription.subscriber_id).label("cnt"),
            )
            .where(
                Subscription.channel_id == channel_id,
                Subscription.created_at >= since,
            )
            .group_by(func.date(Subscription.created_at))
            .order_by(func.date(Subscription.created_at))
        )
        subscribers_per_day = [
            DailyMetric(date=str(row.day), count=row.cnt) for row in subs_result.all()
        ]

        # Unique viewers (distinct user_ids in video_views for channel)
        unique_result = await self.session.execute(
            select(func.count(func.distinct(VideoView.user_id)))
            .join(Video, VideoView.video_id == Video.id)
            .where(Video.channel_id == channel_id, VideoView.user_id.isnot(None))
        )
        unique_viewers = int(unique_result.scalar())

        # Returning viewers (users with > 1 view across channel videos)
        returning_result = await self.session.execute(
            select(func.count()).select_from(
                select(VideoView.user_id)
                .join(Video, VideoView.video_id == Video.id)
                .where(Video.channel_id == channel_id, VideoView.user_id.isnot(None))
                .group_by(VideoView.user_id)
                .having(func.count(VideoView.id) > 1)
                .subquery()
            )
        )
        returning_viewers = int(returning_result.scalar())

        # Comments per day (last 30 days)
        comments_result = await self.session.execute(
            select(
                func.date(Comment.created_at).label("day"),
                func.count(Comment.id).label("cnt"),
            )
            .join(Video, Comment.video_id == Video.id)
            .where(
                Video.channel_id == channel_id,
                Comment.created_at >= since,
            )
            .group_by(func.date(Comment.created_at))
            .order_by(func.date(Comment.created_at))
        )
        comments_per_day = [
            DailyMetric(date=str(row.day), count=row.cnt)
            for row in comments_result.all()
        ]

        return AudienceResponse(
            subscribers_per_day=subscribers_per_day,
            unique_viewers=unique_viewers,
            returning_viewers=returning_viewers,
            comments_per_day=comments_per_day,
        )
