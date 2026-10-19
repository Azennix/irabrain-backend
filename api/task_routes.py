from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.schemas.brain_schema import (
    CreateTaskRequest,
    UpdateTaskRequest,
)
from brain.project.task_model import ProjectTask
from brain.project.task_service import ProjectTaskService
from api.task_dependencies import get_task_service
from security.dependencies import get_current_user


router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["Project Tasks"],
)


def _task_response(task: ProjectTask) -> dict:
    return {
        "task_id": task.task_id,
        "project_id": task.project_id,
        "goal_id": task.goal_id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: str,
    request: CreateTaskRequest,
    current_user=Depends(get_current_user),
    service: ProjectTaskService = Depends(
        get_task_service
    ),
):
    try:
        task = service.create_task(
            project_id=project_id,
            user_id=current_user.user_id,
            title=request.title,
            description=request.description,
            goal_id=request.goal_id,
        )

        return _task_response(task)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("")
def get_tasks(
    project_id: str,
    current_user=Depends(get_current_user),
    service: ProjectTaskService = Depends(
        get_task_service
    ),
):
    try:
        tasks = service.get_tasks(
            project_id=project_id,
            user_id=current_user.user_id,
        )

        return [
            _task_response(task)
            for task in tasks
        ]

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/{task_id}")
def get_task(
    project_id: str,
    task_id: str,
    current_user=Depends(get_current_user),
    service: ProjectTaskService = Depends(
        get_task_service
    ),
):
    try:
        task = service.get_task(
            task_id=task_id,
            project_id=project_id,
            user_id=current_user.user_id,
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return _task_response(task)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.patch("/{task_id}")
def update_task(
    project_id: str,
    task_id: str,
    request: UpdateTaskRequest,
    current_user=Depends(get_current_user),
    service: ProjectTaskService = Depends(
        get_task_service
    ),
):
    try:
        task = service.update_task(
            task_id=task_id,
            project_id=project_id,
            user_id=current_user.user_id,
            title=request.title,
            description=request.description,
            status=request.status,
            goal_id=request.goal_id,
        )

        return _task_response(task)

    except ValueError as exc:
        if str(exc) == "Task not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete("/{task_id}")
def delete_task(
    project_id: str,
    task_id: str,
    current_user=Depends(get_current_user),
    service: ProjectTaskService = Depends(
        get_task_service
    ),
):
    try:
        deleted = service.delete_task(
            task_id=task_id,
            project_id=project_id,
            user_id=current_user.user_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return {
            "message": "Task deleted successfully"
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )