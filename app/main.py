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
def get_subnet_by_value(value: str, skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    items = ip.get_subnet_by_value(db=db, _value=value, skip=skip, limit=limit)
    return items

@app.get("/subnet/", response_model=schemas.IPSubnetGet)
def get_subnet(skip: int=0, limit: int=10, db: Session=Depends(get_db)):
    items = ip.get_subnet(db=db, skip=skip, limit=limit) 
    return items

@app.put("/subnet/{value}")
def update_subnet_by_value(subnet: schemas.IPSubnetUpdate, value: str, db:Session=Depends(get_db)):
    r = ip.update_subnet(db=db, _value=value, subnet=subnet)
    print(r)
    return r
