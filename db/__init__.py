# Author: IFCZT
# Email: ifczt@qq.com
import re
from threading import local
from urllib.parse import urlparse

from starlette.requests import Request

from sqlalchemy import Column, Integer, SmallInteger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from ..utils import path_to_key
from .BaseQuery import BaseQuery
from ..utils.singleton import Singleton
from ..utils.time import time as t


@Singleton
class DBManager:
    base = declarative_base()

    def __init__(self):
        self._session_factory = None
        self._local = None
        self._engine = None

    def setup(self, config):
        if not config.SQLALCHEMY_DATABASE_URI:
            raise Exception('数据库连接地址未配置')

        self._engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        self._session_factory = sessionmaker(bind=None, autocommit=False, autoflush=False)

    def auto(self, request: Request):
        """
        自动生成会话对象 自动生成、关闭会话对象
        """

        path = path_to_key(request.url.path)
        try:
            yield self.get_session()
        finally:
            self.close_session()

    @property
    def engine(self):
        if not self._engine:
            raise Exception('数据库未连接')
        return self._engine

    @engine.setter
    def engine(self, database_uri):
        self._engine = create_engine(database_uri)

    def get_session(self):
        """
        获取当前线程的会话对象
        """
        if not self._local:
            self._local = local()
        if not hasattr(self._local, "session"):
            self._session_factory.configure(bind=self.engine)
            self._local.session = scoped_session(self._session_factory, scopefunc=lambda: id(self._local))
        return self._local.session()

    @property
    def session(self):
        return self.get_session()

    def close_session(self):
        """
        关闭当前线程的会话对象
        """
        if hasattr(self._local, "session"):
            self._local.session.commit()
            self._local.session.close()
            self._local.session.remove()
            del self._local.session

    async def shutdown(self):
        self.close_session()


class BaseDB(DBManager.base):
    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    create_time = Column(Integer, comment='生成时间')
    status = Column(SmallInteger, default=1, comment='是否软删除 0 / 1')

    def __init__(self, *args, **kwargs):
        self.set_attrs(kwargs)
        self.create_time = t.int_time(modes="ms")

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    @classmethod
    @property
    def db(cls):
        return DBManager().session

    @classmethod
    @property
    def query(cls):
        return cls.db.query(cls)

    def dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

    @classmethod
    def get_id(cls, ident):
        result = cls.query.get(ident)
        result = result.dict() if result else None
        return result
