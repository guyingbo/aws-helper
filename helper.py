import typer
import asyncio
from services.ec2 import EC2
from services.rds import RDS


app = typer.Typer()
ec2 = typer.Typer()
rds = typer.Typer()
app.add_typer(ec2, name="ec2")
app.add_typer(rds, name="rds")


@ec2.command(name="show")
def ec2_show():
    ec2 = EC2()
    run(ec2.show())


@ec2.command()
def list_vpcs():
    ec2 = EC2()
    run(ec2.list_vpcs())


@rds.command(name="show")
def rds_show():
    rds = RDS()
    run(rds.show())


def run(coro):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coro)
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()


if __name__ == "__main__":
    app()
