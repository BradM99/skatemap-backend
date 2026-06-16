from database.db import Base, engine

# This file is just a helper to reset the database after making changes to models until I get around to using Alembic
from database.models import Spot, User, Image


def reset_database():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("Database reset complete")


if __name__ == "__main__":
    reset_database()