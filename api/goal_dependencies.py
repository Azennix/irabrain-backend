from fastapi import Depends
from sqlalchemy.orm import Session

from database.dependencies import get_db
from brain.project.goal_service import GoalService
from brain.project.sqlalchemy_goal_repository import SQLAlchemyGoalRepository


def get_goal_service(
    db: Session = Depends(get_db),
) -> GoalService:

    repository = SQLAlchemyGoalRepository(session=db)

    return GoalService(repository=repository)