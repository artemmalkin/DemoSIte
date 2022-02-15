class Configuration(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:postgres@localhost/users?client_encoding=utf8'
    SECRET_KEY = 'SAD12DJJ34KDds#sdsda'
