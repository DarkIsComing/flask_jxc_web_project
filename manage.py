from app import create_app, db
import pymysql  
from app.models import *

app=create_app()


if __name__=='__main__':
    app.run(debug=True,use_reloader=False)