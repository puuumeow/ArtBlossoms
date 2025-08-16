import pymysql
from pymysql.cursors import DictCursor
import pymysql.cursors

def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        db='ArtBlossoms',
        cursorclass=pymysql.cursors.DictCursor
    )
cursorclass=pymysql.cursors.DictCursor