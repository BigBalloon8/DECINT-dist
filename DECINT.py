import click
import install_decint
import node
import time
import pickle
from ecdsa import SigningKey, VerifyingKey, SECP112r2
import boot
import os

@click.command()
@click.option("--install", "-i", is_flag=True, help="Will Install DecInt")
@click.option("--update", "-u", is_flag=True, help="Will send Update protocol to other nodes")
@click.option("--delete", "-d", is_flag=True, help="Will send Delete protocol to other nodes")
@click.option("--run_node", "-r", is_flag=True, help="Will run node, you can also give no option to do the same thing")
@click.option("--test_install", "-ti", is_flag=True)
def run(install, update, delete, run_node, test_install):

    if install:
        with open(f"{os.path.dirname(__file__)}./info/Public_key.txt", "r") as file:
            key = file.read()
        if not key:
            node.get_nodes()
            install_decint.run()
        else:
            click.echo("DECINT is already installed (if DECINT is not installed run install_decint.py)\n")

    elif update:
        node.get_nodes()
        click.echo("In order to update your Node please enter a bit of information")
        time.sleep(2)
        with open(f"{os.path.dirname(__file__)}./info/Public_key.txt", "r") as file:
            pub_key = file.read()
        click.echo("\nLeave Port blank to use default")
        port = click.prompt("Enter Port", default="1379")
        port = str(port)
        version = str(node.__version__)
        click.echo("\nNew Public Key is required if you are changing Keys, please use the old Enter Private Key when Prompted")
        new_key = click.prompt("Enter New Public Key")
        priv_key = click.prompt("Enter Private Key")
        node.update(pub_key, port, version, priv_key, new_key)

    elif delete:
        node.get_nodes()
        click.echo("In order to delete your Node please enter a bit of information")
        time.sleep(2)
        with open(f"{os.path.dirname(__file__)}./info/Public_key.txt", "r") as file:
            pub_key = file.read()
        priv_key = click.prompt("Private Key", type=str)
        node.delete(pub_key, priv_key)

    elif test_install:
        node.get_nodes()
        install_decint.test_install()

    elif run_node:
        boot.run()

    else:
        boot.run()

if __name__ == '__main__':
    run()