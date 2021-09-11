# 处理device设备响应

from sqlalchemy.orm import Session

from ..sql_app import models, schemas
from .response import ResponseData

import ipaddress
from ipaddress import AddressValueError, NetmaskValueError
from typing import Union

from fastapi import status


def response_err(e: Union[AddressValueError, NetmaskValueError]) -> ResponseData:
    """ 封装错误信息，提供给下面的异常处理"""
    response_err = ResponseData(status.HTTP_400_BAD_REQUEST,
                'error subnet format',
                {"detail": 
                    f"错误的ip地址格式: <{e}>"
                })

    return response_err

def with_exception_decorator(func):
    """ 封装异常处理的装饰器函数 """
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
def get_subnet_by_value(db: Session, _value: str):
    """
    url: /subnet/{value}
    value: 格式为192.168.0.0
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

    ip_interface = ipaddress.IPv4Interface(_value)
    value = int(ip_interface)
    network = ipaddress.IPv4Network(ip_interface)

    result = db.query(models.IPSubnet).filter(models.IPSubnet.value == value).first()
    if result:
        response = schemas.IPSubnet(
                id = result.id, 
                value = result.value,
                describe = result.describe
                )

        # 根据result.id获取对应的ip items
        owned_ip = db.query(models.IPAddress).filter(models.IPAddress.subnet_id == result.id).all()
        response.items = [ip for ip in owned_ip]
        print(response.items)
        return response

    response = ResponseData(status.HTTP_404_NOT_FOUND,
            'error',
            {'not found': f'没有找到对应的子网 <{network.exploded}>'})
    return response.response()

@with_exception_decorator
def create_subnet(db: Session, subnet: schemas.IPSubnetCreate):
    """
    url: /subnet/
    post json数据结构
    {
      "id": 0,
      "value": "string",
      "describe": "string"
    }
    """
    ip_interface = ipaddress.IPv4Interface(subnet.value)
    # 注意此处将network转换为整数
    value = int(ipaddress.IPv4Interface(ip_interface))
    network = ipaddress.IPv4Network(ip_interface)

    # 插入前查询
    result = db.query(models.IPSubnet).filter(models.IPSubnet.value == value).first()
    if result:
        if value == result.value:
            response = ResponseData(status.HTTP_400_BAD_REQUEST,
                    'Duplicate entry',
                    {'duplicate entry': f'{ip_interface.exploded} with value {value} already created'})
            return response.response()

    # 注意此处用户提交id的时候，并不会影响到数据库的自增id编号
    db_subnet = models.IPSubnet(value=value, describe=subnet.describe)
    db.add(db_subnet)
    db.commit()

    # 根据ip subnet获取所有ip地址并更新到数据库
    # 获取到对应id
    result = db.query(models.IPSubnet).filter(models.IPSubnet.value == value).first()
    for ip in network:
        db_ipaddr = models.IPAddress(value=int(ip), 
                subnet_id=result.id)
        db.add(db_ipaddr)
    db.commit() 

    db.refresh(db_subnet)

    response = ResponseData(status.HTTP_201_CREATED,
            'success',
            {'created': f'{ip_interface.exploded} with all ipaddress'})
    return response.response()

