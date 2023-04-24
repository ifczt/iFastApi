# Author: IFCZT
# Email: ifczt@qq.com
from sqlalchemy import create_engine, Column, Integer, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from db.BaseQuery import BaseQuery
from utils.singleton import Singleton


@Singleton
class DBManager:
    base = declarative_base()
    def __init__(self):
        self._base = None
        self._session = None
        self._engine = None

    def setup(self, config):
        if not config.SQLALCHEMY_DATABASE_URI:
            raise Exception('数据库连接地址未配置')

        self._engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        self._session = sessionmaker(bind=self.engine, query_cls=BaseQuery)

    @property
    def engine(self):
        if not self._engine:
            raise Exception('数据库未连接')
        return self._engine

    @property
    def session(self):
        if not self._session:
            raise Exception('数据库未连接')
        return self._session

    def get_db(self):
        db = self.session()
        try:
            yield db
        finally:
            db.close()


class BaseDB(DBManager.base):
    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    create_time = Column(Integer, comment='生成时间')
    status = Column(SmallInteger, default=1, comment='是否软删除 0 / 1')
