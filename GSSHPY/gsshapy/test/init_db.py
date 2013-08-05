'''
********************************************************************************
* Name: ORM Tests
* Author: Nathan Swain
* Created On: June 7, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''
import os

from sqlalchemy import create_engine
from gsshapy.orm import metadata
from gsshapy import DBSession

def delSQLiteDB(path):
    os.remove(path)
    print 'DB Deleted:', path

# Define the session
# sqlalchemy_url = 'postgresql://swainn:(|w@ter@localhost:5432/gsshapy_lite' # POSTGRESQL
# sqlalchemy_url = 'sqlite://'                                               # SQLITE_MEMEORY
# sqlalchemy_url = 'sqlite:///gsshapy_lite.db'                               # SQLITE_RELATIVE
sqlalchemy_url = 'sqlite:////Users/swainn/testing/db/gsshapy_lite.db'      # SQLITE_ABSOLUTE
delSQLiteDB('/Users/swainn/testing/db/gsshapy_lite.db')                    # DELETE_DB


engine = create_engine(sqlalchemy_url)
metadata.create_all(engine)

DBSession.configure(bind=engine)

DBSession.commit()
print 'SUCCESS: Database Initialized'