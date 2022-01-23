import os
from pathlib import Path
from typing import Dict, List

import click
import yaml

from yearmaps.providers import providers
from yearmaps.utils import file
from yearmaps.constant import Config


@click.command()
@click.option('--host', '-h', default='0.0.0.0', type=str, help='Host to listen on.')
@click.option('--port', '-p', default=5000, type=str, help='Port to listen on.')
@click.option('--config', '-f', default=str(Path(os.getcwd()) / 'yearmaps.yml'), type=str, show_default=True,
              help='Path to config file.')
@click.pass_context
def cli(ctx: click.Context, host: str, port: int, config: str):
    ctx.ensure_object(dict)
    obj = ctx.obj
    obj[Config.SERVER] = True

    # Load config
    if not Path(config).resolve().exists():
        raise FileNotFoundError(f'Config file not found: {config}')
    with open(config, 'r', encoding='UTF-8') as f:
        config_dict: Dict = yaml.load(f, Loader=yaml.FullLoader)

    # Initialize server args
    if host is not None:
        config_dict['host'] = host
    if port is not None:
        config_dict['port'] = port
    values = {
        'host': '0.0.0.0',
        'port': 5000,
        'data-dir': file.default_data_dir(),
        'cache-dir': file.default_cache_dir(),
    }
    for key in values.keys():
        if key in config_dict.keys():
            values[key] = config_dict[key]

    # Check provider config
    if 'providers' not in config_dict.keys():
        raise KeyError('Providers not found in config file.')

    if not isinstance(config_dict['providers'], Dict):
        raise TypeError('Providers must be a dict.')

    # Build required params for each provider
    provider_required_params = {}
    for provider in providers:
        command: click.Command = provider.command
        params = command.params
        name = command.name
        provider_required_params[name] = []
        for param in params:
            if param.required:
                provider_required_params[name].append(param.name)

    for key in config_dict['providers'].keys():
        if key not in provider_required_params.keys():
            raise KeyError(f'Provider not found: {key}')

        provider_config = config_dict['providers'][key]
        if not isinstance(provider_config, Dict):
            raise TypeError(f'Provider {key} must be a dict.')

        if set(provider_config.keys()) < set(provider_required_params[key]):
            raise KeyError(f'Provider {key} is missing required params: {provider_required_params[key]}')



if __name__ == '__main__':
    cli()
