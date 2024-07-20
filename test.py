import mysql.connector
from mysql.connector import errorcode


def action_test_connection():
    config = {
        "db": "ocsweb",
        "host": "10.0.0.51",
        "port": 3306,
        "user": "desoftocs",
        "passwd": "desarrollo",
    }

    try:
        conn = mysql.connector.connect(
            user="desoftocs",
            passwd="desarrollo",
            host="10.0.0.51",
            db="ocsweb",
            port=3306,
        )
        # conn.close()
        print("Connection established successfully!!.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        conn.close()
    # elif platform == 'linux' and self.connector == 'mssql':
    #     try:
    #         conn = Mssql.connect(
    #             host=data['Server'], user=data['uid'], passwd=data['pwd'],
    #             db=data['database'], port=int(data['port'])
    #         )

    #         conn.close()
    #         self.message_post(body=_('Connection established successfully!!.'))

    #     except Exception:
    #         self.message_post(body=_('Connection failed!!. Check your data connection in Linux System.'))

    # elif platform == 'win32' and self.connector == 'mssql':
    #     try:
    #         conn = Mssql.connect(**data)
    #         self.message_post(body=_('Connection established successfully!!.'))
    #         conn.close()

    #     except Exception:
    #         self.message_post(body=_('Connection failed!!. Check your data connection.'))


# action_test_connection()
