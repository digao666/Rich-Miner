import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE fan_speed
          (id INTEGER PRIMARY KEY ASC, 
           ming_rig_id VARCHAR(250) NOT NULL,
           ming_card_id VARCHAR(250) NOT NULL,
           ming_card_model VARCHAR(100) NOT NULL,
           fan_position VARCHAR(100) NOT NULL,
           fan_speed INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE temperature
          (id INTEGER PRIMARY KEY ASC, 
           ming_rig_id VARCHAR(250) NOT NULL,
           ming_card_id VARCHAR(250) NOT NULL,
           ming_card_model VARCHAR(100) NOT NULL,
           core_temperature INTEGER NOT NULL,
           shell_temperature INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
