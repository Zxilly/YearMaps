import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import click
import indexpy
import uvicorn
import yaml
import schedule

from yearmaps.constant import Configs
from yearmaps.interface.task import Task
from yearmaps.provider import providers, provider_map
from yearmaps.utils import file
from yearmaps.utils.colors import color_list
from yearmaps.utils.file import ensure_dir
from yearmaps.utils.util import option_name


@click.command()
@click.option('--host', '-l', default='0.0.0.0', show_default=True, type=str, help='Host to listen on.')
@click.option('--port', '-p', default=5000, show_default=True, type=int, help='Port to listen on.')
@click.option('--config', '-f', default=str(Path(os.getcwd()) / 'yearmaps.yml'), type=str, show_default=True,
              help='Path to config file.')
@click.pass_context
def cli(ctx: click.Context, host: str, port: int, config: str):
    # Load config
    if not Path(config).resolve().exists():
        raise FileNotFoundError(f'Config file not found: {config}')
    with open(config, 'r', encoding='UTF-8') as f:
        config_dict: Dict = yaml.load(f, Loader=yaml.FullLoader)

    # Initialize server args
    # has default value from click
    if host is not None:
        config_dict['host'] = host
    if port is not None:
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
    ctx.obj = Configs(
        data_dir=config_dict['data-dir'],
        output=config_dict['cache-dir'],  # should append filename later
        mode=config_dict['mode'],
        year=config_dict.get('year', None),
        file_type=config_dict['file_type'],
        color=config_dict.get('color', None)
    )
    obj = ctx.obj
    obj.server = True

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
        if key not in provider_required_params:
            raise KeyError(f'Provider not found: {key}')

        provider_config = config_dict['providers'][key]
        if not isinstance(provider_config, Dict):
            raise TypeError(f'Provider {key} must be a dict.')

    def command_option_map(com: click.Command, option: str) -> str:
        for par in com.params:
            if option == par.name:
                return option
            for opt in par.opts:
                if option_name(opt) == option:
                    return par.name
        raise ValueError(f'Option not found: {option}')

    # Build tasks
    task_list: List[Task] = []
    for provider_key, provider_config in config_dict['providers'].items():
        global_config = {}

        command = provider_map[provider_key].command

        if 'global' in provider_config.keys():
            if not isinstance(provider_config['global'], Dict):
                raise TypeError('Global config must be a dict.')
            for key, value in provider_config['global'].items():
                # Additional check for global config
                if not hasattr(obj, key):
                    raise KeyError(f'{key} is not a valid global option.')

                if key == 'mode':
                    if value not in ['till_now', 'year']:
                        raise ValueError(f'{value} is not a valid mode.')
                elif key == 'year':
                    if not isinstance(value, int):
                        raise TypeError('Year must be an integer.')
                    if value < 2000 or value > datetime.now().year:
                        raise ValueError(f'{value} is not a valid year.')
                elif key == 'file_type':
                    if value not in ['png', 'svg']:
                        raise ValueError(f'{value} is not a supported file type.')
                elif key == 'color':
                    if not isinstance(value, str):
                        raise TypeError('Color must be a string.')
                    if value not in color_list:
                        raise ValueError(f'{value} is not a valid color.')

                global_config[key] = value
                provider_config.pop('global')

        replace_keys = []
        for key, value in provider_config.items():
            mapped_option = command_option_map(command, key)
            if key != mapped_option:
                replace_keys.append((key, mapped_option))
        for old, new in replace_keys:
            provider_config[new] = provider_config.pop(old)

        if not set(provider_config.keys()).issuperset(set(provider_required_params[provider_key])):
            raise KeyError(
                'Provider {key} is missing required params: '
                f'{set(provider_required_params[provider_key]) - set(provider_config.keys())}')
        task_list.append(Task(ctx, command, global_config, provider_config))

    def ensure_cache():
        for queue_task in task_list:
            queue_task.ensure_cache(quiet=True)

    threading.Thread(target=ensure_cache).start()

    def update_cache():
        for queue_task in task_list:
            queue_task.ensure_cache()

    schedule.every().day.at('00:00').do(update_cache)

    def loop():
        while True:
            wait_time = schedule.idle_seconds()
            time.sleep(wait_time)
            schedule.run_pending()

    regen = threading.Thread(target=loop)
    regen.daemon = True
    regen.start()

    # Build tasks hash table
    tasks_hash_table = {}
    for task in task_list:
        click.echo(f'Valid task: {task.task_name()}')
        tasks_hash_table[task.task_hash()] = task

    @app.router.http('/{filehash}')
    async def handler():
        filehash = indexpy.request.path_params.get('filehash')
        if filehash not in tasks_hash_table:
            return indexpy.HttpResponse(status_code=404)
        return indexpy.FileResponse(filepath=str(tasks_hash_table[filehash].cache_path()))

    @app.router.http('/')
    async def map_list():
        ret = []
        for task_hash, task_item in tasks_hash_table.items():
            ret.append((task_item.command.name, task_hash))

        return indexpy.JSONResponse(ret)

    # noinspection PyTypeChecker
    uvicorn.run(app, host=config_dict['host'], port=config_dict['port'])


app = indexpy.Index()

if __name__ == '__main__':
    cli()
