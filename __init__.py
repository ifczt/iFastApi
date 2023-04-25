# Author: IFCZT
# Email: ifczt@qq.com
import atexit

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .db import DBManager


class IFastAPI:
    """
    config: 配置文件
        - ORIGINS: 允许跨域的域名 默认为'*'
    """

    def __init__(self, config):
        self.config = config
        self.app = FastAPI()
        self.setup()
        atexit.register(self.shutdown)

    def setup(self):
        self.setup_config()
        self.setup_db()

    def setup_config(self):
        """配置config"""
        origins = self.config.ORIGINS  # 允许跨域的域名
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=origins,
            allow_headers=origins,
        )

    def setup_db(self):
        """配置数据库"""
        _db = DBManager()
        _db.setup(self.config)
        _db.base.metadata.create_all(bind=_db.engine)

    def shutdown(self):
        """关闭数据库连接"""
        print("关闭数据库连接")
        DBManager().shutdown()

    def run(self):
        uvicorn.run(**self.config.SERVER_CONFIG)
