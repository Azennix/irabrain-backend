from fastapi import APIRouter, Depends, HTTPException

from security.dependencies import get_current_user
from api.goal_dependencies import get_goal_service
from brain.project.goal_service import GoalService
from api.schemas.brain_schema import CreateGoalRequest, UpdateGoalRequest


router = APIRouter(
    prefix="/projects/{project_id}/goals",
    tags=["Project Goals"],
)


@router.post("")
def create_goal(
    project_id: str,
    request: CreateGoalRequest,
    current_user=Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
):
    try:
        goal = goal_service.create_goal(
            user_id=current_user.user_id,
            project_id=project_id,
            title=request.title,
            description=request.description,
        )

        return {
            "goal": {
                "id": goal.goal_id,
                "project_id": goal.project_id,
                "title": goal.title,
                "description": goal.description,
                "status": goal.status,
            }
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("")
def get_goals(
    project_id: str,
    current_user=Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
):
    goals = goal_service.get_goals(
        user_id=current_user.user_id,
        project_id=project_id,
    )

    return {
        "goals": [
            {
                "id": goal.goal_id,
                "project_id": goal.project_id,
                "title": goal.title,
                "description": goal.description,
                "status": goal.status,
            }
            for goal in goals
        ]
    }


@router.get("/{goal_id}")
def get_goal(
    project_id: str,
    goal_id: str,
    current_user=Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
):
    goal = goal_service.get_goal(
        user_id=current_user.user_id,
        project_id=project_id,
        goal_id=goal_id,
    )

    if goal is None:
        raise HTTPException(
            status_code=404,
            detail="Goal not found.",
        )

    return {
        "goal": {
            "id": goal.goal_id,
            "project_id": goal.project_id,
            "title": goal.title,
            "description": goal.description,
            "status": goal.status,
        }
    }


@router.patch("/{goal_id}")
def update_goal(
    project_id: str,
    goal_id: str,
    request: UpdateGoalRequest,
    current_user=Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
):
    try:
        goal = goal_service.update_goal(
            user_id=current_user.user_id,
            project_id=project_id,
            goal_id=goal_id,
            title=request.title,
            description=request.description,
            status=request.status,
        )

        return {
            "goal": {
                "id": goal.goal_id,
                "project_id": goal.project_id,
                "title": goal.title,
                "description": goal.description,
                "status": goal.status,
            }
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.delete("/{goal_id}")
def delete_goal(
    project_id: str,
    goal_id: str,
    current_user=Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
):
    deleted = goal_service.delete_goal(
        user_id=current_user.user_id,
        project_id=project_id,
        goal_id=goal_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Goal not found.",
        )

    return {
        "success": True
    }