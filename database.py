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

        try:
            self.cursor.execute(sql, val)
            self.conn.commit()
            return self.cursor.lastrowid
        except:
            print("error while inserting")
            return False

    def updateId(self, id, **kwargs):
        data = ""
        i = 0
        for key, value in kwargs.items():
            data += f"{key} = '{value}'"
            if i != len(kwargs.items()) - 1: data += ", "
            i += 1

        sql = f"UPDATE {self.table} SET {data} WHERE id = {id};" # TODO: add placeholders?

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            print("error while updating")
            return False

    def removeId(self, id):
        sql = f"DELETE FROM {self.table} WHERE id = %s"

        try:
            self.cursor.execute(sql, (id, ))
            self.conn.commit()
        except:
            print("error while removing")
            return False

if __name__ == "__main__":
    measurements = Table(config.configData["dbMeasurementsTable"])
    # measurements.removeId(1)
    # measurements.removeId(2)
    # measurements.removeId(3)