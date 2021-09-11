from typing import Dict, Any

from fastapi.responses import JSONResponse
from fastapi import status

class ResponseData:
    # 封装响应信息
    def __init__(self, status_code: int, status_msg: str, data: Dict[str,Any]):
        """注意此处的status_code为fastapi中的status响应码属性
        status_msg为字符串比如"success" 或 "failure"
        data为字典数据，保存返回的响应具体信息比如：{'error': '发送的数据不符合ip地址规范'}
        """
        self.status_code = status_code
        self.status_msg = status_msg
        self.data = data

    def response(self):
        """ 根据status来生成不同的响应字典 """
        resp = {} # 保存响应数据
        if self.status_code == status.HTTP_201_CREATED:
            resp = {
                'status': self.status_msg, 
                'data': self.data
                }
        elif self.status_code == status.HTTP_400_BAD_REQUEST or self.status_code == status.HTTP_404_NOT_FOUND:
            resp = {
                'error': self.status_msg,
                'data': self.data
                }
        elif self.status_code == status.HTTP_201_CREATED:
            resp = {
                'status': self.status_msg,
                'data': self.data
                }
        return JSONResponse(content=resp, status_code=self.status_code)


