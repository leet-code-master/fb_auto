from sqlalchemy import text


def clear_all_tables(engine):
    with engine.begin() as conn:
        conn.execute(text('PRAGMA foreign_keys=OFF;'))
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")).fetchall()
        for (table_name,) in tables:
            conn.execute(text(f'DELETE FROM "{table_name}";'))
        conn.execute(text('PRAGMA foreign_keys=ON;'))


def format_datetime(dt):
    if not dt:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")
