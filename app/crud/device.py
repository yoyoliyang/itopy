# 处理device设备响应

from sqlalchemy.orm import Session

from ..sql_app import models, schemas

def create_device(db: Session, device: schemas.Device):
    pass
    
