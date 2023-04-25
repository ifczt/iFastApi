# Author: IFCZT
# Email: ifczt@qq.com

from threading import local

from sqlalchemy import Column, Integer, SmallInteger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from .BaseQuery import BaseQuery
from ..utils.singleton import Singleton
from ..utils.time import time as t


@Singleton
class DBManager:
    base = declarative_base()

    def __init__(self):
        self._local = None
        self._engine = None

    def setup(self, config):
        if not config.SQLALCHEMY_DATABASE_URI:
            raise Exception('数据库连接地址未配置')

        self._engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

    @property
    def engine(self):
        if not self._engine:
            raise Exception('数据库未连接')
        return self._engine

    def get_session(self):
        """
        获取当前线程的会话对象
        """
        if not self._local:
            self._local = local()
        if not hasattr(self._local, "session"):
            session_factory = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
            self._local.session = scoped_session(session_factory, scopefunc=lambda: id(self._local))
        return self._local.session()

    def close_session(self):
        """
        关闭当前线程的会话对象
        """
        if hasattr(self._local, "session"):
            self._local.session.commit()
            self._local.session.close()
            self._local.session.remove()

    async def shutdown(self):
        session = self.get_session()
        session.commit()
        session.close()
        self._local = None
        print("退出数据库连接")


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

    def dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

    @classmethod
    def get_id(cls, ident):
        result = DBManager().get_session().query(cls).get(ident)
        result = result.dict() if result else None
        return result
