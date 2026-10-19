from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.dependencies import get_db
from database.feedback_model import Feedback
from security.dependencies import get_current_user


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


# =====================================================
# FEEDBACK REQUEST
# =====================================================

class FeedbackRequest(BaseModel):
    feedback_type: str
    message: str


# =====================================================
# SUBMIT FEEDBACK
# =====================================================

@router.post("")
def submit_feedback(
    request: FeedbackRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        message = request.message.strip()
        feedback_type = request.feedback_type.strip()

        if not message:
            raise HTTPException(
                status_code=400,
                detail="Feedback message cannot be empty.",
            )

        if not feedback_type:
            raise HTTPException(
                status_code=400,
                detail="Feedback type cannot be empty.",
            )

        feedback = Feedback(
            user_id=current_user.user_id,
            feedback_type=feedback_type,
            message=message,
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        return {
            "success": True,
            "feedback_id": feedback.feedback_id,
            "message": "Feedback submitted successfully.",
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        print(
            "FEEDBACK SUBMISSION ERROR:",
            repr(e),
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to submit feedback.",
        )