# -*- coding: utf-8 -*-

"""
Example 23 - Select Data (the "R" in CRUD)
==========================================

Goal of this script:
    Learn how to read rows back out of a table. In CRUD - Create, Read,
    Update, Delete - this is the "Read" operation, and in SQL it is the
    SELECT statement.

What you will see:
    1. Selecting all rows (the simplest possible query).
    2. Selecting only some columns instead of the whole row.
    3. Filtering rows with a WHERE clause.
    4. Ordering and limiting results.
    5. Different ways to consume the result: .all(), .first(), .scalar(),
       and direct iteration.

Why ``with engine.connect()`` here, not ``engine.begin()``?
    SELECT only reads, it never modifies, so there is nothing to commit.
    ``connect()`` opens a plain read-only-style connection without starting
    an explicit transaction block. For pure reads it is the natural choice.
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
# Setup: build the table and seed some data so we have something to query.
# ----------------------------------------------------------------------------
# We seed four users with different ages on purpose. Having a variety of
# values lets us demonstrate WHERE filters and ORDER BY meaningfully.
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
        ],
    )


# ----------------------------------------------------------------------------
# 1. Select every row, every column.
# ----------------------------------------------------------------------------
# ``select(users_table)`` is the SQLAlchemy way of writing
# ``SELECT * FROM users``. ``conn.execute(stmt)`` returns a ``Result`` object
# that is essentially a cursor over the matching rows. Calling ``.all()``
# materializes that cursor into a regular Python list.
#
# Use ``.all()`` when you know the result is small enough to fit in memory.
# For very large queries you would iterate the result instead (see below).
with engine.connect() as conn:
    # ``print_table`` consumes the cursor result and renders it as an ASCII
    # table with column headers. Every example script uses this helper for
    # row-by-row output so the visual style is consistent.
    print_table(conn.execute(select(users_table)), title="1) All rows")


# ----------------------------------------------------------------------------
# 2. Select only specific columns.
# ----------------------------------------------------------------------------
# Passing column objects (e.g. ``users_table.c.name``) instead of the whole
# table tells the database to return only those columns. This is more
# efficient because the database does not have to ship data you will throw
# away, and the returned rows are narrower (fewer fields) too.
#
# ``users_table.c`` is a namespace for the table's columns: ``c`` stands for
# "columns". So ``users_table.c.name`` means "the ``name`` column of users".
with engine.connect() as conn:
    print_table(
        conn.execute(select(users_table.c.name, users_table.c.age)),
        title="2) Only name + age",
    )


# ----------------------------------------------------------------------------
# 3. Filter rows with WHERE.
# ----------------------------------------------------------------------------
# ``.where(condition)`` adds a WHERE clause to the SELECT. The condition uses
# normal Python comparison operators on column objects, and SQLAlchemy
# translates them into the right SQL.
#
# Important: ``users_table.c.age > 25`` does NOT compare numbers in Python;
# it returns a SQL expression object. Only when ``conn.execute(...)`` runs,
# the database compares values row by row.
#
# Tip on safety: never build WHERE clauses by string-formatting user input
# (e.g. f"age > {x}"). Using column expressions like the line below makes
# SQLAlchemy use bound parameters, which prevents SQL injection.
with engine.connect() as conn:
    stmt = select(users_table).where(users_table.c.age > 25)
    print_table(conn.execute(stmt), title="3) Users older than 25")


# ----------------------------------------------------------------------------
# 4. Order and limit.
# ----------------------------------------------------------------------------
# ``order_by`` sorts the result. ``users_table.c.age.desc()`` sorts from
# largest to smallest age (descending). Without ``.desc()`` the default is
# ascending.
#
# ``limit(n)`` keeps only the first ``n`` rows of the (already ordered)
# result. Combining "order then limit" is the standard recipe for queries
# like "the top 2 oldest users".
with engine.connect() as conn:
    stmt = (
        select(users_table)
        .order_by(users_table.c.age.desc())
        .limit(2)
    )
    print_table(conn.execute(stmt), title="4) Top 2 oldest users")


# ----------------------------------------------------------------------------
# 5. Different ways to consume a Result.
# ----------------------------------------------------------------------------
# Once you have run a SELECT, there are several ways to read the result:
#   - ``.all()``    -> list of all rows. Best for small results.
#   - ``.first()``  -> the first row, or ``None`` if there are no rows. Best
#                      when you expect at most one match (e.g. by primary
#                      key) and want to handle "not found" yourself.
#   - ``.scalar()`` -> the first column of the first row. Handy for queries
#                      that return a single value (a count, a name, etc.).
#   - iteration     -> ``for row in result:`` streams rows one at a time. Use
#                      this when the result might be large and you do not
#                      want to load it all into memory at once.
print("\n--- 5) Different consumption styles ---")
with engine.connect() as conn:
    # .first() - fetch one row by id (or None if it does not exist)
    row = conn.execute(
        select(users_table).where(users_table.c.id == 1)
    ).first()
    print("first():", row)

    # .scalar() - fetch one column from one row
    name = conn.execute(
        select(users_table.c.name).where(users_table.c.id == 1)
    ).scalar()
    print("scalar():", name)

    # iteration - good practice for potentially large results
    print("iter():")
    for row in conn.execute(select(users_table)):
        print("  ", row)
