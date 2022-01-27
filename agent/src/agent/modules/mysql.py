import mysql.connector


# it's going to be replaced with jdbc pipeline
class MySQL:
    def __init__(self, host: str, port: str, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def execute(self, query: str) -> (list, list[tuple]):
        db = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        cursor = db.cursor()
        cursor.execute(query)
        columns = [i[0] for i in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        db.close()
        return data
