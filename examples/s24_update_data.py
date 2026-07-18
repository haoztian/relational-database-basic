# -*- coding: utf-8 -*-

"""
Example 24 - Update Data (the "U" in CRUD)
==========================================

Goal of this script:
    Change values of rows that already exist. In CRUD - Create, Read,
    Update, Delete - this is the "Update" operation, and in SQL it is the
    UPDATE statement.

The single most important rule of UPDATE:
    Always use a WHERE clause unless you really mean to modify every row in
    the table. An UPDATE without a WHERE clause silently changes the entire
    table - a very common and very painful beginner mistake.

What you will see:
    1. Updating one specific row (filtered by primary key).
    2. Updating multiple rows that match a condition.
    3. Computing the new value from the old value (age = age + 1).
    4. Reading back the affected rows to confirm the change.
    5. Reading ``rowcount`` to know how many rows were touched.
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
    update,
)

from utils import print_table

# ----------------------------------------------------------------------------
# Setup: build the table and seed it.
# ----------------------------------------------------------------------------
# Same self-contained pattern as the other examples: in-memory DB, table
# definition, seed data. Each script can run on its own without depending on
# the others.
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


def print_all(label: str) -> None:
    """Helper to dump the whole table so we can see UPDATEs taking effect.

    Defined as a small function because we will call it four times below,
    and copy-pasting a SELECT each time would obscure the lesson. Internally
    it delegates to ``print_table`` (in ``utils.py``) for nice formatting.
    """
    with engine.connect() as conn:
        print_table(conn.execute(select(users_table)), title=label)


print_all("State before any update")


# ----------------------------------------------------------------------------
# 1. Update ONE specific row.
# ----------------------------------------------------------------------------
# The pattern is: ``update(table).where(...).values(...)``.
#   - ``where(...)`` decides WHICH rows to change.
#   - ``values(...)`` decides WHAT to change them to.
#
# We filter by ``id == 1`` because primary keys uniquely identify a single
# row, so this can affect at most one row - exactly what we want when we say
# "update Alice's email".
#
# ``result.rowcount`` reports how many rows the database actually modified.
# Checking it is a good habit: if it is 0, your WHERE matched nothing and
# you may have a bug (wrong id, wrong filter).
with engine.begin() as conn:
    stmt = (
        update(users_table)
        .where(users_table.c.id == 1)
        .values(email="alice.new@example.com")
    )
    result = conn.execute(stmt)
    print(f"\n[1] Rows updated: {result.rowcount}")

print_all("After updating Alice's email")


# ----------------------------------------------------------------------------
# 2. Update MULTIPLE rows that match a condition.
# ----------------------------------------------------------------------------
# Here the WHERE clause matches every user younger than 30. UPDATE does not
# care whether the WHERE matches one row or ten - it changes all of them in
# a single statement. That is one of SQL's superpowers.
#
# Concretely: Bob (25) and Dave (19) match, Alice (30) and Carol (41) do
# not, so two rows will be modified.
with engine.begin() as conn:
    stmt = (
        update(users_table)
        .where(users_table.c.age < 30)
        .values(name="YOUNGSTER")
    )
    result = conn.execute(stmt)
    print(f"\n[2] Rows updated: {result.rowcount}")

print_all("After renaming everyone under 30 to 'YOUNGSTER'")


# ----------------------------------------------------------------------------
# 3. Compute the new value from the old value.
# ----------------------------------------------------------------------------
# A very common need is "increment a counter". The right way is to let the
# database do the math, by passing a SQL expression to ``.values()``. Here
# ``users_table.c.age + 1`` is not Python addition - it is a SQL expression
# that becomes ``age = age + 1`` in the generated UPDATE statement.
#
# Why not read the value in Python, add one, and write it back? Two
# reasons:
#   - It is one round-trip to the database instead of two.
#   - It is correct even if many users get a "happy birthday" at the same
#     time, because the database performs the increment atomically per row.
with engine.begin() as conn:
    stmt = update(users_table).values(age=users_table.c.age + 1)
    result = conn.execute(stmt)
    print(f"\n[3] Rows updated (everyone's birthday): {result.rowcount}")

print_all("After everyone aged by 1 year")
