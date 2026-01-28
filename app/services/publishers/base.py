from abc import ABC, abstractmethod
from app.db.models import ContentItem
from app.services.publishers.errors import PublishErrorType


class PublishError(Exception):
    def __init__(
        self,
        message: str,
        error_type: PublishErrorType = PublishErrorType.UNKNOWN,
        retryable: bool = True,
    ):
        super().__init__(message)
        self.error_type = error_type
        self.retryable = retryable


class PublishResult(dict):
    pass


class BasePublisher(ABC):
    @abstractmethod
    def publish(
        self,
        content: ContentItem,
        access_token: str,
        author_urn: str,
    ) -> PublishResult:
        raise PublishError("Publish not implemented", retryable=False)
