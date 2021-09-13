from sqlalchemy import BigInteger, Boolean, String, Column, ForeignKey, Integer, String, DateTime, Text
# from sqlalchemy.orm import relationship
import datetime

from .database import Base

class IPSubnet(Base):
    __tablename__ = 'ip_subnet'
    
    id = Column(Integer, primary_key=True, index=True)
    # 子网段数值(此处为str类型, 用ipaddress.IPv4Network生成)
    value = Column(String(length=18), nullable=False, unique=True)
    describe = Column(Text(length=64))

class IPAddress(Base):
    __tablename__ = 'ip_address'

    id = Column(Integer, primary_key=True, index=True)

    subnet_id = Column(Integer, ForeignKey("ip_subnet.id"))

    # ip地址数值(ip转int)
    value = Column(BigInteger, nullable=False) # value允许重复，因为所属的subnet_id可能相同
    usable = Column(Boolean, nullable=True, default=True)
    describe = Column(Text(length=64))

    device_id = Column(Integer, ForeignKey("device.id"))

class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, index=True)

    serial_number = Column(String(length=32), unique=True)
    public_port = Column(Integer)
    mapping_port = Column(Integer)

    usable = Column(Boolean, default=True)
    shelf_time = Column(DateTime, default=datetime.datetime.now())


    created_time = Column(DateTime, default=datetime.datetime.now())
    
class DeviceDescribeHistory(Base):
    __tablename__ = "device_describe_history"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(Integer, ForeignKey("device.id"))

    last_update = Column(DateTime, default=datetime.datetime.now())
    history = Column(Text(length=1024))

class SSHAccount(Base):
    __tablename__ = "ssh_account"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=16), nullable=False)
    password = Column(String(length=32), nullable=False)
    private_key = Column(Text(length=1024))
    public_key = Column(Text(length=1024))
    
    device_id = Column(Integer, ForeignKey("device.id"))
    
class Note(Base):
    __tablename__ = "note"

    id = Column(Integer, primary_key=True, index=True)

    account_id = Column(Integer, ForeignKey("admin_account.id"))

    title = Column(String(length=32), nullable=False)
    last_update = Column(DateTime, default=datetime.datetime.now())
    content = Column(Text(length=1024))

class AdminAccount(Base):
    __tablename__ = "admin_account"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(length=32), nullable=False, unique=True)
    password = Column(String(length=32))
    is_super_admin = Column(Boolean, default=False)
    last_login = Column(DateTime, default=datetime.datetime.now())
    token = Column(String(length=1024))

