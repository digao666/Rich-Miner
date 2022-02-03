import sqlite3

conn = sqlite3.connect('readings.sqlite')


c = conn.cursor()
c.execute('''
          DROP TABLE temperature
          ''')
c.execute('''
          DROP TABLE fan_speed
          ''')
conn.commit()
conn.close()
