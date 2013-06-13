'''
********************************************************************************
* Name: ProjectFileModel
* Author: Nathan Swain
* Created On: Mar 18, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''

__all__ = ['ProjectFile',
           'ProjectOption',
           'ProjectCard']

from sqlalchemy import ForeignKey, Column, Table
from sqlalchemy.types import Integer, String, Enum
from sqlalchemy.orm import relationship

from gsshapy.orm import DeclarativeBase, metadata

# Controlled Vocabulary List
valueTypeEnum = Enum('STRING','PATH','INTEGER','FLOAT','DATE','BOOLEAN','TIME', name='prj_card_names')

assocProject = Table('assoc_project_files_options', metadata,
    Column('projectFileID', Integer, ForeignKey('prj_project_files.id')),
    Column('projectOptionID', Integer, ForeignKey('prj_project_options.id'))
    )

class ProjectFile(DeclarativeBase):
    '''
    ProjectFile is the file ORM object that interfaces with the project files directly.
    '''
    __tablename__ = 'prj_project_files'
    
    # Primary and Foreign Keys
    id = Column(Integer, autoincrement=True, primary_key=True)
    modelID = Column(Integer, ForeignKey('model_instances.id'), nullable=False)
    mapTableFileID = Column(Integer, ForeignKey('cmt_map_table_files.id'))
    precipFileID = Column(Integer, ForeignKey('gag_precipitation_files.id'))
    
    # Value Columns
    
    # Relationship Properties
    model = relationship('ModelInstance', back_populates='projectFiles')
    scenarios = relationship('Scenario', back_populates='projectFile')
    mapTableFile = relationship('MapTableFile', back_populates='projectFile')
    precipFile = relationship('PrecipFile', back_populates='projectFile')
    projectOptions = relationship('ProjectOption', secondary=assocProject, back_populates='projectFiles')
         
    def __repr__(self):
        return '<ProjectFile>'
    
    def write(self, session, path, name):
        '''
        Project File Write Method
        '''
        # Initiate project file
        fullPath = '%s%s%s' % (path, name, '.prj')
        
        with open(fullPath, 'w') as f:
            f.write('GSSHAPROJECT\n')
        
            # Initiate write on each ProjectOption that belongs to this ProjectFile
            for opt in self.projectOptions:
                f.write(opt.write())
                
    def writeAll(self, session, path, name):
        '''
        This method orchestrates writing all the files
        '''
        
        # First write self
        self.write(session, path, name)
        
        # Write mapping table file
        self.mapTableFile.write(session, path, name)
        

     
class ProjectOption(DeclarativeBase):
    '''
    classdocs
    '''
    __tablename__ = 'prj_project_options'
    
    # Primary and Foreign Keys
    id = Column(Integer, autoincrement=True, primary_key=True)
    cardID = Column(Integer, ForeignKey('prj_cards_cv.id'), nullable=False)
    
    # Value Columns
    value = Column(String, nullable=False)
    
    # Relationship Properties
    projectFiles = relationship('ProjectFile', secondary=assocProject, back_populates='projectOptions')
    card = relationship('ProjectCard', back_populates='values')
    
    def __init__(self, value):
        '''
        Constructor
        '''
        self.value = value
        

    def __repr__(self):
        return '<ProjectOption: Value=%s>' % (self.value)
    
    def write(self):
        # Determine number of spaces between card and value for nice alignment
        numSpaces = 25 - len(self.card.name)
        
        # Handle special case of boolans
        if self.card.valueType == 'BOOLEAN':
            line = '%s\n' % (self.card.name)
        else:
            line ='%s%s%s\n' % (self.card.name,' '*numSpaces, self.value)
        return line
    
    
class ProjectCard(DeclarativeBase):
    '''
    classdocs

    '''
    __tablename__ = 'prj_cards_cv'
    
    # Primary and Foreign Keys
    id = Column(Integer, autoincrement=True, primary_key=True)
    
    # Value Columns
    name = Column(String, nullable=False)
    valueType = Column(valueTypeEnum, nullable=False)
    
    # Relationship Properties
    values = relationship('ProjectOption', back_populates='card')
    
    def __init__(self, name, valueType):
        '''
        Constructor
        '''
        self.name = name
        self.valueType = valueType
        

    def __repr__(self):
        return '<ProjectCard: Name=%s, ValueType=%s>' % (self.name, self.valueType)
