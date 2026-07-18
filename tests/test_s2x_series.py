"""Smoke tests for the s2x series (SQLAlchemy Core Expression)."""

import sys
from pathlib import Path

# Add examples directory to Python path so we can import the scripts
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "01-crud-two-styles"
sys.path.insert(0, str(EXAMPLES_DIR))


def test_s21_create_table_core_expression():
    """Smoke test: s21_create_table.py runs without crashing.

    Top-level code:
    - Creates an engine (with echo=True to show generated SQL)
    - Defines a MetaData registry
    - Defines a Table object (users_table) with columns
    - Calls metadata.create_all(engine) to create the table in the database

    If MetaData definition is wrong, column types are invalid, or the database
    rejects the CREATE TABLE, this test fails.
    """
    from s21_create_table import engine, metadata

    assert engine is not None
    assert hasattr(engine, "connect"), "engine should be a SQLAlchemy Engine"
    assert metadata is not None
    assert hasattr(
        metadata, "tables"
    ), "metadata should be a MetaData registry with a .tables attribute"


def test_s22_insert_data_core_expression():
    """Smoke test: s22_insert_data.py runs without crashing.

    Top-level code:
    - Creates engine, metadata, and table
    - Builds INSERT statements using insert(table).values(...)
    - Executes single inserts and multi-row inserts (executemany pattern)

    If the Table definition is wrong, column names are misspelled, or
    constraint violations occur, this test fails.
    """
    from s22_insert_data import engine

    assert engine is not None


def test_s23_select_data_core_expression():
    """Smoke test: s23_select_data.py runs without crashing.

    Top-level code:
    - Creates engine, metadata, and table
    - Inserts seed data
    - Builds SELECT statements using select(table).where(...).order_by(...).limit(...)

    If the Table definition is wrong, column names are misspelled, or
    the composition of where/order_by/limit clauses is invalid, this test fails.
    """
    from s23_select_data import engine

    assert engine is not None


def test_s24_update_data_core_expression():
    """Smoke test: s24_update_data.py runs without crashing.

    Top-level code:
    - Creates engine, metadata, and table
    - Inserts seed data
    - Builds UPDATE statements using update(table).where(...).values(...)

    If the Table definition is wrong, the WHERE clause doesn't match column names,
    or the VALUES are invalid, this test fails.
    """
    from s24_update_data import engine

    assert engine is not None


def test_s25_delete_data_core_expression():
    """Smoke test: s25_delete_data.py runs without crashing.

    Top-level code:
    - Creates engine, metadata, and table
    - Inserts seed data
    - Builds DELETE statements using delete(table).where(...)

    If the Table definition is wrong, the WHERE clause is malformed,
    or constraint violations occur, this test fails.
    """
    from s25_delete_data import engine

    assert engine is not None
