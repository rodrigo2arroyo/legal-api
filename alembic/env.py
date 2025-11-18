from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 🧩 importa tu Base desde donde definas los modelos
from app.domain.models.models import Base  # ajusta la ruta según tu proyecto

# Alembic Config
config = context.config

# 💾 URL de conexión directa (local)
config.set_main_option(
    "sqlalchemy.url",
    "postgresql+psycopg2://postgres:Rmdcp0212.@ls-7c5f4a49653d8bcb1b6503d35413aba4c7aae80f.c81c86042ons.us-east-1.rds.amazonaws.com:5432/legal_db_dev"
)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de los modelos
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
