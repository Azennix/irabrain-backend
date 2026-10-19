import uuid

from fastapi import APIRouter, Depends, HTTPException

from security.dependencies import get_current_user
from api.project_dependencies import get_project_service
from brain.project.project_service import ProjectService
from api.schemas.brain_schema import (
    CreateProjectRequest,
    UpdateProjectRequest,
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post("")
def create_project(
    request: CreateProjectRequest,
    current_user=Depends(get_current_user),
    project_service: ProjectService = Depends(
        get_project_service
    ),
):
    try:
        project = project_service.create_project(
            user_id=current_user.user_id,
            name=request.name,
            description=request.description,
        )

        return {
            "project": {
                "id": project.project_id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
            }
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("")
def get_projects(
    current_user=Depends(get_current_user),
    project_service: ProjectService = Depends(
        get_project_service
    ),
):
    projects = project_service.get_projects(
        user_id=current_user.user_id
    )

    return {
        "projects": [
            {
                "id": project.project_id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
            }
            for project in projects
        ]
    }


@router.get("/{project_id}")
def get_project(
    project_id: str,
    current_user=Depends(get_current_user),
    project_service: ProjectService = Depends(
        get_project_service
    ),
):
    project = project_service.get_project(
        user_id=current_user.user_id,
        project_id=project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return {
        "project": {
            "id": project.project_id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
        }
    }


@router.patch("/{project_id}")
def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    current_user=Depends(get_current_user),
    project_service: ProjectService = Depends(
        get_project_service
    ),
):
    try:
        project = project_service.update_project(
            user_id=current_user.user_id,
            project_id=project_id,
            name=request.name,
            description=request.description,
            status=request.status,
        )

        return {
            "project": {
                "id": project.project_id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
            }
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    current_user=Depends(get_current_user),
    project_service: ProjectService = Depends(
        get_project_service
    ),
):
    deleted = project_service.delete_project(
        user_id=current_user.user_id,
        project_id=project_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return {
        "success": True
    }