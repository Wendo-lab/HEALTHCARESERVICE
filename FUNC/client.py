from sqlalchemy.orm import Session
from models import ClientDetails,ExtraClientDetails,ClientNames
from schemas import ClientCreateSchema, ExtraClientDetailsSchema

# Create a new client subject to change
def create_client(db: Session, client_data: dict):  # Use dict instead of Pydantic model here
    existing_client = db.query(ClientDetails).filter(ClientDetails.client_name == client_data["client_name"]).first()
    if existing_client:
        return {"redirect": "/annualplan/"}  # Redirect to /annualplan/ if client exists
    
    new_client = ClientDetails(**client_data)  # Pass the dictionary directly to ClientDetails
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

# Get all clients
# Fetch only client names from the clientnames table
def get_client_names(db: Session):
    return {"clients": [client.client_name for client in db.query(ClientNames).all()]}

# Get a single client by ID
def get_client_by_id(db: Session, client_id: int):
    return db.query(ClientDetails).filter(ClientDetails.id == client_id).first()

# Update a client
def update_client(db: Session, client_id: int, updated_data: ClientCreateSchema):
    client = db.query(ClientDetails).filter(ClientDetails.id == client_id).first()
    if client:
        for key, value in updated_data.dict().items():
            setattr(client, key, value)
        db.commit()
        db.refresh(client)
        return client
    return None

# Delete a client
def delete_client(db: Session, client_id: int):
    client = db.query(ClientDetails).filter(ClientDetails.id == client_id).first()
    if client:
        db.delete(client)
        db.commit()
        return True
    return False








#function to create new extra client details
def create_extra_client_details(db: Session, extra_client_data: dict):
    new_extra_client = ExtraClientDetails(**extra_client_data)
    db.add(new_extra_client)
    db.commit()
    db.refresh(new_extra_client)
    return new_extra_client  # Return the new object (optional, you can return a success message too)

# Get all clients
def get_xtraclients(db: Session):
    return db.query(ExtraClientDetails).all()

# Get a single client by ID
def get_xtraclient_by_id(db: Session, client_id: int):
    return db.query(ExtraClientDetails).filter(ExtraClientDetails.client_id == client_id).first()

# Update a client
def update_xtraclient(db: Session, client_id: int, updated_data: ExtraClientDetailsSchema):
    client = db.query(ExtraClientDetails).filter(ExtraClientDetails.client_id == client_id).first()
    if client:
        for key, value in updated_data.dict().items():
            setattr(client, key, value)
        db.commit()
        db.refresh(client)
        return client
    return None

def delete_xtraclient(db: Session, client_id: int):
    client = db.query(ExtraClientDetails).filter(ExtraClientDetails.client_id == client_id).first()
    if client:
        db.delete(client)
        db.commit()
        return True
    return False
   

