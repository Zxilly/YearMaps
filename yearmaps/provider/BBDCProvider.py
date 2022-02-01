from abc import ABC
from datetime import datetime
from typing import Any

import click
import requests

from yearmaps.impl.provider import Provider
from yearmaps.utils import YearData
from yearmaps.utils.colors import orange
from yearmaps.utils.error import ProviderError

ENDPOINT_URL = "https://learnywhere.cn/bb/dashboard/profile/search?userId={user_id}"


class BBDCProvider(Provider, ABC):
    name = "不背单词"
    id = "bbdc"
    color = orange

    def __init__(self, uid: str):
        self.uid = uid

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

    def access(self):

        """
            data structure
            id: user-id
            utils:
              2021-1-1:
                learn: 20
                time: 5
                review: 20
        """
        with self.data_file() as data:
            if not data:
                data = {
                    "id": self.uid,
                    "utils": {}
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
                if date == "今日":
                    return datetime.today().strftime("%Y-%m-%d")
                return f"{datetime.today().year}-{date}"

            for i in duration:
                full_date = today_transform(i["date"])
                if full_date not in data["utils"]:
                    data["utils"][full_date] = {}
                dur = i["duration"]
                data["utils"][full_date]["time"] = dur

            for i in learn:
                full_date = today_transform(i["date"])
                if full_date not in data["utils"]:
                    data["utils"][full_date] = {}
                learn = i["learnNum"]
                review = i["reviewNum"]
                data["utils"][full_date]["learn"] = learn
                data["utils"][full_date]["review"] = review

        return data


class BBDCTimeProvider(BBDCProvider):
    unit = "分钟"

    def process(self, raw: Any) -> YearData:
        result = {}
        for date, day_data in raw['utils'].items():
            date = datetime.strptime(date, "%Y-%m-%d").date()
            if self.is_date_valid(date):
                time = day_data.get('time', 0)
                result[date] = time
        return result


class BBDCWordProvider(BBDCProvider):
    unit = "词"

    def process(self, raw: Any) -> YearData:
        result = {}
        for date, day_data in raw['utils'].items():
            date = datetime.strptime(date, "%Y-%m-%d").date()
            if self.is_date_valid(date):
                learn: int = day_data.get('learn', 0)
                review: int = day_data.get('review', 0)
                result[date] = learn + review
        return result
