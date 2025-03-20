from sqlalchemy.orm import Session
from models import AnnualServicePlan
from schemas import ClientResponseSchema
from typing import List
from fastapi import HTTPException

#  Retrieve user responses
def get_user_responses(db: Session, client_id: int):
    responses = db.query(AnnualServicePlan).filter(AnnualServicePlan.client_id == client_id).all()
    return [{"question_id": r.question_id, "selected_months": r.selected_months.split(",") if r.selected_months else []} for r in responses]

# Save or update client responses
def save_user_response(db: Session, responses: List[ClientResponseSchema]):
    try:
        if not responses:
            return {"message": "No responses provided. No changes were made."}

        for response in responses:
            existing_response = db.query(AnnualServicePlan).filter(
                AnnualServicePlan.question_id == response.question_id,
                AnnualServicePlan.client_id == response.client_id
            ).first()

            if existing_response:
                existing_response.selected_months = ",".join(response.selected_months) if response.selected_months else None
            else:
                new_response = AnnualServicePlan(
                    client_id=response.client_id,
                    question_id=response.question_id,
                    selected_months=",".join(response.selected_months) if response.selected_months else None
                )
                db.add(new_response)

        db.commit()
        return {"message": "Responses saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error saving responses: {str(e)}")