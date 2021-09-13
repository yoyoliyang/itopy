# api模型框架
import typing as t 
from datetime import datetime

from pydantic import BaseModel

class IPBase(BaseModel):
    """ IP地址基类, 保存id 值 描述 """
    id: int
    """ api接口处为str，实际通过create函数会将其转换为整数, 数据库字段类型为int类型
        但排除subnet，subnet为ipaddress.IPv4Network生成的字符串，保留了掩码位
    """
    value: str 
    describe: t.Union[str, None] # 增加None值避免空数据造成的pydantic检查错误
    class Config:
        orm_mode = True

class IPAddress(IPBase):
    subnet_id: int

    usable: bool = True

    device_id: t.Union[int, None] 

    class Config:
        orm_mode = True


class IPSubnet(IPBase):
    # 子网ip范围
    items: t.List[IPAddress] = []
    class Config:
        orm_mode = True
class IPSubnetCreate(IPBase):
    """ POST 类提供给api结构调用 """
    pass
class IPSubnetGet(BaseModel):
    """ GET 类提供给api结构调用 """
    item: t.List[IPBase] = []
    class Config:
        orm_mode = True
class IPSubnetUpdate(BaseModel):
    """ PUT 类 """
    describe: t.Union[str, None]

class AccountBase(BaseModel):
    id: int
    password: str

class SSHAccount(AccountBase):
    username: str
    private_key: str
    public_key: str
    
    device_id: t.Union[int, None]
    class Config:
        orm_mode =True
    
class DeviceDescribeHistory(BaseModel):
    """ device 描述记录(history) """
    id: int

    device_id: int 

    last_update: datetime
    history: str 

class Device(BaseModel):
    """ Device 设备接口 """
    id: int

    serial_number: str 
    public_port: int
    mapping_port: int

    usable: bool = True
    shelf_time: datetime

    created_time: datetime

    # 设备描述（历史日志）
    describe: t.List[DeviceDescribeHistory] = []
    # 拥有的ip地址 
    owned_ip: t.List[IPAddress] = []
    # 所属网段
    network: str
    # 拥有ssh account
    owned_ssh_account: t.List[SSHAccount] = []

    class Config:
        orm_mode = True

class AdminAccount(AccountBase):
    email: str
    is_super_admin: bool = False
    last_login: datetime 
    token: str
    class Config:
        orm_mode =True

class NoteBase(BaseModel):
    """ 记事本 """
    id: int

    account_id: int

    title: str
    last_update: datetime
    content: str 

class Notes(NoteBase):
    items: t.List[NoteBase]
    class Config:
        orm_mode =True
