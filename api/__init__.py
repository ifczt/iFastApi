# Author: IFCZT
# Email: ifczt@qq.com
import logging

from utils.singleton import Singleton


class BaseAPI:

    def __init__(self):
        pass




@Singleton
class RouteManager:

    def __init__(self):
        self.logger = logging.getLogger('RouteManager')
        # 无需使用DB的路由集合
        self.no_db_route = set()
        self.permissions = {}

    def add_permission(self, route, power):
        self.permissions[route] = power

    def check_permission(self, route, power):
        if route not in self.permissions:
            return True
        return route in self.permissions[route]

    def add_no_db_route(self, route):
        self.no_db_route.add(route)

    def is_no_db_route(self, route):
        return route in self.no_db_route
