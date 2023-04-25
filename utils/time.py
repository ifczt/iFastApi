# Author: IFCZT
# Email: ifczt@qq.com
import datetime
import pytz
from .singleton import Singleton


@Singleton
class Time:
    @property
    def now(self):
        """
        获取当前时间 (UTC+8)
        :return datetime.datetime 2023-04-24 17:34:00.758249
        """
        return datetime.datetime.utcnow() + datetime.timedelta(hours=8)

    def format_time(self, default_datetime: datetime.datetime = None, time_format="%Y-%m-%d %H:%M:%S"):
        """
        获取格式化时间 默认时间为当前时间
        :param default_datetime: datetime.datetime 转换datetime时间对象
        :param time_format: str 时间格式
        :return 2023-04-24 17:34:00
        """
        if not default_datetime:
            default_datetime = self.now
        return default_datetime.strftime(time_format)

    def int_time(self, modes='s'):
        """
        获取当前时间戳
        :param modes: str 时间戳模式 s / ms / us
        :return:  s 10位 精确到秒 ms 13位 精确到毫秒 us 16位 精确到微秒
        """
        _multiple = {'s': 1, 'ms': 1000, 'us': 1000000}

        if modes not in _multiple:
            raise Exception('时间戳模式错误')

        return int(self.now.timestamp() * _multiple[modes])

    @property
    def n_year(self):
        return self.now.year

    @property
    def n_month(self):
        return self.now.month

    @property
    def n_day(self):
        return self.now.day

    @property
    def n_hour(self):
        return self.now.hour

    @property
    def n_minute(self):
        return self.now.minute

    @property
    def n_second(self):
        return self.now.second

    def to_timezone(self, default_datetime: datetime.datetime = None, timezone: str = 'UTC', time_format="%Y-%m-%d %H:%M:%S"):
        """
        将时间对象转换为指定时区的时间
        :param default_datetime: datetime.datetime 转换datetime时间对象
        :param timezone: str 时区，默认为 'UTC'
        :param time_format: str 时间格式
        :return 2023-04-24 17:34:00
        """
        if not default_datetime:
            default_datetime = self.now
        tz = pytz.timezone(timezone)
        return default_datetime.astimezone(tz).strftime(time_format)

    def time_diff(self, start_time: datetime.datetime, end_time: datetime.datetime):
        """
        计算两个时间之间的时间差
        :param start_time: datetime.datetime 开始时间
        :param end_time: datetime.datetime 结束时间
        :return datetime.timedelta 时间差
        """
        return end_time - start_time

    def countdown(self, end_time: datetime.datetime, time_format="%Y-%m-%d %H:%M:%S"):
        """
        计算从当前时间到指定时间的倒计时
        :param end_time: datetime.datetime 结束时间
        :param time_format: str 时间格式
        :return str 倒计时时间
        """
        delta = end_time - self.now
        if delta.total_seconds() < 0:
            return "已结束"
        else:
            return str(delta).split(".")[0]

    def date_range(self, start_date: datetime.datetime, end_date: datetime.datetime):
        """
        获取某个日期范围内的所有日期
        :param start_date: datetime.datetime 开始日期
        :param end_date: datetime.datetime 结束日期
        :return list 所有日期列表
        """
        delta = end_date - start_date
        dates = []
        for i in range(delta.days + 1):
            date = start_date + datetime.timedelta(days=i)
            dates.append(date)
        return dates


time = Time()
