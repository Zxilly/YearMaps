import base64
import json
from abc import ABC
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlparse, parse_qs

import click
import numpy as np
import requests
import requests.utils

from yearmaps.impl.provider import Provider
from yearmaps.utils import YearData
from yearmaps.utils.colors import indigo
from yearmaps.utils.error import ProviderError


class MiFitProvider(Provider, ABC):
    id = 'mifit'
    name = '小米运动'
    color = indigo

    def __init__(self, phone: str, password: str):
        self.phone = phone
        self.password = password
        self.user_id = None
        self.app_token = None
        self.up_token = None

    def init(self):
        with self.data_file() as data:
            if "user_id" in data and "up_token" in data:
                self.user_id = data["user_id"]
                self.up_token = data["up_token"]
                try:
                    self.login_with_token()  # check token
                    return
                except ProviderError as e:
                    if e.status_code != 400:
                        raise e
            self.login_with_password(self.phone, self.password)
            self.login_with_token()
            data["user_id"] = self.user_id
            data["up_token"] = self.up_token

    @staticmethod
    @click.command('mifit', help='小米运动')
    @click.option('--phone', '-u', type=str, required=True, help='手机号（华米健康）')
    @click.option('--password', '-p', type=str, required=True, help='密码')
    @click.option('--type', '-t', 'gtype', type=click.Choice(['sleep']), default='sleep', help='图数据类型')
    @click.pass_context
    def command(ctx: click.Context, phone: str, password: str, gtype: str):
        if gtype == 'sleep':
            provider = MiFitSleepProvider(phone, password)
        else:
            raise ProviderError(f"Unsupported type {gtype}")
        provider.render(ctx.obj)

    def login_with_password(self, phone: str, password: str):
        req_data = (
            ("phone_number", phone),
            ("password", password),
            ("state", "REDIRECTION"),
            ("client_id", "HuaMi"),
            ("country_code", "CN"),
            ("token", "access"),
            ("token", "refresh"),
            ("redirect_uri", "https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html"),
        )
        resp = requests.post(f"https://api-user.huami.com/registrations/%2B86{phone}/tokens", data=req_data,
                             allow_redirects=False)
        if not resp.ok:
            raise ProviderError(f"Login failed {resp.status_code} {resp.reason}")
        location = resp.headers["Location"]
        query = urlparse(location).query
        self.up_token = parse_qs(query)["access"][0]  # should be cached

    def login_with_token(self):
        req_data = {
            "app_name": "com.xiaomi.hm.health",
            "country_code": "CN",
            "code": self.up_token,
            "device_id": "02:00:00:00:00:00",
            "device_model": "android_phone",
            "app_version": "4.0.17",
            "grant_type": "access_token",
            "allow_registration": "false",
            "dn": "account.huami.com,api-user.huami.com,api-watch.huami.com,"
                  "api-analytics.huami.com,app-analytics.huami.com,api-mifit.huami.com",
            "third_name": "huami_phone",
            "source": "com.xiaomi.hm.health:4.0.17:50283",
            "lang": "zh"
        }
        resp = requests.post("https://account.huami.com/v2/client/login", data=req_data)
        if not resp.ok:
            err = ProviderError(f"Login failed {resp.status_code} {resp.reason}")
            err.status_code = resp.status_code
            raise err
        resp_data = resp.json()
        self.app_token = resp_data["token_info"]["app_token"]
        self.user_id = resp_data["token_info"]["user_id"]


class MiFitSleepProvider(MiFitProvider):
    name = '睡眠时间'

    @staticmethod
    def format_time(time: int) -> str:
        t = timedelta(seconds=time)
        return f"平均：{t.seconds // 3600} 小时 {t.seconds // 60 % 60} 分钟"

    unit = format_time

    @staticmethod
    def label_format(value: int) -> str:
        t = timedelta(seconds=value)
        hours = str(t.seconds // 3600).zfill(2)
        minutes = str(t.seconds // 60 % 60).zfill(2)
        return f"{hours}:{minutes}"

    @staticmethod
    def analysis(data: np.ndarray):
        return np.nanmean(data)

    def access(self) -> Any:
        headers = {
            "timezone": "Asia/Shanghai",
            "apptoken": self.app_token,
            "country": "CN",
            "appplatform": "android_phone",
            "appname": "com.xiaomi.hm.health",
        }
        params = {
            "userid": self.user_id,
            "country": "CN",
            "device": "android_30",
            "device_type": "android_phone",
            "lang": "zh_CN",
            "query_type": "summary",
            "timezone": "Asia/Shanghai",
            "from_date": self.start_date().strftime("%Y-%m-%d"),
            "to_date": self.end_date().strftime("%Y-%m-%d"),
        }
        resp = requests.get("https://api-mifit.huami.com/v1/data/band_data.json", headers=headers, params=params)
        if not resp.ok:
            raise ProviderError(f"Access failed {resp.status_code} {resp.reason}")
        return resp.json()

    def process(self, raw: Any) -> YearData:
        ret = {}
        data = raw["data"]
        for piece in data:
            date = datetime.strptime(piece["date_time"], "%Y-%m-%d").date()
            summary = json.loads(base64.b64decode(piece["summary"]).decode("utf-8"))
            sleep = summary['slp']
            value = sleep['ed'] - sleep['st']
            if value > 3600 * 3:  # 3 hour
                ret[date] = value
        return ret
