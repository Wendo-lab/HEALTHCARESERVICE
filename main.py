from fastapi import FastAPI,Depends,HTTPException,status,Form,File, UploadFile
from sqlalchemy.orm import Session
from configs.configs import engine,Base 
from configs import configs
from models import ClientDetails,ExtraClientDetails,AnnualServicePlan,ServicePlan,ClientNames,SignOut
from FUNC import serviceplan,annualplan,client,login,signout
from schemas import ResponseSchema,ClientResponseSchema,ClientCreateSchema,ExtraClientDetailsSchema,LoginRequestSchema,SignOutSchema,ClientDetailsResponse
from typing import List
from static_data import STATIC_QUESTIONS,COVER_TYPES
from staticdata import STATICQUESTIONS
from FUNC.login import authenticate_user
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from pydantic import EmailStr
from typing import Literal
from typing import Optional
from fastapi.responses import JSONResponse
import jwt
from starlette.middleware.sessions import SessionMiddleware



app = FastAPI()
SECRET_KEY = "your_secret_key"

app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")
# Initialize Jinja2 template engine
templates = Jinja2Templates(directory="templates")  # Point to your templates folder
# Create tables in the database



#UPLOAD_FOLDER = "uploads"
#os.makedirs(UPLOAD_FOLDER, exist_ok=True)


Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

#Service Plan
# GET: Fetch all questions with serviceplan responses (if available)
@app.get("/question/", tags=["Service Plan"])
def get_question(client_id: int, db: Session = Depends(configs.get_db)):
    responses = serviceplan.get_responses(db, client_id)

    formatted_questions = []
    for heading, questions in STATIC_QUESTIONS.items():
        for q in questions:
            if "type" not in q:
                print(f"Missing 'type' in question: {q}")  # Debugging line
        formatted_questions.append({
            "heading": heading,
            "questions": [
                {
                    "id": q.get("id", -1), 
                    "text": q.get("text", "No question text"),
                    "type": q.get("type", "default_type"),
                    "response": responses.get(q.get("id", -1), {}).get("response"),
                    "response_date": responses.get(q.get("id", -1), {}).get("response_date")
                }
                for q in questions
            ]
        })
    return formatted_questions

@app.get("/serviceplan/", response_class=HTMLResponse, tags=["Service Plan"])
def render_service_plan_page(
    request: Request,
    client_id: Optional[int] = None,
    db: Session = Depends(configs.get_db)
):
    # If no client_id is provided, use the most recent one
    if client_id is None:
        latest_client = db.query(ClientDetails).order_by(ClientDetails.id.desc()).first()
        if latest_client is None:
            raise HTTPException(status_code=404, detail="No clients found.")
        client_id = latest_client.id  # Use the most recent client_id

    return templates.TemplateResponse("serviceplan.html", {
        "request": request,
        "client_id": client_id,
        "STATIC_QUESTIONS": STATIC_QUESTIONS
    })

@app.get("/serviceplan/latest-client/", tags=["Service Plan"])
def get_latest_client(db: Session = Depends(configs.get_db)):
    latest_client = db.query(ClientDetails).order_by(ClientDetails.id.desc()).first()
    if not latest_client:
        raise HTTPException(status_code=404, detail="No clients found.")
    return {"client_id": latest_client.id}


