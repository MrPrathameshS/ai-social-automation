from app.services.publishers.base import BasePublisher, PublishResult
from app.services.publishers.linkedin_api import (
    publish_to_linkedin,
    LinkedInPublishError,
)
from app.db.models import ContentItem


class LinkedInPublisher(BasePublisher):
    """
    Adapter that connects the platform-agnostic publishing
    system to the LinkedIn API implementation.
    """

    def publish(
        self,
        content: ContentItem,
        access_token: str,
        author_urn: str,
    ) -> PublishResult:
        try:
            return publish_to_linkedin(
                content=content,
                access_token=access_token,
                author_urn=author_urn,
            )
        except LinkedInPublishError:
            # Propagate LinkedIn errors upward
            raise
