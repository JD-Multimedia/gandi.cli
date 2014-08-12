import click

from gandi.cli.core.cli import cli
from gandi.cli.core.utils import output_generic, output_list
from gandi.cli.core.params import pass_gandi


@cli.command()
@click.option('--limit', help='limit number of results', default=100, 
                show_default=True)
@click.argument('domain')
@pass_gandi
def list(gandi, domain, limit):
    """List mailboxes created on a domain"""

    options = {'items_per_page': limit}
    mailboxes = gandi.mailbox.list(domain, options)
    for mailbox in mailboxes:
            gandi.echo(mailbox['login'])

    return mailboxes

@cli.command()
@click.argument('email')
@pass_gandi
def info(gandi, email):
    """Display information about a mailbox"""
    
    email = email.split("@")
    
    login = email[0]
    domain = email[1] 

    output_keys = ['login', 'aliases', 'fallback_email', 'quota', 'responder']    
    mailbox = gandi.mailbox.info(domain, login)
    
    output_generic(gandi, mailbox, output_keys, justify=8)
    
    return mailbox


@cli.command()
@click.option('--quota', help='set a quota on a mailbox. 0 is unlimited', default=False)
@click.option('--fallback', help='add an address of fallback', default="")
@click.argument("email")
@pass_gandi
def create(gandi, email, quota, fallback):
    """Create a mailbox"""

    options = {}
    password = click.prompt('password', hide_input=True,
                                            confirmation_prompt=True)
    
    if quota:
        options['quota'] = quota
    if fallback:
        options['fallback_email'] = fallback

    options['password'] = password

    login, domain = email.split("@")
    result = gandi.mailbox.create(domain, login, options)

    return result

@cli.command()
@click.argument('email')
@pass_gandi
def delete(gandi, email):
    """Delete a mailbox"""
    login, domain = email.split("@")

    proceed = click.confirm("Are you sure to delete the mailbox %s?" % email)
                                                     
    result = gandi.mailbox.delete(domain, login)

    return result

@cli.command()
@click.option('--password', help='prompt a password for a mailbox', is_flag=True)
@click.option('--quota', help='set a quota on a mailbox. 0 is unlimited', 
                                type=click.INT)
@click.option('--fallback', help='add an address of fallback', default="",
                                show_default=True)
@click.argument('email')
@pass_gandi
def update(gandi, email, password, quota, fallback):
    """Update a mailbox"""
    
    options = {}

    if password:
        password = click.prompt('password', hide_input=True,
                                         confirmation_prompt=True)
        options['password'] = password

    if quota:
        options['quota'] = quota

    if fallback:
        options['fallback_email'] = fallback

    login, domain = email.split("@")

    result = gandi.mailbox.update(domain, login, options)
    print result
    return result

@cli.command()
@click.option('--add', '-a', help='add an alias on a mailbox', multiple=True)
@click.option('--delete', '-d', help='remove an alias', multiple=True)
@click.option('--purge', '-p', help='remove all aliases on a mailbox', is_flag=True)
@click.argument('email')
@pass_gandi
def alias(gandi, email, add, delete, purge):
    """Add, remove or purge aliases on a mailbox"""

    login, domain = email.split("@")

    aliases = gandi.mailbox.info(domain, login)['aliases']
    if add:
        for alias in add:
            aliases.append(alias)

    if delete:
        for alias in delete:
            aliases.remove(alias)

    if purge:
        click.confirm("Are you sure to delete all aliases for the mailbox %s?" % email)
        aliases = []

    result = gandi.mailbox.set_alias(domain, login, aliases)
    output_list(gandi, result['aliases'])
    return result