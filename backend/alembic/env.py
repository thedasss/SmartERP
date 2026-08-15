"""
Alembic migration environment.
Reads DATABASE_URL from .env and uses the app's async engine directly.
Supports both SQLite (dev) and MySQL (production).
"""
import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# Add backend/ to sys.path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.core.database import Base
import app.models  # noqa: F401 — ensures all models are registered

settings = get_settings()

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

_is_sqlite = settings.database_url.startswith("sqlite")


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=_is_sqlite,  # required for ALTER TABLE with SQLite
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=_is_sqlite,  # required for ALTER TABLE with SQLite
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    # Build engine directly so we control the options (SQLite vs MySQL)
    if _is_sqlite:
        connectable = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            connect_args={"check_same_thread": False},
            poolclass=pool.NullPool,
        )
    else:
        connectable = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            poolclass=pool.NullPool,
        )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
