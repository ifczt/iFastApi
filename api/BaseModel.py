from pydantic import BaseModel as _BaseModel
from fastapi import Form, UploadFile, File, Header


class BaseModel(_BaseModel):
    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        return dict(filter(lambda x: x[1] is not None, data.items()) or {})


class CaptchaMode(BaseModel):
    """验证码模型"""
    captcha_key: str = File(None)
    captcha_val: float = File(None)


class QueryModel(BaseModel):
    """查询模型"""
    query_dict: dict = File(None)


class PageModel(BaseModel):
    """分页模型"""
    page: int = File(None)
    size: int = File(None)


class UpdateModel(QueryModel):
    """更新模型"""
    update_dict: dict = File(None)


class IDModel(BaseModel):
    """ID模型"""
    id: int = File(...)


class ListModel(PageModel, QueryModel):
    """列表模型"""
    pass
