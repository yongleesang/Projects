# This is a sample Python script.
from datetime import date
from datetime import datetime

import bs4
import requests
import urllib.request, json
import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'maryland_covid'
url_array = []


# connects to the database
def database_connect():
    mydb = mysql.connector.connect(
        host="192.168.1.77",
        user="root",
        password="root_password"
    )
    return mydb

# create database if it doesnt exist
def create_database():
    mydb = database_connect()
    cursor = mydb.cursor()

    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

    cursor.close()
    mydb.close()

# create tables, it is suppose to get the table name from the page, but issue with page ids having dashes
# and names being really long, so not good for table names
def create_tables(table_name):
    mydb = database_connect()
    cursor = mydb.cursor()
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            mydb.database = DB_NAME
        else:
            print(err)
            exit(1)

    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute("CREATE TABLE `{}` (  `obj_id` int(11) NOT NULL,  `date` date NOT NULL, "
                       "`death` int(11) NOT NULL, PRIMARY KEY (`obj_id`)) ENGINE=InnoDB".format(table_name))

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

    cursor.close()
    mydb.close()

# parsing through the json file and getting what i need and inserting it in the database
def add_data_to_database():
    mydb = database_connect()
    cursor = mydb.cursor()

    length = len(url_array)
    for i in range(1):
        print(url_array[i])
        with urllib.request.urlopen(url_array[i]) as url:
            page_id_array = []
            page_name_array = []
            obj_id_array = []
            obj_time_array = []
            obj_death_num_array = []

            add_all_data = []

            data = json.loads(url.read().decode())
            # print(data)
            # print(data['meta'])
            # print(data['meta']['view']['id'])
            #page_id_array.append(data['meta']['view']['id'])
            #page_name_array.append(data['meta']['view']['name'])
            #id doesnt work because it has a -, it creates but cant add any data
            create_tables('probable_death')
            # print(data['data'])
            data_length = len(data['data'])
            # print(data_length)
            for j in range(data_length):
                obj_id_array.append(data['data'][j][8])
                date_time_str = data['data'][j][9].replace('T', ' ')
                date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                obj_date = date
                obj_time_array.append(data['data'][j][9])
                obj_death_num_array.append(data['data'][j][10])

                add_all_data.append((data['data'][j][8], date_time_obj, data['data'][j][10]))

            print(add_all_data)
            try:
                cursor.execute("USE {}".format(DB_NAME))
            except mysql.connector.Error as err:
                print("Database {} does not exists.".format(DB_NAME))
                if err.errno == errorcode.ER_BAD_DB_ERROR:
                    create_database(cursor)
                    print("Database {} created successfully.".format(DB_NAME))
                    mydb.database = DB_NAME
                else:
                    print(err)
                    exit(1)

            stmt = "INSERT IGNORE INTO probable_death (obj_id, date, death) VALUES (%s, %s, %s)"
            cursor.executemany(stmt, add_all_data)

            mydb.commit()

    cursor.close()
    mydb.close()

# using beautifulsoup(bs4) to parse through the html and getting the links for each page, and bs4 again the pages
# to get the json urls
def get_json_url_using_url():
    url = "https://healthdata.gov/search/field_resources%253Afield_format/json-56/type/dataset?query=covid%20state%20of%20maryland&sort_by=changed&sort_order=DESC"
    url_health = "https://healthdata.gov{}"
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    for i in soup.find_all('h2', attrs={'class': 'node-title'}):
        link = None
        if i.find('a'):
            link = i.find('a').get('href')
            response = requests.get(url_health.format(link))
            soupin = bs4.BeautifulSoup(response.text, 'html.parser')
            json_url = soupin.find(class_='field-name-field-identifier').get_text()
            url_array.append(json_url + "{}".format("/rows.json"))

# testing adding data
def add_data_test():
    print("start add_data_test")
    mydb = database_connect()
    cursor = mydb.cursor()
    test_table = 'probable_death'

    test_data = [
        ('1', date(2005, 2, 12), '1'),
        ('2', date(2005, 2, 12), '1'),
        ('3', date(2005, 2, 12), '1'),
    ]

    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            mydb.database = DB_NAME
        else:
            print(err)
            exit(1)

    stmt = "INSERT INTO probable_death (obj_id, date, death) VALUES (%s, %s, %s)"
    cursor.executemany(stmt, test_data)

    mydb.commit()

    cursor.close()
    mydb.close()
    print("end add_data_test")

# getting the data out from the database and doing simple math with the numbers
def get_data_from_database():
    mydb = database_connect()
    cursor = mydb.cursor()

    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            mydb.database = DB_NAME
        else:
            print(err)
            exit(1)

    cursor.execute("SELECT * FROM probable_death")

    myresult = cursor.fetchall()

    sum_death = 0
    row_counter = 0
    for x in myresult:
        sum_death += x[2]
        row_counter += 1

    print('sum of all death' + str(sum_death))
    print('avg death per day ' + str(sum_death/row_counter))

    cursor.close()
    mydb.close()


if __name__ == '__main__':
    create_database()
    get_json_url_using_url()
    # add_data_test()
    add_data_to_database()
    get_data_from_database()
