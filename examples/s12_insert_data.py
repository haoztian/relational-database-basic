# -*- coding: utf-8 -*-

"""
Example 12 - Insert Data with RAW SQL (the "C" in CRUD)
=======================================================

Goal of this script:
    Now that we know how to create a table, learn how to put rows into it
    using raw SQL. "Insert" is the database word for "add a new row". In
    CRUD - Create, Read, Update, Delete - this is the "Create" operation.

What you will see:
    1. Inserting a single row with bound parameters.
    2. Inserting many rows in one call (much faster than a loop of singles).
    3. Reading the rows back so we can prove they really landed.

A note on bound parameters (very important!): 问题：为什么'{name}'的方式是危险的？会rewrite？
    NEVER build a SQL string by concatenating or f-string-formatting raw
    values. The line
        text(f"INSERT INTO users(name) VALUES ('{name}')")
    looks innocent but is the classic recipe for SQL injection - a hostile
    value of ``name`` could rewrite the rest of the statement. Always use
    *bound parameters* instead: write ``:name`` in the SQL string and pass
    the real value separately as a dict. SQLAlchemy hands the value to the
    database in a way that cannot break out of its slot.

A note on connections and ``engine.begin()``:
    To send SQL we need an open connection. The pattern
    ``with engine.begin() as conn:`` does three things in one line:
      - opens a connection,
      - starts a transaction,
      - commits automatically at the end of the block (or rolls back if an
        exception is raised inside the block).
"""

from sqlalchemy import create_engine, text

from utils import print_table

# ----------------------------------------------------------------------------
# Setup: same in-memory database and same table definition as Example 11.
# ----------------------------------------------------------------------------
# Each script in this folder is fully self-contained because an in-memory
# SQLite database disappears the moment its Python process exits. That
# means we cannot "carry over" the table from script s11; we must recreate
# it here. Reading the same setup five times also reinforces the pattern
# in your memory.
engine = create_engine("sqlite:///:memory:")

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY,
            name  TEXT NOT NULL,
            age   INTEGER,
            email TEXT UNIQUE
        )
    """))


# ----------------------------------------------------------------------------
# Insert ONE row at a time.
# ----------------------------------------------------------------------------
# The ``:name``, ``:age``, ``:email`` placeholders inside the SQL string
# are *bound parameters*. They are NOT Python variables - they are slots
# that the database driver fills in for us safely. We pass the real values
# as the second argument to ``conn.execute``, in a plain dict whose keys
# match the placeholder names.
#
# Why don't we set ``id``? Because ``id`` is an INTEGER PRIMARY KEY in
# SQLite, the database will assign the next available value automatically.
# Letting the database pick the id is the default and the simplest pattern.
with engine.begin() as conn:
    result = conn.execute(
        text("INSERT INTO users (name, age, email) VALUES (:name, :age, :email)"),
        {"name": "Alice", "age": 30, "email": "alice@example.com"},
    )

    # ``result.lastrowid`` is the SQLite driver's way of telling us which
    # id the database picked for the row we just added. Useful when the
    # application needs to remember the new row's id (e.g. to show it
    # back to the user).
    print("\nInserted Alice. Her new id =", result.lastrowid)


# ----------------------------------------------------------------------------
# Insert MANY rows in a single call.
# ----------------------------------------------------------------------------
# When you pass a *list of dicts* as the second argument to ``execute``,
# SQLAlchemy runs the statement once per dict and lets the driver batch
# the work efficiently. This is much faster than calling ``execute`` in a
# Python ``for`` loop.
#
# The SQL string and its placeholders stay the same; only the data shape
# changes from "one dict" to "list of dicts". This pattern is sometimes
# called "executemany".
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO users (name, age, email) VALUES (:name, :age, :email)"),
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
# We have not formally covered SELECT yet (that is Example 13), but we use
# a tiny taste of it here just to verify the writes succeeded. The point
# is: whatever you insert, you can immediately read back.
#
# Instead of looping and printing raw tuples, we hand the cursor result to
# our shared ``print_table`` helper, which renders it as a nice ASCII
# table with column headers. Every example script in this folder uses the
# same helper so the output style stays consistent.
with engine.connect() as conn:
    print_table(
        conn.execute(text("SELECT * FROM users")),
        title="Current contents of users",
    )
