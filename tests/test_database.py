from sqlalchemy import inspect
from lightapi.database import engine


def test_database_connection():
    """
        Test that the database connection is established correctly and the required tables are present.

        This test checks if the tables "person" and "company" exist in the database.

        Raises:
            AssertionError: If the tables "person" or "company" are not found.
    """
    inspector = inspect(engine)
    assert inspector.has_table("person")
    assert inspector.has_table("company")


def test_database_engine_type():
    """
    Test that the database engine is of the correct type.

    This test checks if the database URL starts with "sqlite", indicating that the SQLite database engine is used.

    Raises:
        AssertionError: If the database URL does not start with "sqlite".

    """
    assert str(engine.url).startswith("sqlite")


def test_database_session():
    """
   Test that a database session can be created successfully.

   This test ensures that the SessionLocal instance can create a session and that the session is not None.

    Raises:
        AssertionError: If the session is None.

    """
    from lightapi.database import SessionLocal
    session = SessionLocal()
    assert session is not None
    try:
        session.execute('Select 1')
    except Exception as e:
        raise AssertionError(f'Session could not perform the operation (SELECT): {e}')
    finally:
        session.close()