import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import click
import yaml

from yearmaps.interface.task import Task
from yearmaps.providers import providers
from yearmaps.utils import file
from yearmaps.constant import Config
from yearmaps.utils.colors import color_list
from yearmaps.utils.file import ensure_dir


@click.command()
@click.option('--host', '-h', default='0.0.0.0', type=str, help='Host to listen on.')
@click.option('--port', '-p', default=5000, type=int, help='Port to listen on.')
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
    # has default value from click
    if config_dict['host'] is not None:
        config_dict['host'] = host
    if config_dict['port'] is not None:
        config_dict['port'] = port

    # Initialize config from yaml
    if 'data-dir' not in config_dict.keys():
        config_dict['data-dir'] = file.default_data_dir()
    if 'cache-dir' not in config_dict.keys():
        config_dict['cache-dir'] = file.default_cache_dir()
    if 'mode' not in config_dict.keys():
        config_dict['mode'] = 'till_now'
    if 'year' not in config_dict.keys() and config_dict['mode'] == 'year':
        config_dict['year'] = datetime.now().year
    if 'file_type' not in config_dict.keys():
        config_dict['file_type'] = 'png'

    # Check dirs
    ensure_dir(config_dict['data-dir'])
    ensure_dir(config_dict['cache-dir'])

    # Copy yaml config to context object
    obj[Config.DATA_DIR] = config_dict['data-dir']
    obj[Config.OUTPUT_DIR] = config_dict['cache-dir']
    obj[Config.MODE] = config_dict['mode']
    obj[Config.YEAR] = config_dict.get('year', None)
    obj[Config.FILE_TYPE] = config_dict['file_type']
    obj[Config.COLOR] = config_dict.get('color', None)

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

    # Validate provider config
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

    # Build provider map
    provider_map = {}
    for provider in providers:
        name = provider.command.name
        provider_map[name] = provider

    # Build tasks
    task_list: List[Task] = []
    for provider_key, provider_config in config_dict['providers'].items():
        global_config = {}
        if 'global' in provider_config.keys():
            if not isinstance(provider_config['global'], Dict):
                raise TypeError('Global config must be a dict.')
            for key, value in provider_config['global']:
                try:
                    obj_key = Config(key)
                except ValueError:
                    raise KeyError(f'{key} is not a valid global option.')

                # Additional check for global config
                if obj_key == Config.MODE:
                    if value not in ['till_now', 'year']:
                        raise ValueError(f'{value} is not a valid mode.')
                elif obj_key == Config.YEAR:
                    if not isinstance(value, int):
                        raise TypeError('Year must be an integer.')
                    if value < 2000 or value > datetime.now().year:
                        raise ValueError(f'{value} is not a valid year.')
                elif obj_key == Config.FILE_TYPE:
                    if value not in ['png', 'svg']:
                        raise ValueError(f'{value} is not a supported file type.')
                elif obj_key == Config.COLOR:
                    if not isinstance(value, str):
                        raise TypeError('Color must be a string.')
                    if value not in color_list.keys():
                        raise ValueError(f'{value} is not a valid color.')

                global_config[obj_key] = value
        task = Task(ctx, provider_map[provider_key].command, global_config, provider_config)
        task_list.append(task)

    for task in task_list:
        task.run()


if __name__ == '__main__':
    cli()
