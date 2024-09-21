import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Alembic Config object
config = context.config

# Set up loggers
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Get the database engine
def get_engine():
    return current_app.extensions['migrate'].db.get_engine()

# Set the SQLAlchemy URL
config.set_main_option('sqlalchemy.url', 'mysql+mysqlconnector://root:Mokshagna%%40123@localhost/data1?charset=utf8mb4')


# Import your models here
from models import db, Login, Artist, Picture, Value

  # Adjust the import path
target_metadata = db.Model.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
