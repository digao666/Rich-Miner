import sqlite3

conn = sqlite3.connect('stats.sqlite')
c = conn.cursor()
c.execute('''
    CREATE TABLE stats
    (id INTEGER PRIMARY KEY ASC,
    num_core_temp INTEGER NOT NULL,
    num_shell_temp INTEGER NOT NULL,
    avg_shell_temp FLOAT NOT NULL,
    avg_core_temp FLOAT	 NOT NULL,
    num_fan_speed INTEGER NOT NULL,
    avg_fan_speed FLOAT	 NOT NULL,
    last_updated VARCHAR(100) NOT NULL)
''')
conn.commit()
conn.close()
