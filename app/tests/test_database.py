from sqlalchemy import text
from sql_app.database import SessionLocal as db
from sql_app.database import engine
from sqlalchemy.orm import Session 
import sql_app.models as models

import ipaddress

models.Base.metadata.create_all(bind=engine)

def session(func):
    """ 传递session到测试函数 """ 
    with db.begin() as session:
        def wrap():
            func(session)
        return wrap
   
@session
def test_db_connect(s: Session):
    """数据库连接测试"""
    _ = s.execute(text("show tables"))
    
@session
def test_insert_device(s: Session):
    import random
    d1 = models.Device(id=None, serial_number=random.randint(1,100),
            public_port=8080, mapping_port=80)
    s.add(d1)
    s.commit()

@session
def test_insert_ssh_account(s: Session):
    s1 = models.SSHAccount(id=None, device_id=1, username='root', password='somepswd')
    s.add(s1)
    s.commit()

@session
def test_insert_admin_account(s: Session):
    a1 = models.AdminAccount(id=None, email="yoyoliyang@gmail.com",
            password="fakepswd",
            is_super_admin=True)
    s.add(a1)
    s.commit()

@session
def test_insert_describe(s: Session):
    des1 = models.DeviceDescribeHistory(id=None, device_id=1, history="some device describe")
    s.add(des1)
    s.commit()

@session
def test_insert_note(s: Session):
    note1 = models.Note(id=None,title='first note', account_id=1, content="note content")
    s.add(note1)
    s.commit()

@session
def test_insert_ipsub(s: Session):
    ip_inte_192 = ipaddress.IPv4Interface('192.168.0.0/24')
    sub1 = models.IPSubnet(id=None, value=int(ip_inte_192), describe='192 subnet')
    s.add(sub1)
    s.commit()

@session
def test_insert_ip(s: Session):
    ip123 = models.IPAddress(id=None, subnet_id=1, 
            value=int(ipaddress.IPv4Address('192.168.0.123')),
            usable=True,
            describe="dell server ipaddress",
            device_id=1)
    s.add(ip123)
    s.commit()
