from abc import ABC
from typing import Any, Dict

import click

from yearmaps.script import cli
from yearmaps.data import YearData
from yearmaps.interface.provider import Provider


class BBDCProvider(Provider, ABC):
    name = "不背单词"

    uid: str

    def __init__(self, uid: str):
        self.uid = uid

    def fetch(self):
        pass

    @staticmethod
    @cli.command('bbdc', help="不背单词")
    @cli.option('--uid', type=str, required=True, help='不背单词用户 ID')
    @cli.option('--gtype', type=click.Choice(['time', 'word']), default='time', help='图数据类型')
    @cli.pass_context
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
