# -*- coding: utf-8 -*-

"""
Example 11 - Create a Table (with RAW SQL)
==========================================

Goal of this script:
    Show the absolute minimum needed to create a table in a SQLite database
    by sending raw SQL strings through SQLAlchemy. This is the most direct
    way to talk to a database from Python: you write SQL by hand, and
    SQLAlchemy just ships it over the wire for you.

Why raw SQL first?
    Before you learn SQLAlchemy's Pythonic "Core" or "ORM" APIs, it pays to
    see plain SQL with your own eyes. The higher-level APIs are convenient
    but they hide the SQL from you, and that makes it harder to understand
    what is happening when something breaks. If you can read and write SQL
    yourself, the Pythonic layer on top becomes much easier to learn later.

Mental model for a complete beginner:
    A "relational database" is just a collection of spreadsheets that we call
    "tables". Each table has named columns (like spreadsheet headers) and
    typed values (numbers, text, etc.). Before we can store any rows, we
    must first describe the shape of that table - this is what we do here,
    but in SQL.

Why SQLite + in-memory?
    SQLite is a tiny database engine that lives inside a single file - or,
    if we ask for it, entirely inside RAM. Using ``sqlite:///:memory:`` means
    nothing is written to disk: the database appears when the script starts
    and disappears when the script exits. That is perfect for learning,
    because every run starts from a clean slate and we never have to worry
    about stale data, file paths, or cleanup.

What is ``sqlalchemy.text(...)``?
    ``text("...")`` wraps a raw SQL string in a small object that SQLAlchemy
    knows how to execute safely. SQLAlchemy 2.0 requires this explicit
    wrapper for raw SQL, and it is a good habit anyway: it makes "this is
    raw SQL" jump out visually in your Python code.
"""

from sqlalchemy import create_engine, inspect, text

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
# Notice that we do NOT pass ``echo=True`` here. In the raw-SQL world, the
# SQL you send is the SQL you wrote yourself - you can already read it in
# your source file. The ``echo`` flag becomes more useful later, when we
# let SQLAlchemy *generate* SQL for us and we want to peek at what it
# produced.
engine = create_engine("sqlite:///:memory:")


# ----------------------------------------------------------------------------
# Step 2: Write the CREATE TABLE statement in raw SQL.
# ----------------------------------------------------------------------------
# This is plain SQL, exactly the kind you would type into the ``sqlite3``
# command line tool. SQLAlchemy will pass it through to the database
# unchanged.
#
# Column choices and why:
#   - id      : INTEGER PRIMARY KEY
#               Every row needs a unique identifier so we can refer to it
#               later (update this row, delete that row). For SQLite, an
#               INTEGER PRIMARY KEY auto-increments by default, so we don't
#               have to supply the id ourselves on insert.
#   - name    : TEXT NOT NULL
#               Names are short text. ``NOT NULL`` means "this column must
#               always have a value" - you cannot insert a user with no
#               name. It catches mistakes early.
#   - age     : INTEGER (no NOT NULL, so it is optional)
#               Age is a whole number. We allow it to be missing because a
#               user might not have provided it.
#   - email   : TEXT UNIQUE
#               ``UNIQUE`` tells the database to reject any insert that
#               would duplicate an existing email. The database itself
#               enforces this rule, so even buggy application code cannot
#               break the invariant.
#
# We use a Python triple-quoted string so the SQL can span multiple lines
# and stay readable.
create_users_sql = text("""
    CREATE TABLE IF NOT EXISTS users (
        id    INTEGER PRIMARY KEY,
        name  TEXT NOT NULL,
        age   INTEGER,
        email TEXT UNIQUE
    )
""")


# ----------------------------------------------------------------------------
# Step 3: Actually run the CREATE TABLE.
# ----------------------------------------------------------------------------
# ``engine.begin()`` opens a connection AND starts a transaction. The
# ``with`` block commits automatically when it ends successfully, and rolls
# back if an exception is raised inside it. For now you can read it as:
# "do all my database work inside this block and save the result when the
# block ends." We will not dwell on transactions in this beginner course.
#
# This is the moment Python finally talks to the database.
with engine.begin() as conn:
    conn.execute(create_users_sql)


# ----------------------------------------------------------------------------
# Step 4: Verify the table actually exists.
# ----------------------------------------------------------------------------
# The ``inspect`` helper opens a read-only view of the database's schema
# (its list of tables, columns, indexes, etc.). We use it here purely as a
# sanity check, to prove that the CREATE TABLE in Step 3 really happened.
inspector = inspect(engine)
print("\n--- Verification ---")
print("Tables in the database:", inspector.get_table_names())
print("Columns of 'users':")
for col in inspector.get_columns("users"):
    # Each ``col`` is a dict with keys like name, type, nullable, ...
    print(f"  - {col['name']:8s} type={col['type']!s:10s} nullable={col['nullable']}")


# ----------------------------------------------------------------------------
# Step 5: Show the (still empty) table via our pretty-printer.
# ----------------------------------------------------------------------------
# We have not inserted anything yet, so ``SELECT * FROM users`` returns
# zero rows. Printing it with ``print_table`` confirms two things at once:
#   - the table really exists (otherwise the SELECT would error), and
#   - its columns are exactly the four we declared above.
# Subsequent example scripts will use the same helper to display data.
with engine.connect() as conn:
    print_table(conn.execute(text("SELECT * FROM users")), title="users (empty)")
