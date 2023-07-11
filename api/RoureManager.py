import logging

from ..utils.singleton import Singleton


@Singleton
class RouteManager:
    def __init__(self):
        # 无需使用DB的路由集合
        self.use_db_route = set()
        self.auth = {}
        self.need_token = set()

    def add_auth(self, route, power):
        if isinstance(power, bool) and power:
            self.need_token.add(route)
            return
        self.auth[route] = power

    def check_auth(self, route, power):
        if route not in self.auth:
            return True
        print(power,self.auth[route])
        return power in self.auth[route]

    def path_need_token(self, path_key):
        return path_key in self.need_token or path_key in self.auth

    def add_use_db_route(self, route):
        self.use_db_route.add(route)

    def is_use_db_route(self, route):
        return route in self.use_db_route