@app.post("/serviceplan/response/")
def save_response(request: Request,responses: str = Form(...),file: Optional[UploadFile] = File(None),db: Session = Depends(configs.get_db)):
    try:
        print(" Incoming POST request to /serviceplan/response/")
        print(" Responses received:", responses)
        # Get client_id
        session_client_id = request.session.get("client_id")
        if not session_client_id:
            raise HTTPException(status_code=400, detail="No client ID found in session.")
        
        # Fetch the corresponding client_id from the ClientNames table
        client_details = db.query(ClientDetails).filter(ClientDetails.id == session_client_id).first()
        if not client_details:
            raise HTTPException(status_code=404, detail="Client not found in ClientDetails table.")
        
        client_name_entry = db.query(ClientNames).filter(ClientNames.id == client_details.client_id).first()
        if not client_name_entry:
            raise HTTPException(status_code=404, detail="Client not found in ClientNames table.")
        

         # Use the id from ClientNames as the client_id for responses
        correct_client_id = client_name_entry.id
        print("Correct Client ID:", correct_client_id)

        # Use the CRUD function to save responses
        result = serviceplan.create_response(db, responses, file, correct_client_id)
        return JSONResponse(content=result, status_code=201)

    except Exception as e:
        print("❌ Error saving response:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

#GET: Fetch all questions with client responses
@app.get("/questions/", tags=["Annual Service Plan"])
def get_questions(client_id: int, db: Session = Depends(configs.get_db)):
    responses = annualplan.get_user_responses(db, client_id)
    for q in STATICQUESTIONS:
        q["response"] = next((r for r in responses if r["question_id"] == q["id"]), None)
    return STATICQUESTIONS

@app.post("/responses/", tags=["Annual Service Plan"])
def save_user_responses(responses: List[ClientResponseSchema], db: Session = Depends(configs.get_db)):
    if not responses:
        return {"message": "No responses provided. No changes were made."}

    result = annualplan.save_user_response(db, responses)
    return result

@app.get("/annualplan/", response_class=HTMLResponse)
def render_annual_plan_page(request: Request, db: Session = Depends(configs.get_db)):
    # Retrieve the client_id from the session
    session_client_id = request.session.get("client_id")
    if not session_client_id:
        raise HTTPException(status_code=400, detail="No client ID found in session.")

    # Fetch the corresponding client_id from the ClientNames table
    client_details = db.query(ClientDetails).filter(ClientDetails.id == session_client_id).first()
    if not client_details:
        raise HTTPException(status_code=404, detail="Client not found in ClientDetails table.")

    client_name_entry = db.query(ClientNames).filter(ClientNames.id == client_details.client_id).first()
    if not client_name_entry:
        raise HTTPException(status_code=404, detail="Client not found in ClientNames table.")

    # Use the id from ClientNames as the client_id for responses
    correct_client_id = client_name_entry.id

    # Fetch user responses for the client
    responses = annualplan.get_user_responses(db, correct_client_id)

    # Attach responses to the corresponding questions
    questions_with_responses = []
    for question in STATICQUESTIONS:
        question_response = next((r for r in responses if r["question_id"] == question["id"]), None)
        questions_with_responses.append({
            **question,
            "response": question_response
        })

    return templates.TemplateResponse("annualplan.html", {
        "request": request,
        "questions": questions_with_responses,  # Pass questions with responses
        "client_id": correct_client_id  # Pass the correct client_id to the frontend
    })

#Client details
# GET: Fetch available cover types
@app.get("/cover-types/", tags=["Client"])
def get_cover_types():
    return {"available_cover_types": COVER_TYPES}

@app.get("/client/", response_class=HTMLResponse, tags=["Client"])
def get_client_page(request: Request):
    return templates.TemplateResponse("client.html", {"request": request})

# Get all clients
@app.get("/clients/", response_model=list[ClientCreateSchema],tags=["Client"])
def get_clients(db: Session = Depends(configs.get_db)):
    return client.get_clients(db)

@app.get("/clients/names")
def fetch_client_names(db: Session = Depends(configs.get_db)):
    return client.get_client_names(db)

@app.get("/clients/{client_id}", response_model=ClientCreateSchema,tags=["Client"])
def get_client(client_id: int, db: Session = Depends(configs.get_db)):
    client = client.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

# Update a client subject to change
@app.put("/clients/{client_id}", response_model=ClientCreateSchema, tags=["Client"])
def update_client(client_id: int, client: ClientCreateSchema, db: Session = Depends(configs.get_db)):
    updated_client = client.update_client(db, client_id, client)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated_client

@app.delete("/clients/{client_id}", tags=["Client"])
def delete_client(client_id: int, db: Session = Depends(configs.get_db)):
    if not client.delete_client(db, client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted successfully"}


@app.post("/clients/", tags=["Client"])
def create_client(
    request: Request,  # Add request parameter to access the session
    client_name: str = Form(...),
    relationship_manager: str = Form(...),
    co_handler: str = Form(...),
    policy_period: str = Form(...),
    premium: str = Form(...),
    admin_fee: str = Form(...),
    income: str = Form(...),
    cover_type: Literal["Insured", "Hybrid", "Funded"] = Form(...),
    non_government: bool = Form(False),
    government: bool = Form(False),
    client_main_contact: str = Form(...),
    client_designation: str = Form(...),
    client_cell: str = Form(...),
    client_email: EmailStr = Form(...),
    db: Session = Depends(configs.get_db)  # Ensure you have a get_db function defined
):
    # Check if the client name exists in ClientNames
    client_name_entry = db.query(ClientNames).filter(ClientNames.client_name == client_name).first()

    if not client_name_entry:
        # If the client name doesn't exist, create a new entry
        client_name_entry = ClientNames(client_name=client_name)
        db.add(client_name_entry)
        db.commit()
        db.refresh(client_name_entry)

    # Create and save the new client details
    new_client = ClientDetails(
        relationship_manager=relationship_manager,
        co_handler=co_handler,
        policy_period=policy_period,
        premium=premium,
        admin_fee=admin_fee,
        income=income,
        cover_type=cover_type,
        non_government=non_government,
        government=government,
        client_main_contact=client_main_contact,
        client_designation=client_designation,
        client_cell=client_cell,
        client_email=client_email,
        client_id=client_name_entry.id  # Associate with the ClientNames entry
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    # Store the client name in the session
    request.session["client_id"] = new_client.id  # Store the client ID in the session for later use

    return {"message": "Client created successfully", "client": new_client}

#Login Functionality
# Route to display login page
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route to handle login request
@app.post("/login", status_code=status.HTTP_200_OK, tags=["Login"])
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(configs.get_db)):
    try:
        response_data = authenticate_user(db, username, password)

        if response_data["message"] == "Login successful":
            return templates.TemplateResponse("login.html", {
                "request": request,
                "response_data": response_data,
                "login_success": True  # Used in JavaScript for redirection
            })

    except HTTPException as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_message": str(e.detail)
        })

