import binascii
import os
from datetime import datetime

import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .iResponse import Error, HTTPStatus
from .globals import g

print(binascii.hexlify(os.urandom(24)))
SECRET_KEY = "4105177d86fa16a2747212a7101dafda5c4027a4e4f64054"  # 密钥
ALGORITHM = "HS256"  # 算法


class JWTBearer(HTTPBearer):
    def __init__(self, rules=None, auto_error: bool = False):
        self.rules = rules
        super(JWTBearer, self).__init__(auto_error=auto_error)

    @staticmethod
    def token(data: dict, expires_time=None):
        if expires_time is None:
            expires_time = g.config.get('ACCESS_TOKEN_EXPIRES')
            if expires_time is None:
                raise Error(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, message="未设置ACCESS_TOKEN_EXPIRES")
        exp = datetime.utcnow() + expires_time  # expire 令牌到期时间
        data.update({"exp": exp})
        __token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return __token

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise Error(status_code=HTTPStatus.FORBIDDEN, message="无效的身份验证方案。")
            account_info = JWTBearer.verify_jwt(credentials.credentials)
            if not account_info:
                raise Error(status_code=HTTPStatus.FORBIDDEN, message="无效令牌或过期令牌。")
            JWTBearer.verify_type(self.rules, account_info)
            g.u_id = account_info.get('u_id')
            return account_info
        else:
            raise Error(status_code=HTTPStatus.FORBIDDEN, message="无效的授权代码。")

    # 验证token
    @staticmethod
    def verify_jwt(jwtoken: str) -> dict:
        # noinspection PyBroadException
        try:
            jwtoken = jwtoken.strip()
            load_data = jwt.decode(jwtoken, SECRET_KEY, algorithms=[ALGORITHM])
        except Exception:
            load_data = {}
        return load_data

    # 验证用户权限
    @staticmethod
    def verify_type(rules, account_info):
        _type = account_info.get('type')
        if _type not in rules:
            raise Error(status_code=HTTPStatus.FORBIDDEN, message="权限不足，拒绝继续访问")
