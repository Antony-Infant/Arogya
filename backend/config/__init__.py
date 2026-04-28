import pymysql
pymysql.version_info = (2, 2, 4, 'final', 0)
pymysql.install_as_MySQLdb()

from .celery_app import app as celery_app
__all__ = ('celery_app',)
