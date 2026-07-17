# -*- coding: utf-8 -*-

"""
Shared helpers for the example scripts.
=======================================

Why this file exists:
    Every example script wants to dump query results in a way that a human
    can actually read. Printing rows as raw tuples like
        (1, 'Alice', 30, 'alice@example.com')
    is fine for one or two columns, but quickly becomes hard to scan. The
    ``prettytable`` library renders rows as an ASCII table with column
    headers, which is much friendlier - especially for beginners who are
    still building a mental model of "rows and columns".

    Centralizing this helper means all five example scripts produce visually
    consistent output, and we keep each script focused on its CRUD topic
    instead of repeating boilerplate print loops.
"""

from prettytable import PrettyTable
from sqlalchemy import CursorResult


def print_table(result: CursorResult, title: str = "") -> None:
    """Pretty-print a SQLAlchemy cursor result as an ASCII table.

    :param result: the object returned by ``connection.execute(select(...))``.
        It behaves like an iterator over rows and exposes ``.keys()`` for the
        column names. Note that it is *single-use*: once this helper iterates
        through it, the caller cannot read it again. That is exactly what we
        want in these teaching scripts - print once and move on.
    :param title: optional human-readable label printed above the table so
        the reader knows which step they are looking at (e.g. "After insert",
        "Top 2 oldest"). Pass an empty string to skip the header line.
    """
    # ``result.keys()`` returns the column names of the SELECT, in the same
    # order as the values inside each row. We materialize them into a plain
    # list so PrettyTable can use them as the header row.
    columns = list(result.keys())

    table = PrettyTable()
    table.field_names = columns

    # We let PrettyTable left-align text columns. The default is centered,
    # which looks fine for short values but makes longer text harder to
    # compare row-by-row.
    table.align = "l"

    # Iterate the cursor and add one ASCII row per database row. Wrapping
    # ``row`` in ``list(...)`` works because each SQLAlchemy ``Row`` is
    # tuple-like (it is iterable in column order).
    for row in result:
        table.add_row(list(row))

    if title:
        print(f"\n--- {title} ---")
    print(table)
