from abc import ABC
from typing import Any, Dict

import click

from yearmaps.data import YearData
from yearmaps.interface.provider import Provider

ENDPOINT_URL = "https://learnywhere.cn/bb/dashboard/profile/search?userId={user_id}"


class BBDCProvider(Provider, ABC):
    name = "不背单词"
    id = "bbdc"

    uid: str

    def __init__(self, uid: str):
        self.uid = uid

    def fetch(self):
        pass

    @staticmethod
    @click.command('bbdc', help="不背单词")
    @click.option('--id', '-i', 'uid', type=str, required=True, help='不背单词用户 ID')
    @click.option('--type', '-t', 'gtype', type=click.Choice(['time', 'word']), default='time', help='图数据类型')
    @click.pass_context
    def command(ctx: click.Context, uid: str, gtype: str):
        if gtype == 'time':
            provider = BBDCTimeProvider(uid)
        else:
            provider = BBDCWordProvider(uid)
        provider.render(ctx.obj)


class BBDCTimeProvider(BBDCProvider):
    unit = "分钟"

    def parse(self, data: Any) -> Dict[int, YearData]:
        pass


class BBDCWordProvider(BBDCProvider):
    unit = "词"

    def parse(self, data: Any) -> Dict[int, YearData]:
        pass
