import uuid

from .project_model import Project
from .project_repository import ProjectRepository
from brain.notification.notification_event import NotificationEvent
from brain.notification.notification_publisher import NotificationPublisher
from brain.notification.notification_types import NotificationType


class ProjectService:

    def __init__(
        self,
        repository: ProjectRepository,
        notification_publisher: NotificationPublisher | None = None,
    ):
        self.repository = repository
        self.notification_publisher = notification_publisher

    def create_project(
        self,
        user_id: int,
        name: str,
        description: str | None = None,
    ) -> Project:

        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError("Project name is required.")

        project = Project(
            project_id=str(uuid.uuid4()),
            user_id=user_id,
            name=normalized_name,
            description=description.strip() if description else None,
            status="active",
        )

        created_project = self.repository.create(project)

        if self.notification_publisher is not None:
            self.notification_publisher.publish(
                NotificationEvent(
                    user_id=user_id,
                    type=NotificationType.WORKSPACE,
                    title="Project created",
                    message=f'Your project "{created_project.name}" was created successfully.',
                )
           )

        return created_project

    def get_project(
        self,
        user_id: int,
        project_id: str,
    ) -> Project | None:

        return self.repository.get_by_id(
            project_id=project_id,
            user_id=user_id,
        )

    def get_projects(
        self,
        user_id: int,
    ) -> list[Project]:

        return self.repository.get_all(
            user_id=user_id,
        )

    def update_project(
        self,
        user_id: int,
        project_id: str,
        name: str,
        description: str | None,
        status: str,
    ) -> Project:

        project = self.repository.get_by_id(
            project_id=project_id,
            user_id=user_id,
        )

        if project is None:
            raise ValueError("Project not found.")

        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError("Project name is required.")

        project.name = normalized_name
        project.description = (
            description.strip()
            if description
            else None
        )
        project.status = status

        return self.repository.update(project)

    def delete_project(
        self,
        user_id: int,
        project_id: str,
    ) -> bool:

        return self.repository.delete(
            project_id=project_id,
            user_id=user_id,
        )