import mysql.connector

db_conn = mysql.connector.connect(host="localhost", user="root", password="password", database="events")
db_cursor = db_conn.cursor()
db_cursor.execute(''' 
    CREATE TABLE fan_speed (
    id INT NOT NULL AUTO_INCREMENT, 
    ming_rig_id VARCHAR(250) NOT NULL, 
    ming_card_id VARCHAR(250) NOT NULL,
    fan_size INTEGER NOT NULL,
    fan_speed INTEGER NOT NULL,
    timestamp VARCHAR(100) NOT NULL, 
    trace_id VARCHAR(100) NOT NULL, 
    date_created VARCHAR(100) NOT NULL, 
    CONSTRAINT fan_speed_pk PRIMARY KEY (id)) ''')

db_cursor.execute(''' CREATE TABLE temperature (
    id INT NOT NULL AUTO_INCREMENT, 
    ming_rig_id VARCHAR(250) NOT NULL, 
    ming_card_id VARCHAR(250) NOT NULL, 
    timestamp VARCHAR(100) NOT NULL,
    core_temperature INTEGER NOT NULL,
    shell_temperature INTEGER NOT NULL,
    trace_id VARCHAR(100) NOT NULL, 
    date_created VARCHAR(100) NOT NULL, 
    CONSTRAINT temperature_pk PRIMARY KEY (id)) ''')

db_conn.commit()
db_conn.close()
