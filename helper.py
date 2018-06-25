import click
import asyncio
from services.ec2 import EC2
from services.rds import RDS


@click.group()
def cli():
    pass


@cli.group()
def ec2():
    pass


@ec2.command(name='show')
def ec2_show():
    ec2 = EC2()
    run(ec2.show())


@cli.group()
def rds():
    pass


@rds.command(name='show')
@click.argument('fields', nargs=-1)
def rds_show(fields):
    if not fields:
        fields = ('region', 'proj', 'engine', 'type')
    rds = RDS()
    run(rds.show(fields))


def run(coro):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coro)
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()


if __name__ == '__main__':
    cli()
