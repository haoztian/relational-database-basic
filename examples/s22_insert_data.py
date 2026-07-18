# -*- coding: utf-8 -*-

"""
Example 22 - Insert Data (the "C" in CRUD)
==========================================

Goal of this script:
    Now that we know how to create a table, learn how to put rows into it.
    "Insert" is the database word for "add a new row". In CRUD - Create,
    Read, Update, Delete - this is the "Create" operation.

What you will see:
    1. Inserting a single row.
    2. Inserting many rows in one call (much faster than a loop of singles).
    3. Reading the rows back so we can prove they really landed.

A note on connections and ``engine.begin()``:
    To send SQL we need an open connection. The pattern
    ``with engine.begin() as conn:`` does three things in one line:
      - opens a connection,
      - starts a transaction,
      - commits automatically at the end of the block (or rolls back if an
        exception is raised inside the block).
    For now you can read it as: "do all my database work inside this block
    and save the result when the block ends." We will not dwell on
    transactions in this beginner course.
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
)

from utils import print_table

# ----------------------------------------------------------------------------
# Setup: same in-memory database and same table definition as Example 21.
# ----------------------------------------------------------------------------
# Each script in this folder is fully self-contained because an in-memory
# SQLite database disappears the moment its Python process exits. That means
# we cannot "carry over" the table from script s01; we must redefine and
# recreate it here. Reading the same setup five times also reinforces the
# pattern in your memory.
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


# ----------------------------------------------------------------------------
# Insert ONE row at a time.
# ----------------------------------------------------------------------------
# ``insert(users_table).values(...)`` builds an INSERT statement. It does NOT
# send it; it just returns a Python object that represents the SQL. We then
# pass that object to ``conn.execute(...)`` to actually run it.
#
# Why don't we set ``id``? Because ``id`` is an integer primary key, SQLite
# will assign the next available value for us. Letting the database pick the
# id is the default and the simplest pattern.
with engine.begin() as conn:
    stmt = insert(users_table).values(name="Alice", age=30, email="alice@example.com")
    result = conn.execute(stmt)

    # ``inserted_primary_key`` tells us which id the database picked for the
    # row we just added. Useful when the application needs to remember the
    # new row's id (e.g., to show it back to the user).
    print("\nInserted Alice. Her new id =", result.inserted_primary_key)


# ----------------------------------------------------------------------------
# Insert MANY rows in a single call.
# ----------------------------------------------------------------------------
# Calling ``conn.execute(stmt, list_of_dicts)`` runs the statement once for
# each dictionary in the list. The database driver can batch these, so it is
# much faster than calling ``execute`` in a Python ``for`` loop.
#
# This pattern is called "executemany". Notice that we pass the data as a
# list of plain dicts - one dict per row - and we do NOT call ``.values()``
# on the statement when doing it this way.
with engine.begin() as conn:
    conn.execute(
        insert(users_table),
        [
            {"name": "Bob", "age": 25, "email": "bob@example.com"},
            {"name": "Carol", "age": 41, "email": "carol@example.com"},
            {"name": "Dave", "age": 19, "email": "dave@example.com"},
        ],
    )
    print("\nInserted 3 more users in one call.")


# ----------------------------------------------------------------------------
# Read everything back to confirm the inserts.
# ----------------------------------------------------------------------------
# We have not formally covered SELECT yet (that is Example 23), but we use a
# tiny taste of it here just to verify the writes succeeded. The point is:
# whatever you insert, you can immediately read back.
#
# Instead of looping and printing raw tuples, we hand the cursor result to
# our shared ``print_table`` helper, which renders it as a nice ASCII table
# with column headers. Every example script in this folder uses the same
# helper so the output style stays consistent.
with engine.connect() as conn:
    print_table(
        conn.execute(select(users_table)),
        title="Current contents of users",
    )
