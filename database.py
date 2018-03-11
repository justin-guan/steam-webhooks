import psycopg2


class DatabaseHandler:
    dbname = None
    user = None
    password = None
    host = None
    port = None

    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def _connect(self):
        connection = psycopg2.connect(dbname=self.dbname,
                                      user=self.user,
                                      password=self.password,
                                      host=self.host,
                                      port=self.port)
        return connection

    def create_tables(self):
        connection = None
        try:
            connection = self._connect()
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS games ("
                           "appid INT PRIMARY KEY,"
                           "gid BIGINT NOT NULL,"
                           "date BIGINT NOT NULL"
                           ")")
            connection.commit()
            cursor.close()
        except psycopg2.DatabaseError as error:
            print(error)
        finally:
            if connection is not None:
                connection.close()

    def get_last_seen(self, appid):
        connection = None
        try:
            connection = self._connect()
            cursor = connection.cursor()
            cursor.execute("SELECT * "
                           "FROM games "
                           "WHERE appid=%s",
                           [appid])
            connection.commit()
            rows = cursor.fetchall()
            cursor.close()
            num_rows = len(rows)
            if num_rows > 1:
                raise LookupError("Expected a single last seen result from query for appid %s "
                                  "but found %s instead",
                                  [appid, num_rows])
            if num_rows is 0:
                return appid, 0, 0
            return rows[0]
        except psycopg2.DatabaseError as error:
            print(error)
        finally:
            if connection is not None:
                connection.close()

    def update_last_seen(self, appid, gid, date):
        connection = None
        try:
            connection = self._connect()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO games (appid, gid, date) " 
                           "VALUES (%s, %s, %s) " 
                           "ON CONFLICT (appid) DO UPDATE " 
                           "SET (gid, date) = (EXCLUDED.gid, EXCLUDED.date)",
                           [appid, gid, date])
            connection.commit()
            cursor.close()
        except psycopg2.DatabaseError as error:
            print(error)
        finally:
            if connection is not None:
                connection.close()