#client extra details
@app.get("/xtraclient", response_class=HTMLResponse)
def extra_client_details_form(request: Request):
    return templates.TemplateResponse("xtraclient.html", {"request": request})

@app.get("/get_client_name/")
def get_client_name(request: Request, db: Session = Depends(configs.get_db)):
    client_id = request.session.get("client_id")
    if not client_id:
        return {"client_name": "Unknown Client"}

    client = db.query(ClientDetails).filter(ClientDetails.id == client_id).first()
    if not client:
        return {"client_name": "Unknown Client"}

    client_name_entry = db.query(ClientNames).filter(ClientNames.id == client.client_id).first()
    if not client_name_entry:
        return {"client_name": "Unknown Client"}

    return {"client_name": client_name_entry.client_name}

# Get all extra clients
@app.get("/xtraclients/", response_model=list[ExtraClientDetailsSchema],tags=["Client"])
def get_clients(db: Session = Depends(configs.get_db)):
    return client.get_xtraclients(db)

@app.get("/xtraclients/{client_id}", response_model=ExtraClientDetailsSchema,tags=["Client"])
def get_client(client_id: int, db: Session = Depends(configs.get_db)):
    client = client.get_xtraclient_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

# Update a extra client
@app.put("/xtraclients/{client_id}", response_model=ExtraClientDetailsSchema, tags=["Client"])
def update_client(client_id: int, client: ExtraClientDetailsSchema, db: Session = Depends(configs.get_db)):
    updated_client = client.update_xtraclient(db, client_id, client)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated_client

@app.delete("/xtraclients/{client_id}", tags=["Client"])
def delete_client(client_id: int, db: Session = Depends(configs.get_db)):
    if not client.delete_xtraclient(db, client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted successfully"}

# Create new extra client details
@app.post("/extra_client_details/", tags=["Client"])
def create_extra_client_details_endpoint(
    request: Request,
    client_name: str = Form(...),
    other_client_personel: List[Optional[str]] = Form(...),
    designation: List[Optional[str]] = Form(...),
    cell: List[Optional[str]] = Form(...),
    email: List[Optional[str]] = Form(...),
    db: Session = Depends(configs.get_db),
):
    # Fetch the client_id based on the provided client_name
    client_name_entry = db.query(ClientNames).filter(ClientNames.client_name == client_name).first()
    if not client_name_entry:
        raise HTTPException(status_code=400, detail="Invalid client name provided.")

    client_id = client_name_entry.id

    data_inserted = False  # Track if any data is entered

    try:
        # Loop over multiple form entries and insert only if there's input
        for i in range(len(other_client_personel)):
            if any([other_client_personel[i], designation[i], cell[i], email[i]]):  # Check if any field has data
                extra_client_data = ExtraClientDetails(
                    client_id=client_id,
                    other_client_personel=other_client_personel[i] or None,
                    designation=designation[i] or None,
                    cell=cell[i] or None,
                    email=email[i] or None,
                )
                db.add(extra_client_data)
                data_inserted = True  # Mark that we inserted some data

        db.commit()

        if data_inserted:
            return JSONResponse(content={"message": "Data submitted successfully"}, status_code=201)
        else:
            return JSONResponse(content={"message": "No data input, but proceeding..."}, status_code=200)

    except Exception as e:
        db.rollback()
        print("Database error:", str(e))
        raise HTTPException(status_code=500, detail="Database error occurred.")


    
#Signout Functionality
@app.get("/signout", response_class=HTMLResponse)
def signout_page(request: Request):
    return templates.TemplateResponse("signout.html", {"request": request})

@app.get("/signoffs/", response_model=list[SignOutSchema])
def list_sign_offs(db: Session = Depends(configs.get_db)):
    return signout.get_sign_offs(db)

@app.post("/signoffs/confirm/{role}/", response_model=SignOutSchema)
def confirm_sign_off(role: str, confirmed_by: str, db: Session = Depends(configs.get_db)):
    updated_sign_off = signout.confirm_sign_off(db, role, confirmed_by)
    if not updated_sign_off:
        raise HTTPException(status_code=404, detail="Role not found")
    return updated_sign_off

@app.get("/signoffs/confirm-email/")
def confirm_via_email(token: str, db: Session = Depends(configs.get_db)):
    """Confirms sign-off when user clicks the email link."""
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        role = decoded["role"]
        confirmed_by = decoded["confirmed_by"]

        return signout.confirm_sign_off(db, role, confirmed_by)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Confirmation link expired.")
    except jwt.DecodeError:
        raise HTTPException(status_code=400, detail="Invalid confirmation link.")

