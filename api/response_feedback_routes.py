from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.dependencies import get_db
from database.response_feedback_model import ResponseFeedback
from security.dependencies import get_current_user


router = APIRouter(
    prefix="/response-feedback",
    tags=["Response Feedback"],
)


class ResponseFeedbackRequest(BaseModel):
    conversation_id: str | None = None
    message_id: str
    rating: str


@router.post("")
def submit_response_feedback(
    request: ResponseFeedbackRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        message_id = request.message_id.strip()
        rating = request.rating.strip().lower()

        if not message_id:
            raise HTTPException(
                status_code=400,
                detail="Message ID cannot be empty.",
            )

        if rating not in {"like", "dislike"}:
            raise HTTPException(
                status_code=400,
                detail="Rating must be like or dislike.",
            )

        existing_feedback = (
            db.query(ResponseFeedback)
            .filter(
                ResponseFeedback.user_id == current_user.user_id,
                ResponseFeedback.message_id == message_id,
            )
            .first()
        )

        if existing_feedback:
            existing_feedback.rating = rating

            if request.conversation_id:
                existing_feedback.conversation_id = (
                    request.conversation_id
                )

            db.commit()
            db.refresh(existing_feedback)

            return {
                "success": True,
                "feedback_id": existing_feedback.feedback_id,
                "message": "Response feedback updated.",
            }

        feedback = ResponseFeedback(
            user_id=current_user.user_id,
            conversation_id=request.conversation_id,
            message_id=message_id,
            rating=rating,
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        return {
            "success": True,
            "feedback_id": feedback.feedback_id,
            "message": "Response feedback submitted.",
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        print(
            "RESPONSE FEEDBACK SUBMISSION ERROR:",
            repr(e),
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to submit response feedback.",
        )