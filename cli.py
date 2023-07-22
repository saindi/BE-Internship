import sys
import os

import asyncclick as click

SOURCE_DIR = 'app/'

sys.path.insert(0, os.path.abspath(SOURCE_DIR))


@click.command()
@click.option("--email", prompt="Email", help="Email of the superuser")
@click.option("--username", prompt="Username", help="Username of the superuser")
@click.option("--password", prompt="Password", hide_input=True, confirmation_prompt=True, help="Password of the superuser")
async def create_superuser(email, username, password):
    from db.database import async_session
    from user.models import User
    from utils.hashing import Hasher

    async with async_session() as session:
        hashed_password = Hasher.get_password_hash(password)

        superuser = User(email=email, username=username, hashed_password=hashed_password, is_superuser=True)

        session.add(superuser)
        await session.commit()
        await session.refresh(superuser)

        click.echo(f"Superuser created successfully. {superuser.email}:{superuser.id}")


if __name__ == '__main__':
    create_superuser()