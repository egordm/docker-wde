import os, subprocess, re
import pty
from typing import Optional, Union

import click

from wde import container, config


def get_rel_domain_path(path) -> Optional[str]:
    return container.translate_path(config.get().DOMAIN_PATH, container.get_path('domains'), path)


def get_relative_path(root, path) -> Optional[str]:
    root = os.path.abspath(root)
    path = os.path.abspath(path)
    rel = os.path.relpath(path, root)

    if rel.startswith('..'):
        return None
    else:
        return rel


def asserte(expr: bool, error_msg: str):
    if not expr:
        click.echo(error_msg, err=True)
        exit(1)


def cmd_expect(cmd: Union[list, str], error_msg: str, cwd=None, hide_output=True) -> bool:
    if isinstance(cmd, str):
        res = command(cmd, capture=hide_output, shell=True, cwd=cwd)
    else:
        res = command(cmd, capture=hide_output, shell=False, cwd=cwd)

    asserte(res is not None, error_msg)
    return True


def command(cmd: Union[list, str], cwd=None, capture=True, shell=False) -> Optional[str]:
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE if capture else None,
        cwd=cwd,
        shell=shell
    )
    if capture and result.returncode == 0:
        return str(result.stdout.decode('utf-8').strip())
    elif result.returncode == 0:
        return ''
    else:
        return None


def command_it(cmd: Union[list, str], cwd=None) -> bool:
    old_path = os.getcwd()
    if cwd is not None: os.chdir(cwd)
    code = pty.spawn(cmd)
    os.chdir(old_path)
    return code == 0


def update_ini(name: str, value: str):
    with open(config.get().get_root('.env')) as f:
        lines = f.readlines()

    pattern = re.compile(f'^({re.escape(name)})=.*')
    for i in range(len(lines)):
        if pattern.match(lines[i]):
            lines[i] = f"{name}={value}\n"

    with open(config.get().get_root('.env'), 'w') as f:
        f.writelines(lines)
