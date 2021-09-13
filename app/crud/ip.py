# 处理device设备响应

from sqlalchemy.orm import Session

from ..sql_app import models, schemas
from .response import ResponseData

import ipaddress
from ipaddress import AddressValueError, NetmaskValueError
from typing import Union

from fastapi import status

def ipswap(ipaddr: schemas.IPAddress) -> schemas.IPAddress:
    """ 转换数据库中获取的ip整数value为字符串 """
    addr = ipaddress.IPv4Address(ipaddr.value)
    ipaddr.value = addr.exploded
    return ipaddr

def response_err(e: Union[AddressValueError, NetmaskValueError]) -> ResponseData:
    """ 封装错误信息，提供给下面的异常处理"""
    response_err = ResponseData(status.HTTP_400_BAD_REQUEST,
                'error subnet format',
                {"detail": 
                    f"错误的ip地址格式: <{e}>"
                })

    return response_err

def with_exception_decorator(func):
    """ 封装ip地址转换或输入错误导致的异常处理的装饰器函数 """
    def wrapper(*args, **kwargs):
        try:
            func_result = func(*args, **kwargs)
            return func_result
        except AddressValueError as e:
            # 地址不规范的处理
            response = response_err(e)
            return response.response()
        except NetmaskValueError as e:
            response = response_err(e)
            return response.response()
    return wrapper

@with_exception_decorator
def get_subnet_by_value(db: Session, _value: str, skip: int=0, limit: int=100):
    """
    url: /subnet/{value}
    value: 格式为ip_netmask ex: 192.168.0.0_24
    get json数据结构
    {
      "id": 0,
      "value": "string",
      "describe": "string",
      "items": [
          {
          "id": 258,
          "value": "16777216",
          "describe": null,
          "subnet_id": 15,
          "usable": true,
          "device_id": null
        },
        ...
      ]
    }
    """

    ip_value = '/'.join(_value.split('_')) # ip地址下划线格式转换
    ip_network = ipaddress.IPv4Network(ip_value)

    result = db.query(models.IPSubnet).filter(models.IPSubnet.value == ip_network.exploded).first()
    if result:
        response = schemas.IPSubnet(
                id = result.id, 
                value = result.value,
                describe = result.describe
                )

        # 根据result.id获取对应的ip items
        owned_ip = db.query(models.IPAddress).\
                filter(models.IPAddress.subnet_id == result.id).\
                offset(skip).limit(limit).all()
        # 追加items返回对应的response结构
        response.items = [ipswap(ip) for ip in owned_ip]
        return response

    response = ResponseData(status.HTTP_404_NOT_FOUND,
            'error',
            {'not found': f'没有找到对应的子网 <{ip_network.exploded}>'})
    return response.response()

def get_subnet(db: Session, skip: int=0, limit: int=10):
    """
    url: /subnet/
    GET json数据结构
    {
        "id": 0,
        "value": "string",
        "describe": "string"
    }
    """
    items = db.query(models.IPSubnet).offset(skip).limit(limit).all()
    if items:
        response = schemas.IPSubnetGet()
        response.item = items
        return response
    response = ResponseData(status.HTTP_404_NOT_FOUND,
            'error',
            {'not found': 'no subnets were created.'})
    return response

@with_exception_decorator
def create_subnet(db: Session, subnet: schemas.IPSubnetCreate):
    """
    # 创建一个ip network(ex: 192.168.0.0/24)
    url: /subnet/
    post json数据结构
    {
      "id": 0,
      "value": "string",
      "describe": "string"
    }
    """
    network = ipaddress.IPv4Network(subnet.value)

    # 插入前查询
    result = db.query(models.IPSubnet).filter(models.IPSubnet.value == network.exploded).first()
    if result:
        if network.exploded == result.value:
            response = ResponseData(status.HTTP_400_BAD_REQUEST,
                    'Duplicate entry',
                    {'duplicate entry': f'{network.exploded} already created'})
            return response.response()

    # 注意此处用户提交id的时候，并不会影响到数据库的自增id编号
    db_subnet = models.IPSubnet(value=network.exploded, describe=subnet.describe)
    db.add(db_subnet)
    db.commit()

    # 根据ip subnet获取所有ip地址并更新到数据库
    # 获取到对应id
    result = db.query(models.IPSubnet).filter(models.IPSubnet.value == network.exploded).first()
    for ip in network:
        db_ipaddr = models.IPAddress(value=int(ip), 
                subnet_id=result.id)
        db.add(db_ipaddr)
    db.commit() 

    db.refresh(db_subnet)

    response = ResponseData(status.HTTP_201_CREATED,
            'success',
            {'created': f'{network.exploded} with IP range <{network[0]}~{network[-1]}> created'})
    return response.response()

@with_exception_decorator
def update_subnet(db: Session, _value: str, subnet: schemas.IPSubnetUpdate):
    """
    url: /subnet/
    put json数据结构 # 更新subnet，只能更新describe
    {
      "describe": "string"
    }
    """
    ip_value = '/'.join(_value.split('_')) # ip地址下划线格式转换
    network = ipaddress.IPv4Network(ip_value)

    # 插入前查询
    result = db.query(models.IPSubnet).filter(models.IPSubnet.value == network.exploded).first()
    if result:
        update_info = db.query(models.IPSubnet).filter(models.IPSubnet.id == result.id).\
                update({"describe": subnet.describe}, synchronize_session="fetch")
        db.commit()
        response = ResponseData(status.HTTP_201_CREATED,
                'success',
                {'updated': f'{network.exploded} was updated: <{update_info}>'})
        return response
    response = ResponseData(status.HTTP_400_BAD_REQUEST,
            'not found',
            {"detail": 
                f"not found network with {network.exploded}"
            })
    return response
