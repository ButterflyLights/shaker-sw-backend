import mysql.connector
import config

class Table:
    def __init__(self, table):
        self.table = table

        self.conn = mysql.connector.connect(
            host=config.configData["dbHost"],
            user=config.configData["dbUser"],
            password=config.configData["dbPassword"],
            database=config.configData["dbName"]
        )

        self.cursor = self.conn.cursor()

    def insert(self, **kwargs):
        columns = ""
        placeholders = ""
        val = []
        i = 0
        for key, value in kwargs.items():
            columns += key
            placeholders += "%s"
            if i != len(kwargs.items()) - 1:
                columns += ", "
                placeholders += ", "
            val.append(value)
            i += 1

        sql = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        
        print(sql)
        print(val)

        try:
            self.cursor.execute(sql, val)
            self.conn.commit()
            return self.cursor.lastrowid
        except:
            print("error while inserting")

    def removeId(self, id):
        sql = f"DELETE FROM {self.table} WHERE id = %s"

        try:
            self.cursor.execute(sql, (id, ))
            self.conn.commit()
        except:
            print("error while removing")

if __name__ == "__main__":
    measurements = Table(config.configData["dbMeasurementsTable"])
    # measurements.removeId(1)
    # measurements.removeId(2)
    # measurements.removeId(3)