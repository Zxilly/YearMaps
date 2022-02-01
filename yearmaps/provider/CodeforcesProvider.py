from abc import ABC
from collections import defaultdict
from datetime import date
from typing import Any

import click
import requests

from yearmaps.impl.provider import Provider
from yearmaps.utils import YearData
from yearmaps.utils.colors import purple
from yearmaps.utils.error import ProviderError

ENDPOINT_URL = "https://codeforces.com/api/user.status?handle={user}"


class CodeforcesProvider(Provider, ABC):
    name = "Codeforces"
    id = "cf"
    color = purple

    def __init__(self, user: str):
        self.user = user

    def access(self) -> Any:
        return requests.get(ENDPOINT_URL.format(user=self.user)).json()

    @staticmethod
    @click.command("cf", help="Codeforces")
    @click.option("--user", "-u", type=str, required=True, help="Codeforces user name")
    @click.option("--type", "-t", "gtype", type=click.Choice(("all", "ac")), default="all", help="图数据类型")
    @click.pass_context
    def command(ctx: click.Context, user: str, gtype: str):
        if gtype == "all":
            provider = CodeforcesAllProvider(user)
        elif gtype == "ac":
            provider = CodeforcesACProvider(user)
        else:
            raise ProviderError(f"Unknown type {gtype}")
        provider.render(ctx.obj)


class CodeforcesACProvider(CodeforcesProvider):
    unit = "Accepted Problems"

    def process(self, raw: Any) -> YearData:
        d = defaultdict(int)
        for res in raw["result"]:
            if res["verdict"] == "OK":
                d[date.fromtimestamp(res["creationTimeSeconds"])] += 1
        return d


class CodeforcesAllProvider(CodeforcesProvider):
    unit = "Problems"

    def process(self, raw: Any) -> YearData:
        d = defaultdict(int)
        for res in raw["result"]:
            d[date.fromtimestamp(res["creationTimeSeconds"])] += 1
        return d
