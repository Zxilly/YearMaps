from yearmaps.provider.BBDCProvider import BBDCProvider
from yearmaps.provider.BilibiliProvider import BilibiliProvider
from yearmaps.provider.CodeforcesProvider import CodeforcesProvider
from yearmaps.provider.GitHubProvider import GitHubProvider
from yearmaps.provider.MiFitProvider import MiFitProvider

providers = [BBDCProvider, BilibiliProvider, CodeforcesProvider, GitHubProvider, MiFitProvider]

provider_map = {x.command.name: x for x in providers}
