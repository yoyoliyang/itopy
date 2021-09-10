# 处理device设备响应

from sqlalchemy.orm import Session

from ..sql_app import models, schemas
from .response import ResponseData

import ipaddress
from ipaddress import AddressValueError, NetmaskValueError

from fastapi import status

"""
{
id: 1,
value: '192.168.0.0/24',
describe: '192 subnet for dell server',
items: ['192.168.0.1/24', '192.168.0.2/24', ...]
}
"""
def create_subnet(db: Session, subnet: schemas.IPSubnetCreate):
    try:
        network = ipaddress.IPv4Network(subnet.value)
        # 注意此处将network转换为整数
        value = int(ipaddress.IPv4Interface(network))
        # 插入前查询

        result = db.query(models.IPSubnet).filter(models.IPSubnet.value == value).first()
        if value == result.value:
            response = ResponseData(status.HTTP_400_BAD_REQUEST,
                    'Duplicate entry',
                    {'duplicate entry': f'{network.exploded} with value {value} already created'})
            return response.response()

        db_subnet = models.IPSubnet(value=value, describe=subnet.describe)
        db.add(db_subnet)
        db.commit()
        db.refresh(db_subnet)
        response = ResponseData(status.HTTP_201_CREATED,
                'success',
                {'created': network.exploded})
        return response.response()

    except AddressValueError as e:
        # 地址不规范的处理
        response = ResponseData(status.HTTP_400_BAD_REQUEST,
                'error subnet format',
                {"detail": 
                    f"format error with <{e}>"
                })
        return response.response()
    except NetmaskValueError as e:
        response = ResponseData(status.HTTP_400_BAD_REQUEST,
                'error subnet format',
                {"detail": 
                    f"format error with: <{e}>"
                })
        return response.response()

