# relational-database-basic

This project teaches the fundamentals of relational databases through practical Python examples. It's designed for beginners who want to understand how databases work and how to use SQL in Python. You'll learn the core concepts of relational databases, raw SQL syntax, and how to execute CRUD operations (create, insert, select, update, delete) using both raw SQL strings and Python's SQLAlchemy Core Expression language.

## Install & run

You'll need Python 3.12+ and `uv` (the fast Python package manager). Clone the repo and run:

```bash
uv run python examples/01-crud-two-styles/s11_create_table.py
```

`uv` will automatically install dependencies and run the script. Start with the `s1x` series (s11 through s15) to understand raw SQL syntax and concepts — this foundation makes the `s2x` series (s21 through s25) much easier to follow. If you're already comfortable with raw SQL, you can skip directly to `s2x`.

## What I learned

I was surprised to discover that Python can handle database operations directly through SQLAlchemy. The most valuable skill I gained is understanding how to use Python to manipulate databases effectively. The trickiest concepts were bound parameters and their security implications — learning why `text("SELECT * WHERE id = :id")` is safer than string concatenation, and understanding the subtle differences between `engine.begin()` and `engine.connect()`. These details seemed cryptic at first, but going through the examples clarified how they work and why they matter.

## What's next

Next steps include adding a comprehensive test suite to verify that database operations behave as expected, and building a third series that explores SQLAlchemy's ORM layer. Beyond this project, I want to dive into more advanced database concepts like indexing, query optimization, and working with server-based databases like PostgreSQL.

---

*By Haozhi*
