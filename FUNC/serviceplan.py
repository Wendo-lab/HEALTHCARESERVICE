from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, UploadFile, File, Form
import json
import os
from typing import Optional
from static_data import STATIC_QUESTIONS
from models import ServicePlan

def create_response(db: Session,responses: str,file: Optional[UploadFile] = None,client_id: int = None):
    try:
        responses_list = json.loads(responses)

        # Initialize file_path
        file_path = None

        # Function to get question type safely
        def get_question_type(question_id):
            for section in STATIC_QUESTIONS.values():
                for question in section:
                    if question["id"] == question_id:
                        return question.get("type")
            return None  # Default to None if not found

        # Process each response
        for response_data in responses_list:
            question_id = response_data["question_id"]
            response_value = response_data["response"]

            # Handle Question ID 4 separately (save under the reason column)
            if question_id == 4:
                new_response = ServicePlan(
                    question_id=question_id,
                    response=None,  # Set response to None
                    client_id=client_id,
                    response_date=None,
                    reason=response_value,  # Save the response under the reason column
                    file_path=None
                )
                db.add(new_response)
                continue  # Skip the rest of the loop for Question ID 4

            question_type = get_question_type(question_id)
            if question_type is None:
                print(f"⚠ Warning: Question ID {question_id} not found in STATIC_QUESTIONS")
                continue  # Skip if question ID is invalid

            # Convert response based on question type
            response_date = None

            if question_type == "boolean":
                response_value = response_value.lower() == "yes"

            elif question_type == "date":
                try:
                    response_date = datetime.strptime(response_value, "%Y-%m-%d").date()
                    response_value = None  # Date is stored separately
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid date format for question {question_id}. Use YYYY-MM-DD.")

            # Handle file upload for question 22
            if question_id == 22 and response_value is True:
                if not file:
                    raise HTTPException(status_code=400, detail="File upload required for question 22")

                upload_folder = "uploads"
                os.makedirs(upload_folder, exist_ok=True)
                file_location = os.path.join(upload_folder, file.filename)

                with open(file_location, "wb") as buffer:
                    buffer.write(file.file.read())

                file_path = file_location  # Save file path

            # Save response to database
            new_response = ServicePlan(
                question_id=question_id,
                response=response_value,
                client_id=client_id,
                response_date=response_date,
                reason=None,  # Reason is only used for Question ID 4
                file_path=file_path if question_id == 22 else None  # Ensure file_path is only for question 22
            )
            db.add(new_response)

        db.commit()
        print("Data saved successfully")

        return {"message": "Responses saved successfully", "client_id": client_id}

    except Exception as e:
        db.rollback()
        print("❌ Error saving response:", str(e))
        raise HTTPException(status_code=500, detail=str(e))