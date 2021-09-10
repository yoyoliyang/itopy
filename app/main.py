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
