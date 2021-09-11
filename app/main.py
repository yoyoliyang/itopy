from fastapi import Depends, FastAPI

from sqlalchemy.orm import Session

from .crud import ip
from .sql_app.database import SessionLocal, engine
from .sql_app import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/subnet/", response_model=schemas.IPSubnetCreate)
def create_subnet(subnet: schemas.IPSubnetCreate, db: Session=Depends(get_db)):
    return ip.create_subnet(db=db, subnet=subnet)

@app.get("/subnet/{value}", response_model=schemas.IPSubnet)
def get_subnet_by_value(value: str, db: Session=Depends(get_db)):
    db_subnet = ip.get_subnet_by_value(db=db, _value=value)
    return db_subnet
