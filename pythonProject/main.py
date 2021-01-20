# This is a sample Python script.
import mysql.connector
import pymysql

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    cnx = mysql.connector.connect(user='root', password='root_password',
                                  host='192.168.1.77',
                                  database='classicmodels')

    cur = cnx.cursor()

    cur.execute("SELECT amount FROM payments")

    # Read and print tables
    for table in [tables[0] for tables in cur.fetchall()]:
        print(table)

    cnx.close()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
