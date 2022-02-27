# DemoSIte
1) Install the requirements in a virtual environment `pip3 install -r requirements.txt`
2) If you need then edit string SQLALCHEMY_DATABASE_URI (user, password, port) in the file **config.py**
3) Log in PostgreSQL: `sudo -u user_name psql`
4) After authorization in your psql, run this command `CREATE DATABASE demosite;`
5) Run file **run.py**: `python run.py`
6) Complete this commands in python console `from app import db` & `db.create_all()`
7) Restart **run.py**
8) Visit **_**http://localhost:5000**_**