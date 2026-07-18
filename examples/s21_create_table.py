# -*- coding: utf-8 -*-

"""
Example 21 - Create a Table
===========================

Goal of this script:
    Show the absolute minimum needed to create a table in a SQLite database
    using SQLAlchemy 2.0 Core (the "Table" API, not the ORM).

Mental model for a complete beginner:
    A "relational database" is just a collection of spreadsheets that we call
    "tables". Each table has named columns (like spreadsheet headers) and
    typed values (numbers, text, etc.). Before we can store any rows, we must
    first describe the shape of that table - this is what we do here.

Why SQLite + in-memory?
    SQLite is a tiny database engine that lives inside a single file - or,
    if we ask for it, entirely inside RAM. Using ``sqlite:///:memory:`` means
    nothing is written to disk: the database appears when the script starts
    and disappears when the script exits. That is perfect for learning,
    because every run starts from a clean slate and we never have to worry
    about stale data, file paths, or cleanup.

Why SQLAlchemy Core (Table) instead of ORM?
    The ORM (Object-Relational Mapper) lets you treat rows as Python objects.
    That is convenient in real applications but adds extra concepts (mapped
    classes, sessions, identity map) that can confuse beginners. The Core
    "Table" API stays close to raw SQL while still being Pythonic, so you can
    see clearly which SQL statements are produced.
"""

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    inspect,
    select,
)

from utils import print_table

# ----------------------------------------------------------------------------
# Step 1: Create an "engine".
# ----------------------------------------------------------------------------
# An ``Engine`` is SQLAlchemy's handle to a database. Think of it as a phone
# number that knows how to call the database. Creating the engine does NOT
# actually connect yet - the first real connection happens lazily when we
# run a statement.
#
# The URL ``sqlite:///:memory:`` is decoded as:
#   - ``sqlite``     : use the SQLite dialect (driver)
#   - ``:memory:``   : open the database in RAM only (no file on disk)
#
# ``echo=True`` makes SQLAlchemy print every SQL statement it sends to the
# database. This is extremely useful while learning - you can see exactly
# what SQL your Python code becomes.
engine = create_engine("sqlite:///:memory:", echo=True)


# ----------------------------------------------------------------------------
# Step 2: Create a ``MetaData`` registry.
# ----------------------------------------------------------------------------
# ``MetaData`` is just a container that remembers every table you define
# against it. Later, when we ask "please create all my tables in the real
# database", SQLAlchemy looks at this registry to know what to create.
#
# In a small project like this one, a single shared ``MetaData`` object is
# enough. You almost never need more than one.
metadata = MetaData()


# ----------------------------------------------------------------------------
# Step 3: Describe the "users" table in Python.
# ----------------------------------------------------------------------------
# This is a *description*, not the table itself. We are telling SQLAlchemy:
# "When I say ``users_table``, I mean a table named 'users' that has these
# four columns with these data types." No SQL is sent to the database yet.
#
# Column choices and why:
#   - id      : Integer + primary_key=True
#               Every row needs a unique identifier so we can refer to it
#               later (update this row, delete that row). The "primary key"
#               is the column the database uses to identify a row uniquely.
#               For SQLite, an integer primary key auto-increments by default,
#               so we don't have to supply the id ourselves on insert.
#   - name    : String, nullable=False
#               Names are short text. ``nullable=False`` means "this column
#               must always have a value" - you cannot insert a user with no
#               name. It catches mistakes early.
#   - age     : Integer, nullable=True (the default)
#               Age is a whole number. We allow it to be missing because a
#               user might not have provided it.
#   - email   : String, unique=True
#               ``unique=True`` tells the database to reject any insert that
#               would duplicate an existing email. The database itself
#               enforces this rule, so even buggy application code cannot
#               break the invariant.
users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("age", Integer),
    Column("email", String, unique=True),
)


# ----------------------------------------------------------------------------
# Step 4: Actually create the table inside the database.
# ----------------------------------------------------------------------------
# ``metadata.create_all(engine)`` walks every Table registered on this
# MetaData and issues a ``CREATE TABLE IF NOT EXISTS ...`` statement for it.
# This is the moment Python finally talks to the database.
#
# Because we used ``echo=True`` on the engine, you will see the generated
# CREATE TABLE SQL printed in the terminal. Compare it to the Python
# definition above - they describe the same thing.
metadata.create_all(engine)


# ----------------------------------------------------------------------------
# Step 5: Verify the table actually exists.
# ----------------------------------------------------------------------------
# The ``inspect`` helper opens a read-only view of the database's schema
# (its list of tables, columns, indexes, etc.). We use it here purely as a
# sanity check, to prove that the CREATE TABLE in Step 4 really happened.
inspector = inspect(engine)
print("\n--- Verification ---")
print("Tables in the database:", inspector.get_table_names())
print("Columns of 'users':")
for col in inspector.get_columns("users"):
    # Each ``col`` is a dict with keys like name, type, nullable, ...
    print(f"  - {col['name']:8s} type={col['type']!s:10s} nullable={col['nullable']}")


# ----------------------------------------------------------------------------
# Step 6: Show the (still empty) table via our pretty-printer.
# ----------------------------------------------------------------------------
# We have not inserted anything yet, so SELECT * FROM users has zero rows.
# Printing it with ``print_table`` confirms two things at once:
#   - the table really exists (otherwise the SELECT would error), and
#   - its columns are exactly the four we declared above.
# Subsequent example scripts will use the same helper to display data.
with engine.connect() as conn:
    print_table(conn.execute(select(users_table)), title="users (empty)")
