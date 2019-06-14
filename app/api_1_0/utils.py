import re
import pymysql
#
def table_exists(cursor,table_name):
    sql = "show tables;"
    cursor.execute(sql)
    #print(cursor.fetchall())
    tables=[cursor.fetchall()]      #数据库中所有的表名称组成的列表
    #print(str(tables))
    table_list = re.findall('(\'.*?\')',str(tables))
    table_list = [re.sub("'",'',each) for each in table_list]
    #print(table_list)
    if table_name in table_list:
        return True
    else:
        return False

def connect_to_mysql():
    con=pymysql.connect(host='localhost',port=3306,user='root',password='woaini123..',database="jxc",charset='utf8')
    return con





