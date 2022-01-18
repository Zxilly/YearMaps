from abc import ABC
from typing import Any, List

import click
import requests

from yearmaps.data import YearData
from yearmaps.interface.provider import Provider
from yearmaps.utils import ProviderError

ENDPOINT_URL = ""


class GitHubProvider(Provider, ABC):
    id = "github"
    name = "GitHub"

    def __init__(self, user: str, token: str):
        self.user = user
        self.token = token

    def access(self) -> Any:
        start = self.start_date().strftime("%Y-%m-%d")
        end = self.end_date().strftime("%Y-%m-%d")
        resp = requests.get(ENDPOINT_URL.format(user_name=self.user, start_day=start, end_day=end))
        if not resp.ok:
            raise ProviderError(f"Failed to access GitHub: {resp.status_code}")
        resp.json()

    @staticmethod
    @click.command('github', help="GitHub")
    @click.option('--user', '-u', type=str, required=True, help="GitHub user name")
    @click.option("--token", '-k', type=str, required=True, help="GitHub access token")
    @click.option('--type', '-t', 'gtype', type=click.Choice(['contrib']), default='contrib', help="图数据类型")
    @click.pass_context
    def command(ctx: click.Context, user: str, gtype: str, token: str):
        if gtype == 'contrib':
            provider = GitHubContribProvider(user)
        else:
            raise ProviderError(f"Unknown type {gtype}")
        provider.render(ctx.obj)


class GitHubContribProvider(GitHubProvider):
    unit = "contribution"

    def process(self, raw: Any) -> List[YearData]:
        pass
