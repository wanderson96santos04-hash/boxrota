import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.settings import settings
from app.db.base import Base  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def normalize_database_url(url: str) -> str:
    """
    Normaliza URLs comuns para o SQLAlchemy/Alembic.
    - Alguns provedores retornam "postgres://", mas o driver esperado aqui é "postgresql+psycopg://".
    """
    if not url:
        return url
    u = url.strip()
    if u.startswith("postgres://"):
        u = u.replace("postgres://", "postgresql+psycopg://", 1)
    return u


def get_url() -> str:
    url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
    url = normalize_database_url(url)
    if not url:
        raise RuntimeError("DATABASE_URL não configurada para migrations.")
    return url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()