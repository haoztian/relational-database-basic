"""Smoke tests for the s1x series (raw SQL via text())."""

import sys
from pathlib import Path

# Add examples directory to Python path so we can import the scripts
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "01-crud-two-styles"
sys.path.insert(0, str(EXAMPLES_DIR))


def test_s11_create_table_raw_sql():
    """Smoke test: s11_create_table.py runs without crashing.

    Importing the script executes its top-level code:
    - Creates an engine
    - Executes CREATE TABLE
    - Verifies the table exists

    If any of this fails, the import raises an exception and the test fails.
    """
    from s11_create_table import engine

    assert engine is not None
    assert hasattr(engine, "connect"), "engine should be a SQLAlchemy Engine"


def test_s12_insert_data_raw_sql():
    """Smoke test: s12_insert_data.py runs without crashing.

    Top-level code:
    - Creates engine and table
    - Inserts data using text() and bound parameters
    - Verifies the inserts worked

    If binding fails, INSERT fails, or any SQL is malformed, this test fails.
    """
    from s12_insert_data import engine

    assert engine is not None


def test_s13_select_data_raw_sql():
    """Smoke test: s13_select_data.py runs without crashing.

    Top-level code:
    - Creates engine and table
    - Inserts seed data
    - Runs multiple SELECT queries with different WHERE clauses, ORDER BY, etc.

    If any SELECT is malformed or the table doesn't exist, this test fails.
    """
    from s13_select_data import engine

    assert engine is not None


def test_s14_update_data_raw_sql():
    """Smoke test: s14_update_data.py runs without crashing.

    Top-level code:
    - Creates engine and table
    - Inserts seed data
    - Runs UPDATE queries (by PK, multi-row, expressions like age = age + 1)

    If any UPDATE is malformed or constraint violations occur, this test fails.
    """
    from s14_update_data import engine

    assert engine is not None


def test_s15_delete_data_raw_sql():
    """Smoke test: s15_delete_data.py runs without crashing.

    Top-level code:
    - Creates engine and table
    - Inserts seed data
    - Runs DELETE queries (by PK, by WHERE, DELETE all rows vs DROP table)

    If any DELETE is malformed or violates constraints, this test fails.
    """
    from s15_delete_data import engine

    assert engine is not None
