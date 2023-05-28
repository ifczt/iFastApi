# Author: IFCZT
# Email: ifczt@qq.com






# 多个装饰器合并
# 列如 @icompose(classmethod, idb)
def icompose(*funs):
    def deco(f):
        for fun in reversed(funs):
            f = fun(f)
        return f

    return deco



