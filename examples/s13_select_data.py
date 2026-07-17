# -*- coding: utf-8 -*-

"""
Example 13 - Select Data with RAW SQL (the "R" in CRUD)
=======================================================

Goal of this script:
    Learn how to read rows back out of a table using raw SQL. In CRUD -
    Create, Read, Update, Delete - this is the "Read" operation, and in
    SQL it is the SELECT statement.

What you will see:
    1. Selecting all rows (the simplest possible query).
    2. Selecting only some columns instead of the whole row.
    3. Filtering rows with a WHERE clause and bound parameters.
    4. Ordering and limiting results.
    5. Different ways to consume the result: .all(), .first(), .scalar(),
       and direct iteration.

Why ``with engine.connect()`` here, not ``engine.begin()``?
    SELECT only reads, it never modifies, so there is nothing to commit.
    ``connect()`` opens a plain read-only-style connection without starting
    an explicit transaction block. For pure reads it is the natural choice.
"""

from sqlalchemy import create_engine, text

from utils import print_table

# ----------------------------------------------------------------------------
# Setup: build the table and seed some data so we have something to query.
# ----------------------------------------------------------------------------
# We seed four users with different ages on purpose. Having a variety of
# values lets us demonstrate WHERE filters and ORDER BY meaningfully.
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
    conn.execute(
        text("INSERT INTO users (name, age, email) VALUES (:name, :age, :email)"),
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
# ``SELECT * FROM users`` is the classic "give me everything" query. The
# star ``*`` means "all columns". ``conn.execute(stmt)`` returns a Result
# object that is essentially a cursor over the matching rows.
#
# Use ``.all()`` (or pass the result to a helper that iterates it) when you
# know the result is small enough to fit in memory. For very large queries
# you would stream rows one at a time instead (see section 5 below).
with engine.connect() as conn:
    # ``print_table`` consumes the cursor result and renders it as an ASCII
    # table with column headers. Every example script uses this helper for
    # row-by-row output so the visual style is consistent.
    print_table(conn.execute(text("SELECT * FROM users")), title="1) All rows")


# ----------------------------------------------------------------------------
# 2. Select only specific columns.
# ----------------------------------------------------------------------------
# Listing column names instead of ``*`` tells the database to return only
# those columns. This is more efficient because the database does not have
# to ship data you will throw away, and the returned rows are narrower
# (fewer fields) too.
#
# Naming the columns explicitly is also good documentation: a reader of
# your code can see exactly which fields the rest of the program is going
# to use.
with engine.connect() as conn:
    print_table(
        conn.execute(text("SELECT name, age FROM users")),
        title="2) Only name + age",
    )


# ----------------------------------------------------------------------------
# 3. Filter rows with WHERE - using a bound parameter.
# ----------------------------------------------------------------------------
# ``WHERE age > :min_age`` keeps only rows where the condition is true.
# The colon-prefixed ``:min_age`` is a bound parameter, NOT a string-
# formatted Python value. We pass the real number as a dict in the second
# argument to ``execute``.
#
# Why bother with parameters here? Because in a real application the value
# of ``min_age`` might come from a web form or an API. If you interpolated
# it with an f-string, a hostile user could turn the SQL into something
# very different from what you intended (SQL injection). Bound parameters
# make that impossible: the value is sent to the database separately and
# is always treated strictly as data.
with engine.connect() as conn:
    stmt = text("SELECT * FROM users WHERE age > :min_age")
    print_table(
        conn.execute(stmt, {"min_age": 25}),
        title="3) Users older than 25",
    )


# ----------------------------------------------------------------------------
# 4. Order and limit.
# ----------------------------------------------------------------------------
# ``ORDER BY age DESC`` sorts the result from largest age down to smallest.
# Without ``DESC`` the default is ascending (``ASC``). ``LIMIT 2`` keeps
# only the first two rows of the (already ordered) result.
#
# Combining "order then limit" is the standard recipe for queries like
# "the top 2 oldest users" or "the most recent 10 orders".
with engine.connect() as conn:
    stmt = text("SELECT * FROM users ORDER BY age DESC LIMIT 2")
    print_table(conn.execute(stmt), title="4) Top 2 oldest users")


# ----------------------------------------------------------------------------
# 5. Different ways to consume a Result.
# ----------------------------------------------------------------------------
# Once you have run a SELECT, there are several ways to read the result:
#   - ``.all()``    -> list of all rows. Best for small results.
#   - ``.first()``  -> the first row, or ``None`` if there are no rows.
#                      Best when you expect at most one match (e.g. by
#                      primary key) and want to handle "not found"
#                      yourself.
#   - ``.scalar()`` -> the first column of the first row. Handy for
#                      queries that return a single value (a count, a
#                      name, etc.).
#   - iteration     -> ``for row in result:`` streams rows one at a time.
#                      Use this when the result might be large and you do
#                      not want to load it all into memory at once.
print("\n--- 5) Different consumption styles ---")
with engine.connect() as conn:
    # .first() - fetch one row by id (or None if it does not exist)
    row = conn.execute(
        text("SELECT * FROM users WHERE id = :id"),
        {"id": 1},
    ).first()
    print("first():", row)

    # .scalar() - fetch one column from one row
    name = conn.execute(
        text("SELECT name FROM users WHERE id = :id"),
        {"id": 1},
    ).scalar()
    print("scalar():", name)

    # iteration - good practice for potentially large results
    print("iter():")
    for row in conn.execute(text("SELECT * FROM users")):
        print("  ", row)
