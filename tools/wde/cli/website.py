from wde.cli import *
from wde import utils, container
import os


@prelude.command()
@pass_config
@click.option('-q', '--quiet', 'quiet', default=False, is_flag=True)
@click.argument('domain', default=os.path.basename(os.getcwd()))
def unsecure(cfg: Config, quiet, domain):
    """Unecures given domain and removes self signed certificate from trusted"""
    container.build_cmd(cfg.WDE_NAME, ['valet', 'unsecure'], req_mount=True, cwd=cfg.get_domain(domain)).exec(quiet)
    domain = f'{domain}.{cfg.DOMAIN_SUFFIX}'
    utils.command(f'certutil -d sql:$HOME/.pki/nssdb -D -n "{domain}"', shell=True, capture=True)
    utils.command(f'certutil -d $HOME/.mozilla/firefox/*.default -D -n "{domain}"', shell=True, capture=True)


@prelude.command()
@click.pass_context
@pass_config
@click.option('-q', '--quiet', 'quiet', default=False, is_flag=True)
@click.argument('domain', default=os.path.basename(os.getcwd()))
def secure(cfg: Config, ctx, quiet, domain):
    """Secures given domain and adds self signed certificate as trusted"""
    ctx.invoke(unsecure)
    container.build_cmd(cfg.WDE_NAME, ['valet', 'secure'], req_mount=True, cwd=cfg.get_domain(domain)).exec(quiet)
    domain = f'{domain}.{cfg.DOMAIN_SUFFIX}'
    cert_path = cfg.get_root(f'storage/valet/certificates/{domain}.crt')
    utils.command(f'certutil -d sql:$HOME/.pki/nssdb -A -t TC -n "{domain}" -i "{cert_path}"', shell=True,
                  capture=quiet)
    utils.command(f'certutil -d $HOME/.mozilla/firefox/*.default -A -t TC -n "{domain}" -i "{cert_path}"', shell=True,
                  capture=quiet)
