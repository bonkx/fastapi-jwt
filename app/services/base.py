from fastapi import BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession


class SessionMixin:
    """Provides instance of database session."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class BaseService(SessionMixin):
    """Base class for application services."""


class EmailBackgroundTasksMixin:
    """Provides instance of email background_tasks."""

    def __init__(self, background_tasks: BackgroundTasks) -> None:
        self.background_tasks = background_tasks
