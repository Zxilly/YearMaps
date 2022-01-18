from abc import ABC
from datetime import datetime
from typing import Any, Dict

import click
import requests

from yearmaps.data import YearData
from yearmaps.interface.provider import Provider
from yearmaps.utils import ProviderError
from yearmaps.data.colors import orange

ENDPOINT_URL = "https://learnywhere.cn/bb/dashboard/profile/search?userId={user_id}"


class BBDCProvider(Provider, ABC):
    """
    cache structure
    id: user-id
    data:
      2021-1-1:
        learn: 20
        time: 5
        review: 20
    """

    name = "不背单词"
    id = "bbdc"
    colors = orange

    def __init__(self, uid: str):
        self.uid = uid

    def access(self):
        data = self.read_data_file()
        if data == {}:
            data = {
                "id": self.uid,
                "data": {}
            }
        if data.get("id") != self.uid:
            raise ProviderError("user_id 和数据缓存不一致")
        resp = requests.get(ENDPOINT_URL.format(user_id=self.uid))
        if not resp.ok:
            raise ProviderError(f"Meet network error. {resp.reason}")
        resp_data = resp.json()
        if resp_data["result_code"] != 200:
            raise ProviderError(f"Unexpected error. {data}")

        body = resp_data["data_body"]
        duration = body["durationList"]
        learn = body["learnList"]

        def today_transform(date):
            if not date == "今日":
                return f"{datetime.today().year}-{date}"
            else:
                return datetime.today().strftime("%Y-%m-%d")

        for i in duration:
            full_date = today_transform(i["date"])
            if full_date not in data["data"]:
                data["data"][full_date] = {}
            dur = i["duration"]
            data["data"][full_date]["time"] = dur

        for i in learn:
            full_date = today_transform(i["date"])
            if full_date not in data["data"]:
                data["data"][full_date] = {}
            learn = i["learnNum"]
            review = i["reviewNum"]
            data["data"][full_date]["learn"] = learn
            data["data"][full_date]["review"] = review
        self.write_data_file(data)

        return data

    @staticmethod
    @click.command('bbdc', help="不背单词")
    @click.option('--id', '-i', 'uid', type=str, required=True, help='不背单词用户 ID')
    @click.option('--type', '-t', 'gtype', type=click.Choice(['time', 'word']), default='time', help='图数据类型')
    @click.pass_context
    def command(ctx: click.Context, uid: str, gtype: str):
        if gtype == 'time':
            provider = BBDCTimeProvider(uid)
        elif gtype == "word":
            provider = BBDCWordProvider(uid)
        else:
            raise ProviderError(f"Unknown type {gtype}")
        provider.render(ctx.obj)


class BBDCTimeProvider(BBDCProvider):
    unit = "分钟"

    def process(self, data: Any) -> YearData:
        result = dict()
        for date, day_data in data['data'].items():
            date = date.strptime(date, "%Y-%m-%d")
            if self.is_date_valid(date):
                time = day_data.get('time', 0)
                result[date] = time
        return result


class BBDCWordProvider(BBDCProvider):
    unit = "词"

    def process(self, data: Any) -> Dict[int, YearData]:
        result = dict()
        for date, day_data in data['data'].items():
            date = date.strptime(date, "%Y-%m-%d")
            if self.is_date_valid(date):
                learn = day_data.get('learn', 0)
                review = day_data.get('review', 0)
                result[date] = learn + review
        return result
