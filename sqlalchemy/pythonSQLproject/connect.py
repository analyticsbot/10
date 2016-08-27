from sqlalchemy import create_engine
from ConfigParser import SafeConfigParser
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import table
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy.ext.automap import automap_base

engine = create_engine('mysql://root:pass123@127.0.0.1:3306/newschema')
print engine.table_names()

name = 'zBspNU9LTkXRwk6GIWUGIG1gw3ea2M7HbjZw5r6ag127lzHx5iolx8D1ZYuT.jpg'

metadata = MetaData()
metadata.reflect(engine)

Base = automap_base(metadata=metadata)
Base.prepare()
allimages = Base.classes['allimages']

Session = sessionmaker(bind = engine)
session = Session()
results = session.query((allimages)).filter(allimages.name == name).all()

for row in results:
    print row.name

