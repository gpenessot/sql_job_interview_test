
import configparser
from sqlalchemy import MetaData
from sqlalchemy_schemadisplay import create_schema_graph

config = configparser.ConfigParser()
config.read('./config.cfg')

HOST_EXT = config['POSTGRES']['host_name_ext']
DATABASE_NAME = config['POSTGRES']['database']
HOST_PORT = config['POSTGRES']['port']
USERNAME = config['POSTGRES']['username']
PASSWORD = config['POSTGRES']['password']

## Draw from database
graph = create_schema_graph(metadata=MetaData(f"postgresql://{USERNAME}:{PASSWORD}@{HOST_EXT}/{DATABASE_NAME}"),
    show_datatypes=False, # The image would get nasty big if we'd show the datatypes
    show_indexes=False, # ditto for indexes
    rankdir='LR', # From left to right (instead of top to bottom)
    concentrate=False # Don't try to join the relation lines together
)
graph.write_png('dbschema.png') # write out the file