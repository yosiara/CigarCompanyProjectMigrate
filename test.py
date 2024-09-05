import mysql.connector
from mysql.connector import errorcode
import pymssql
import re

# from mysql.connector import connection


def action_test_connection():
    config = {
        "db": "ocsweb",
        "host": "10.0.0.51",
        "port": "3306",
        "user": "desoftocs",
        "passwd": "desarrollo",
    }
    config2 = {
        "database": "versat2",
        "host": "10.0.0.23\\versat",
        "port": "1433",
        "user": "consultor2",
        "password": "Turei.101",
    }
    try:
        return pymssql.connect(**config2)
    except pymssql.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    return None


def getDatasSmoke(start_date, end_date):

    datas = {
        "total": 0.0,
        "salidas": [],
        "devoluciones": [],
        "farol": 0.0,
        "cajetillas": 0.0,
        "conceptosArray": [],
        "sumaCantidadArray": [],
    }

    cnx = action_test_connection()
    cursor = cnx.cursor()

    cursor.execute(
        f"""
            SELECT fecha, sum(sumacantidad) as sumacantidad, descripcion, iddocumento
            FROM dbo.inv_documento
            WHERE idconcepto = '64' AND fecha BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY fecha, descripcion, iddocumento
        """
    )

    salidas = cursor.fetchall()
    for rec in salidas:
        print("Rec: ---------> ", rec)

    # datas["devoluciones"] = cursor.execute(
    #     f"""
    #                         SELECT fecha, sum(sumacantidad) as sumacantidad, descripcion, iddocumento
    #                             FROM dbo.inv_documento
    #                             WHERE idconcepto = '53' AND fecha BETWEEN {start_date} AND {end_date}
    #                             GROUP BY fecha, descripcion, iddocumento
    #     """
    # )
    # cursor.close()

    # print("\ndevoluciones: ---------> ", datas["devoluciones"])

    # for i in range(datas["salidas"]):
    #     datas["total"] += i.sumacantidad
    #     if "farol" in i.description.lower():
    #         datas["farol"] += i.sumacantidad
    #     else:
    #         datas["cajetillas"] += i.sumacantidad

    #     substring = re.sub(r"\s*IP\d+$", "", i.description)
    #     if substring not in datas["conceptosArray"]:
    #         datas["conceptosArray"].push(substring)
    #         it += 1
    #         j = i
    #         for j in range(datas["salidas"]):
    #             if substring == re.sub(r"\s*IP\d+$", "", j.description):
    #                 datas["sumaCantidadArray"][it] += j.sumacantidad

    return datas


getDatasSmoke("2024-05-01", "2024-05-31")
