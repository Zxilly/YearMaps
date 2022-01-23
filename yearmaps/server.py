import os
from pathlib import Path
from typing import Dict, List

import click
import yaml

from yearmaps.interface.task import Task
from yearmaps.providers import providers
from yearmaps.utils import file
from yearmaps.constant import Config
from yearmaps.utils.file import ensure_dir


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

    if 'data-dir' not in config_dict.keys():
        config_dict['data-dir'] = file.default_data_dir()
    if 'cache-dir' not in config_dict.keys():
        config_dict['cache-dir'] = file.default_cache_dir()

    ensure_dir(config_dict['data-dir'])

    obj[Config.DATA_DIR] = config_dict['data-dir']
    obj[Config.OUTPUT_DIR] = config_dict['cache-dir']

    # Check provider config
    if 'providers' not in config_dict.keys():
        raise KeyError('Providers not found in config file.')

    if not isinstance(config_dict['providers'], Dict):
        raise TypeError('Providers must have arguments.')

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

        if not set(provider_config.keys()).issuperset(set(provider_required_params[key])):
            raise KeyError(
                'Provider {key} is missing required params: '
                f'{set(provider_required_params[key]) - set(provider_config.keys())}')

    provider_map = {}
    for provider in providers:
        name = provider.command.name
        provider_map[name] = provider

    task_list: List[Task] = []
    for provider_key, provider_config in config_dict['providers'].items():
        if 'global' in provider_config.keys():
            global_config = provider_config['global']
        else:
            global_config = {}
        task = Task(ctx, provider_map[provider_key].command, global_config, provider_config)
        task_list.append(task)
        for task in task_list:
            task.run()


if __name__ == '__main__':
    cli()
