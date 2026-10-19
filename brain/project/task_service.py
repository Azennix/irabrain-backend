from uuid import UUID, uuid4

from .task_model import ProjectTask
from .task_repository import ProjectTaskRepository
from brain.notification.notification_event import NotificationEvent
from brain.notification.notification_publisher import NotificationPublisher
from brain.notification.notification_types import NotificationType


class ProjectTaskService:

    VALID_STATUSES = {
        "pending",
        "active",
        "completed",
        "paused",
        "archived",
    }

    def __init__(
        self,
        repository: ProjectTaskRepository,
         notification_publisher: NotificationPublisher | None = None,
    ):
        self.repository = repository
        self.notification_publisher = notification_publisher

    def create_task(
        self,
        project_id: str,
        user_id: int,
        title: str,
        description: str | None = None,
        goal_id: str | None = None,
    ) -> ProjectTask:
        self._validate_uuid(
            project_id,
            "project_id",
        )

        title = title.strip()

        if not title:
            raise ValueError(
                "Task title is required"
            )

        task = ProjectTask(
            task_id=str(uuid4()),
            project_id=project_id,
            goal_id=goal_id,
            user_id=user_id,
            title=title,
            description=description,
            status="pending",
        )
        created_task = self.repository.create(task)

        if self.notification_publisher is not None:
             self.notification_publisher.publish(
                NotificationEvent(
                    user_id=user_id,
                    type=NotificationType.WORKSPACE,
                    title="Task created",
                    message=f'The task "{created_task.title}" was created successfully.',
                )
            )

        return created_task



    def get_task(
        self,
        task_id: str,
        project_id: str,
        user_id: int,
    ) -> ProjectTask | None:
        self._validate_uuid(
            task_id,
            "task_id",
        )

        self._validate_uuid(
            project_id,
            "project_id",
        )

        return self.repository.get_by_id(
            task_id=task_id,
            project_id=project_id,
            user_id=user_id,
        )

    def get_tasks(
        self,
        project_id: str,
        user_id: int,
    ) -> list[ProjectTask]:
        self._validate_uuid(
            project_id,
            "project_id",
        )

        return self.repository.get_all(
            project_id=project_id,
            user_id=user_id,
        )

    def update_task(
        self,
        task_id: str,
        project_id: str,
        user_id: int,
        title: str,
        description: str | None,
        status: str,
        goal_id: str | None = None,
    ) -> ProjectTask:
        self._validate_uuid(
            task_id,
            "task_id",
        )

        self._validate_uuid(
            project_id,
            "project_id",
        )

        title = title.strip()

        if not title:
            raise ValueError(
                "Task title is required"
            )

        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid task status: {status}"
            )

        existing = self.repository.get_by_id(
            task_id=task_id,
            project_id=project_id,
            user_id=user_id,
        )

        if existing is None:
            raise ValueError(
                "Task not found"
            )

        updated_task = ProjectTask(
            task_id=existing.task_id,
            project_id=existing.project_id,
            goal_id=goal_id,
            user_id=existing.user_id,
            title=title,
            description=description,
            status=status,
        )

        return self.repository.update(
            updated_task
        )

    def delete_task(
        self,
        task_id: str,
        project_id: str,
        user_id: int,
    ) -> bool:
        self._validate_uuid(
            task_id,
            "task_id",
        )

        self._validate_uuid(
            project_id,
            "project_id",
        )

        return self.repository.delete(
            task_id=task_id,
            project_id=project_id,
            user_id=user_id,
        )

    @staticmethod
    def _validate_uuid(
        value: str,
        field_name: str,
    ) -> None:
        try:
            UUID(value)
        except (ValueError, AttributeError):
            raise ValueError(
                f"Invalid {field_name}"
            )