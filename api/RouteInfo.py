# Author: IFCZT
# Email: ifczt@qq.com
from collections import UserDict


class RouteInfo(UserDict):
    def __init__(self, path, endpoint, methods=None, dependencies=None, summary=None, need_db=True, need_auth=True,
                 need_captcha=True):
        """
        :param path: 访问路径
        :param endpoint: 执行函数
        :param methods: 请求方法
        :param dependencies: 依赖函数
        :param summary: 描述
        :param need_db: 是否需要使用数据库
        :param need_auth: 是否需要验证权限
        """
        super().__init__()
        if methods is None:
            methods = ['POST']
        self.data = {
            'path': path,
            'endpoint': endpoint,
            'methods': methods,
            'dependencies': dependencies,
            'summary': summary,
            'need_db': need_db,
            'need_auth': need_auth,
            'need_captcha': need_captcha,
        }