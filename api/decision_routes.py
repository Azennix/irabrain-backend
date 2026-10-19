from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas.brain_schema import (
    CreateDecisionRequest,
    UpdateDecisionRequest,
)
from brain.project.project_decision import ProjectDecision
from brain.project.decision_service import ProjectDecisionService
from api.project_dependencies import (
    get_project_decision_service,
)
from security.dependencies import get_current_user


router = APIRouter(
    prefix="/projects/{project_id}/decisions",
    tags=["Project Decisions"],
)


def _decision_response(
    decision: ProjectDecision,
) -> dict:
    return {
        "decision_id": decision.decision_id,
        "project_id": decision.project_id,
        "user_id": decision.user_id,
        "title": decision.title,
        "description": decision.description,
        "reason": decision.reason,
        "status": decision.status,
        "created_at": decision.created_at,
        "updated_at": decision.updated_at,
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_decision(
    project_id: str,
    request: CreateDecisionRequest,
    current_user=Depends(get_current_user),
    service: ProjectDecisionService = Depends(
        get_project_decision_service
    ),
):
    try:
        decision = service.create_decision(
            project_id=project_id,
            user_id=current_user.user_id,
            title=request.title,
            description=request.description,
            reason=request.reason,
        )

        return _decision_response(decision)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("")
def get_decisions(
    project_id: str,
    current_user=Depends(get_current_user),
    service: ProjectDecisionService = Depends(
        get_project_decision_service
    ),
):
    try:
        decisions = service.get_project_decisions(
            project_id=project_id,
            user_id=current_user.user_id,
        )

        return [
            _decision_response(decision)
            for decision in decisions
        ]

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/{decision_id}")
def get_decision(
    project_id: str,
    decision_id: str,
    current_user=Depends(get_current_user),
    service: ProjectDecisionService = Depends(
        get_project_decision_service
    ),
):
    try:
        decision = service.get_decision(
            decision_id=decision_id,
            user_id=current_user.user_id,
        )

        if decision is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found",
            )

        if decision.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found",
            )

        return _decision_response(decision)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.patch("/{decision_id}")
def update_decision(
    project_id: str,
    decision_id: str,
    request: UpdateDecisionRequest,
    current_user=Depends(get_current_user),
    service: ProjectDecisionService = Depends(
        get_project_decision_service
    ),
):
    try:
        existing = service.get_decision(
            decision_id=decision_id,
            user_id=current_user.user_id,
        )

        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found",
            )

        if existing.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found",
            )

        decision = service.update_decision(
            decision_id=decision_id,
            user_id=current_user.user_id,
            title=request.title,
            description=request.description,
            reason=request.reason,
            status=request.status,
        )

        return _decision_response(decision)

    except ValueError as exc:
        if str(exc) == "Decision not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete("/{decision_id}")
def delete_decision(
    project_id: str,
    decision_id: str,
    current_user=Depends(get_current_user),
    service: ProjectDecisionService = Depends(
        get_project_decision_service
    ),
):
    try:
        existing = service.get_decision(
            decision_id=decision_id,
            user_id=current_user.user_id,
        )

        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found",
            )

        if existing.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found",
            )

        service.delete_decision(
            decision_id=decision_id,
            user_id=current_user.user_id,
        )

        return {
            "message": "Decision deleted successfully"
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )