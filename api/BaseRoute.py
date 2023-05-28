import inspect

from fastapi import APIRouter

from .BaseModel import ListModel, QueryModel, UpdateModel
from .RoureManager import RouteManager
from .RouteInfo import RouteInfo
from ..utils.toolfuns import path_to_key
from ..utils.iResponse import Error, HTTPStatus

class BaseRoute:
    __is_initialized = False

    def __init__(self, prefix=None):
        self._db = None
        _name = f'/{prefix or self.__class__.__name__.lower()}'
        self.router = APIRouter(prefix=_name)
        self.default_routes = [
            RouteInfo('/remove', self.remove, summary='软删除', verify_auth=True),
            RouteInfo('/delete', self.delete, summary='硬删除', verify_auth=True),
            RouteInfo('/update', self.update, summary='更新', verify_auth=True),
            RouteInfo('/get_list', self.get_list, summary='获取列表', verify_auth=True),
            RouteInfo('/get_info', self.get_info, summary='获取详情', verify_auth=True)
        ]
        self.roure_manager = RouteManager()
        self.routers = []

    @property
    def db(self):
        if not self._db:
            raise Error(message='未初始化数据库', status_code=HTTPStatus.SERVICE_UNAVAILABLE)
        return self._db

    @db.setter
    def db(self, db):
        self._db = db

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

    @classmethod
    def init_router(cls, app):
        if BaseRoute.__is_initialized:
            return 'BaseRoute已经初始化过了'
        BaseRoute.__is_initialized = True
        for item in BaseRoute.__subclasses__():
            item().setup_routes(app)

    def setup_routes(self, app):
        routes = self.default_routes + self.routers
        for route_info in routes:
            route_info.update({'tags': [self.__class__.__name__]})
            path_key = path_to_key(self.router.prefix[1:] + route_info.get('path'))
            if route_info.get('use_db'):
                self.roure_manager.add_use_db_route(path_key)
            if route_info.get('verify_auth'):
                self.roure_manager.add_auth(path_key, route_info.get('verify_auth'))

            # 使用字典推导式和 filter 函数获取目标函数的参数信息
            func_params = inspect.signature(self.router.add_api_route).parameters
            kwargs = {k: v for k, v in route_info.items() if k in filter(lambda x: x in route_info, func_params)}
            self.router.add_api_route(**kwargs)

        app.include_router(self.router)
