from database import *

class Assembly(Base):
    __table__ = Table("assemblies", metadata, 
        Column("latest_revision_id", Integer, ForeignKey("revisions.revision_id")),
        autoload=True)
        
    latest_revision = relationship("Revision", primaryjoin="Assembly.latest_revision_id==Revision.revision_id")
    
class Revision(Base):
    __table__ = Table("revisions", metadata, 
        Column("id", Integer, ForeignKey("assemblies.id")),
        Column("revision_id", Integer, primary_key=True),
        autoload=True)

class Config(Base):
    __table__ = Table("config", metadata, autoload=True)


