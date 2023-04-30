from fastapi import APIRouter

from api.BaseModel import ListModel, QueryModel, UpdateModel
from api.RouteInfo import RouteInfo


class BaseRoute:
    __is_initialized = False

    def __init__(self, prefix=None):
        self._db = None
        self.name = self.__class__.__name__.lower()
        self.router = APIRouter(prefix='/' + (prefix or self.name))
        self.default_routes = (
            RouteInfo('/remove', self.remove, summary='软删除', verify_auth=True),
            RouteInfo('/delete', self.delete, summary='硬删除', verify_auth=True),
            RouteInfo('/update', self.update, summary='更新', verify_auth=True),
            RouteInfo('/get_list', self.get_list, summary='获取列表', verify_auth=True),
            RouteInfo('/get_info', self.get_info, summary='获取详情', verify_auth=True),
        )

    @property
    def db(self):
        if not self._db:
            raise NotImplementedError()
        return self._db

    @db.setter
    def db(self, db):
        self._db = db

    def setup(self):
        self.setup_routes()

    def remove(self, data: QueryModel):
        return self.db.remove(data.dict())

    def delete(self, data: QueryModel):
        return self.db.delete(data.dict())

    def update(self, data: UpdateModel):
        return self.db.update(**data.dict())

    def get_list(self, data: ListModel):
        return self.db.get_list(**data.dict())

    def get_info(self, data: QueryModel):
        return self.db.get_info(**data.dict())

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls != BaseRoute:
            delattr(cls, "init_router")

    @classmethod
    def init_router(cls):
        if BaseRoute.__is_initialized:
            return 'BaseRoute已经初始化过了'
        BaseRoute.__is_initialized = True
        for item in BaseRoute.__subclasses__():
            item().setup()

    def setup_routes(self):
        raise NotImplementedError()
