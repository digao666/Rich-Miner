import sqlite3

conn = sqlite3.connect('stats.sqlite')
c = conn.cursor()
c.execute('''
    CREATE TABLE stats
    (id INTEGER PRIMARY KEY ASC,
    num_shell_temp INTEGER NOT NULL,
    num_core_temp INTEGER NOT NULL,
    num_fan_speed INTEGER NOT NULL,
    max_fan_speed INTEGER,
    max_shell_temp INTEGER,
    max_core_temp INTEGER,
    last_updated VARCHAR(100) NOT NULL)
''')
conn.commit()
conn.close()
