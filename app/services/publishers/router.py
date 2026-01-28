print("🚀 router.py imported")

from app.core.platform import Platform
from app.services.publishers.linkedin import LinkedInPublisher
from app.db.models import ContentItem


class PublisherRouter:
    """
    Routes publishing requests to the correct platform publisher.
    """

    def __init__(self):
        self._publishers = {
            Platform.LINKEDIN: LinkedInPublisher(),
        }

    def publish(
        self,
        content: ContentItem,
        access_token: str,
        author_urn: str,
    ) -> dict:
        publisher = self._publishers.get(content.platform)

        if not publisher:
            raise ValueError(
                f"No publisher registered for platform {content.platform}"
            )

        return publisher.publish(
            content=content,
            access_token=access_token,
            author_urn=author_urn,
        )
