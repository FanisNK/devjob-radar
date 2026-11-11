from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.core.database import Base
from app.models import Job, User


# Get the Alembic configuration object.
# It provides access to settings from alembic.ini.
config = context.config


# Configure Python logging using the Alembic configuration.
# This allows us to see migration messages in the terminal.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Set the database connection URL from our .env file.
# This keeps database credentials out of alembic.ini.
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("%", "%%"),
)


# Register SQLAlchemy metadata.
# Alembic uses this metadata to detect changes in database models.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    # Run migrations without creating a database connection.
    # Alembic generates SQL statements using the configured database URL.
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    # Start a migration transaction.
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Create a database engine using the Alembic configuration.
    # NullPool prevents Alembic from keeping connections open.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Open a connection to the database.
    with connectable.connect() as connection:
        # Configure Alembic to compare models with database tables.
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        # Start a migration transaction.
        with context.begin_transaction():
            context.run_migrations()


# Choose the migration mode depending on the Alembic command.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
