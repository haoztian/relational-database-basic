# -*- coding: utf-8 -*-

"""
Example 25 - Delete Data (the "D" in CRUD)
==========================================

Goal of this script:
    Remove rows from a table. In CRUD - Create, Read, Update, Delete - this
    is the "Delete" operation, and in SQL it is the DELETE statement.

The single most important rule of DELETE:
    Just like UPDATE, a DELETE without a WHERE clause removes EVERY row in
    the table. That is sometimes what you want (an "empty the table"
    command), but it is almost never what a beginner means. Always think
    about your WHERE clause first, run a matching SELECT to preview what
    you are about to delete, and only then run the DELETE.

What you will see:
    1. Deleting one specific row (filtered by primary key).
    2. Deleting multiple rows that match a condition.
    3. Deleting every row in the table (the dangerous form).
    4. Reading ``rowcount`` to confirm how many rows were removed.
"""

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    insert,
    select,
    delete,
)

from utils import print_table

# ----------------------------------------------------------------------------
# Setup: build the table and seed it with five rows.
# ----------------------------------------------------------------------------
# Five rows is convenient: enough variety to delete some and keep some, but
# small enough that we can print the whole table after each step and visually
# check what changed.
engine = create_engine("sqlite:///:memory:", echo=True)
metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("age", Integer),
    Column("email", String, unique=True),
)

metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(
        insert(users_table),
        [
            {"name": "Alice", "age": 30, "email": "alice@example.com"},
            {"name": "Bob",   "age": 25, "email": "bob@example.com"},
            {"name": "Carol", "age": 41, "email": "carol@example.com"},
            {"name": "Dave",  "age": 19, "email": "dave@example.com"},
            {"name": "Eve",   "age": 22, "email": "eve@example.com"},
        ],
    )


def print_all(label: str) -> None:
    """Print the entire table so we can see DELETEs taking effect.

    Same helper idea as in Example 24: factored out so the focus of the
    script stays on the DELETE statements themselves. Internally it uses
    ``print_table`` (from ``utils.py``) for the actual rendering.
    """
    with engine.connect() as conn:
        print_table(conn.execute(select(users_table)), title=label)


print_all("State before any delete")


# ----------------------------------------------------------------------------
# 1. Delete ONE specific row by primary key.
# ----------------------------------------------------------------------------
# Pattern: ``delete(table).where(...)``. The WHERE clause picks the rows to
# remove. Filtering by ``id`` (the primary key) is the safest form of
# deletion: it can affect at most one row, so there is no risk of taking
# out neighbours by accident.
#
# We check ``result.rowcount`` afterwards. If we expected to delete one row
# and rowcount is 0, that is a strong signal that our id was wrong (maybe
# the row never existed, or was already deleted).
with engine.begin() as conn:
    stmt = delete(users_table).where(users_table.c.id == 2)
    result = conn.execute(stmt)
    print(f"\n[1] Rows deleted: {result.rowcount}")

print_all("After deleting the user with id=2 (Bob)")


# ----------------------------------------------------------------------------
# 2. Delete MULTIPLE rows that match a condition.
# ----------------------------------------------------------------------------
# Here we delete every user under 25. DELETE applies the same WHERE-then-act
# logic as UPDATE: zero, one, or many rows can be removed by a single
# statement. Among the remaining users (Alice 30, Carol 41, Dave 19, Eve 22),
# Dave and Eve match, so two rows are expected to disappear.
#
# Best practice tip: before running a DELETE in real code, run the same
# query as a SELECT first to *preview* what would be deleted:
#
#     conn.execute(select(users_table).where(users_table.c.age < 25)).all()
#
# This is the database equivalent of "measure twice, cut once".
with engine.begin() as conn:
    stmt = delete(users_table).where(users_table.c.age < 25)
    result = conn.execute(stmt)
    print(f"\n[2] Rows deleted: {result.rowcount}")

print_all("After deleting users under 25")


# ----------------------------------------------------------------------------
# 3. Delete EVERY row (the dangerous form).
# ----------------------------------------------------------------------------
# ``delete(users_table)`` with no ``.where(...)`` removes all rows from the
# table. The table itself still exists - its schema is untouched - but it
# is now empty. This is sometimes useful (e.g. clearing a cache table) but
# is irreversible inside this transaction once committed, so be deliberate
# about it.
#
# Compare with two related operations you do NOT want to confuse:
#   - DELETE without WHERE  -> removes all rows, keeps the table.
#   - DROP TABLE            -> removes the table itself, schema and all.
#                              In SQLAlchemy: ``users_table.drop(engine)``.
with engine.begin() as conn:
    result = conn.execute(delete(users_table))
    print(f"\n[3] Rows deleted (whole table): {result.rowcount}")

print_all("After deleting everything")
