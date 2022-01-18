from datetime import datetime
from abc import ABC
from typing import Any, List

import click
import requests

from yearmaps.data import YearData
from yearmaps.interface.provider import Provider
from yearmaps.utils import ProviderError

ENDPOINT_URL = "https://api.github.com/graphql"

contribution_query = """
query ($user: String!,$start: DateTime) {
  user(login: $user) {
    contributionsCollection(from:$start) {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""


class GitHubProvider(Provider, ABC):
    id = "github"
    name = "GitHub"

    def __init__(self, user: str, token: str):
        self.user = user
        self.token = token

    @staticmethod
    @click.command('github', help="GitHub")
    @click.option('--user', '-u', type=str, required=True, help="GitHub user name")
    @click.option("--token", '-k', type=str, required=True, help="GitHub access token")
    @click.option('--type', '-t', 'gtype', type=click.Choice(['contrib']), default='contrib', help="图数据类型")
    @click.pass_context
    def command(ctx: click.Context, user: str, gtype: str, token: str):
        if gtype == 'contrib':
            provider = GitHubContribProvider(user, token)
        else:
            raise ProviderError(f"Unknown type {gtype}")
        provider.render(ctx.obj)


class GitHubContribProvider(GitHubProvider):
    unit = "contribution"

    def access(self) -> Any:
        resp = requests.post(ENDPOINT_URL, json={
            'query': contribution_query,
            'variables': {
                'user': self.user,
                'start': datetime.combine(self.start_date(), datetime.min.time()).isoformat()
            }
        }, headers={
            'Authorization': f"bearer {self.token}"
        })
        if not resp.ok:
            raise ProviderError(f"{resp.status_code} - {resp.reason}")
        return resp.json()

    def process(self, raw: Any) -> List[YearData]:
        result = dict()
        data = raw['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        for week in data:
            for day in week['contributionDays']:
                date = datetime.fromisoformat(day['date']).date()
                value = day['contributionCount']
                result[date] = value
        return result
