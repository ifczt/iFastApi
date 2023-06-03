# Author: IFCZT
# Email: ifczt@qq.com
import re
from threading import local

from starlette.requests import Request

from sqlalchemy import Column, Integer, SmallInteger, text, and_
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from ..utils.toolfuns import path_to_key
from ..utils.iResponse import  Error
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
        self._session_factory = sessionmaker(bind=None, autocommit=False, autoflush=False, query_cls=BaseQuery)

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

    def execute(self, sql, execute_type='read'):
        """执行sql语句"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            if execute_type == 'read':
                return result
            elif execute_type == 'write':
                conn.commit()
                return result.lastrowid

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
    fileds = []

    def __init__(self, *args, **kwargs):
        self.set_attrs(kwargs)
        self.create_time = t.int_time(modes="s")

    '''输出dict 相关方法'''

    def __getitem__(self, item):
        return getattr(self, item)

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def keys(self):
        return self.fileds

    def hide(self, *keys):
        for key in keys:
            self.fileds.remove(key)
        return self

    def append(self, *keys):
        for key in keys:
            self.fileds.append(key)
        return self

    '''输出dict 相关方法'''

    @property
    def create_datetime(self):
        # 将时间戳转换为时间
        if self.create_time:
            return t.format_time(self.create_time)
        else:
            return None

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
    def get_id(cls, ident, result_dict=None):
        result = cls.query.get(ident)
        result.fileds = result_dict or result.fileds
        return dict(result or {})

    @classmethod
    def get_list(cls, page=1, size=20, query_dict=None, order_by=None):
        """
        获取列表
        :param page: 页码
        :param size: 每页数量
        :param query_dict: 查询条件
        :param order_by: 排序 id^ = id desc id = id asc
        """
        condition = cls.build_query_condition(query_dict)
        total = cls.query.filter(condition).count()
        sql = cls.query.filter(condition)
        if order_by:
            order_by = re.sub(r'(\w+)\^', r'\1 desc', order_by)
            sql = sql.order_by(text(order_by))
        result = sql.limit(size).offset((page - 1) * size).all()
        return [dict(row) for row in result], total

    @classmethod
    def remove(cls, ident=None, query_dict=None):
        """
        删除
        :param ident: id
        :param query_dict: 查询条件
        """
        condition = None
        if ident:
            condition = and_(cls.id == ident)
        elif query_dict:
            condition = cls.build_query_condition(query_dict)
        if not condition:
            raise Error(message='删除条件不能为空')

        cls.query.filter(condition).update({cls.status: 0})
        cls.db.commit()

    @classmethod
    def build_query_condition(cls, query_dict=None):
        condition = and_(cls.status == 1)

        for key, value in query_dict.items():

            if key.startswith('eq:'):
                condition = and_(condition, getattr(cls, key[3:]) == value)
            elif key.startswith('ne:'):
                condition = and_(condition, getattr(cls, key[3:]) != value)
            elif key.startswith('gt:'):
                condition = and_(condition, getattr(cls, key[3:]) > value)
            elif key.startswith('ge:'):
                condition = and_(condition, getattr(cls, key[3:]) >= value)
            elif key.startswith('lt:'):
                condition = and_(condition, getattr(cls, key[3:]) < value)
            elif key.startswith('le:'):
                condition = and_(condition, getattr(cls, key[3:]) <= value)
            elif key.startswith('in:'):
                condition = and_(condition, getattr(cls, key[3:]).in_(value))
            elif key.startswith('like:'):
                condition = and_(condition, getattr(cls, key[5:]).like(value))
            elif key.startswith('ilike:'):
                condition = and_(condition, getattr(cls, key[6:]).ilike(value))
            elif key.startswith('is:'):
                condition = and_(condition, getattr(cls, key[3:]) == value)
            elif key.startswith('isnot:'):
                condition = and_(condition, getattr(cls, key[6:]) != value)
            elif key.startswith('isnull:'):
                condition = and_(condition, getattr(cls, key[6:]) is None)
            elif key.startswith('isnotnull:'):
                condition = and_(condition, getattr(cls, key[9:]) is not None)
            elif key.startswith('between:'):
                condition = and_(condition, getattr(cls, key[8:]).between(value[0], value[1]))

        return condition
