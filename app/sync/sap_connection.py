import pymssql
from contextlib import contextmanager 

from app.core.config import settings 

@contextmanager 
def get_sap_connection():
    conn = pymssql.connect(
        server=settings.SAP_DB_HOST,
        port=str(settings.SAP_DB_PORT),
        user=settings.SAP_DB_USER,
        password=settings.SAP_DB_PASSWORD,
        database=settings.SAP_DB_NAME
    )
    
    try:
        yield conn 
    finally:
        conn.close()