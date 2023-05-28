# Author: IFCZT
# Email: ifczt@qq.com
from typing import Tuple, Any

from sqlalchemy import orm
from ..utils.iResponse import Error, HTTPStatus


class BaseQuery(orm.Query):
    def _all_selected_columns(self):
        # 获取当前查询对象中所有被选择的列
        selected_columns = set()
        for entity in self._entities:
            if isinstance(entity, orm.attributes.QueryableAttribute):
                selected_columns.add(entity)
        return selected_columns

    def _copy_internals(self, omit_attrs=(), **kw):
        # 复制当前查询对象的内部状态
        instance = self.__class__.__new__(self.__class__)
        instance.__dict__.update(self.__dict__)
        for attr in omit_attrs:
            delattr(instance, attr)
        instance.__dict__.update(kw)
        return instance

    def first_or_404(self, msg='资源不存在'):
        rv = self.first()
        if not rv:
            raise Error(message=msg, status_code=HTTPStatus.NOT_FOUND)
        return rv
