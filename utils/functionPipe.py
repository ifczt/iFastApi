"""
管道函数
将需要依次执行的函数用管道符连接起来 并且将前一个函数的返回值作为后一个函数的参数
使用方法:
FunctionPipe(value) | (lambda x: x + 1) | (lambda x: x + 2) | print
"""


class FunctionPipe:
    def __init__(self, value):
        self.value = value

    def __or__(self, func):
        self.value = func(self.value)
        return self
