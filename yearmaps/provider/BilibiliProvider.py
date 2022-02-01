from abc import ABC
from collections import defaultdict
from datetime import date
from typing import Any

import click
import requests

from yearmaps.impl.provider import Provider
from yearmaps.utils import YearData
from yearmaps.utils.colors import pink
from yearmaps.utils.error import ProviderError

ENDPOINT_URL = "https://api.bilibili.com/x/space/arc/search?mid={uid}&ps=50&pn={pn}"


class BilibiliProvider(Provider, ABC):
    name = "bilibili"
    id = "bili"
    color = pink

    def __init__(self, uid: str):
        self.uid = uid

    def access(self) -> Any:
        data_ret = []
        pn = 1
        data_tmp = requests.get(ENDPOINT_URL.format(uid=self.uid, pn=pn)).json()
        ps = data_tmp["data"]["page"]["ps"]
        cnt = data_tmp["data"]["page"]["count"]
        while (pn - 1) * ps <= cnt:
            data_ret.extend(data_tmp["data"]["list"]["vlist"])
            pn += 1
            data_tmp = requests.get(ENDPOINT_URL.format(uid=self.uid, pn=pn)).json()
        return data_ret

    @staticmethod
    @click.command("bili", help="Bilibili")
    @click.option("--id", "-i", "uid", type=str, required=True, help="bilibili uid")
    @click.option("--type", "-t", "gtype", type=click.Choice(("video",)), default="video", help="图数据类型")
    @click.pass_context
    def command(ctx: click.Context, uid: str, gtype: str):
        if gtype == "video":
            provider = BilibiliVideoProvider(uid)
        else:
            raise ProviderError(f"Unknown type {gtype}")
        provider.render(ctx.obj)


class BilibiliVideoProvider(BilibiliProvider):
    unit = "Video"

    def process(self, raw: Any) -> YearData:
        d = defaultdict(int)
        for res in raw:
            d[date.fromtimestamp(res["created"])] += 1
        return d
