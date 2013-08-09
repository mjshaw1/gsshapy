'''
********************************************************************************
* Name: Testing Script
* Author: Nathan Swain
* Created On: July 10, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''
import time
from gsshapy.orm import ProjectFile
from gsshapy.lib import db_tools as dbt

# Read Parameters
readDirectory='/Users/swainn/testing/test models/ContaminentTransport'
projectFile='contam.prj'

# Write Parameters
writeDirectory='/Users/swainn/testing/test models/ContaminentTransport/write'
newName='test_contam'



# Reset Database
dbt.del_sqlite_db('/Users/swainn/testing/db/gsshapy_lite.db')
sqlalchemy_url = dbt.init_sqlite_db('/Users/swainn/testing/db/gsshapy_lite.db', time=True)

# Initialize the Session
readSession = dbt.create_session(sqlalchemy_url)
writeSession = dbt.create_session(sqlalchemy_url)

# Create an empty Project File Object
project = ProjectFile(directory=readDirectory, filename=projectFile, session=readSession)

# Start timer
start = time.time()

# Invoke read command on Project File Object
project.readProject()

# Report Read Time
print 'READ TIME:', time.time()-start


# Query Database to Retrieve Project File
project1 = writeSession.query(ProjectFile).filter(ProjectFile.id == 1).one()

# Reset Timer
start = time.time()
                       
# Invoke write command on Project File Query Object
project1.writeProject(session=writeSession, directory=writeDirectory, newName=newName)

# Report Write Time
print 'WRITE TIME:', time.time() - start
