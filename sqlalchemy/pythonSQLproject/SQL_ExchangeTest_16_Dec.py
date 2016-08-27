## import required libraries
import os
from ConfigParser import SafeConfigParser
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base

## get path of the current file. append to the config file
dir = os.path.dirname(__file__)
serverConfigFile = os.path.join(dir, 'serverSQLtest.cnf')

# initializing the config parser
parser = SafeConfigParser()
parser.read(serverConfigFile)

# get values from the config file
url = parser.get('client', 'host')
user = parser.get('client', 'user')
database = parser.get('client', 'database')
pwd = parser.get('client', 'password')
port = parser.get('client', 'port')

class SQL_Exchange:
    """Class to connect to MySQL DB using SQL Alchemy ORM and perform select and update
    operations"""

    def __init__(self, nameDB, uploadsFolderPath, nameAlbum, user, pwd, url, port, database):
        """ Init method
        self.dropbox = list to insert items after a select query
        self.nameDB = name of the table        
        self.uploadsFolderPath = upload folder path
        self.nameAlbum = name of the album. Used for filtering
        self.photoSelection = list 
        self.SQLALCHEMY_DATABASE_URI = URI to connect to DB
        self.tableClass = get table class name to be used for querying 
        """
        self.dropbox = []
        self.nameDB = nameDB        
        self.uploadsFolderPath = uploadsFolderPath
        self.nameAlbum = nameAlbum
        self.photoSelection = []
        self.SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}:{}/{}'.format(
            user, pwd, url, port, database)
        self.tableClass = self.getTableClass(self.nameDB)

    def connect(self):
        """ Method to open database connection using the connection string
        engine = connection do db
        session = start a session
        """
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind = engine)
        session = Session()
        return engine, session

    def getTableClass(self, tableName):
        """Method to get the class name of a particular table """
        engine, session = self.connect()
        metadata = MetaData()
        metadata.reflect(engine)

        Base = automap_base(metadata=metadata)
        Base.prepare()
        tableClass = Base.classes[tableName]
        return tableClass
        
    def readSQL(self, debug):
        """Method to read data from a table
        debug = Used for printing out some statements
        """
        engine, session = self.connect()
        if debug: print "Connection to DB made!"
        try:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            results = session.query(self.tableClass.dropbox_thumbL, self.tableClass.date, self.tableClass.time, self.tableClass.orientation,
                                    self.tableClass.view, self.tableClass.name, self.tableClass.file_path
                                    ).filter(self.tableClass.photoalbum == self.nameAlbum).all()
            if debug: print "Data fetched using the query!"
            for dropbox_thumbL, date, time, orientation, view, name, file_path in results:
                    file_path = dropbox_thumbL
                    try:
                        date = int(date)
                    except:
                        date = 0
                    try:
                        time = int(time)
                    except:
                        time = 0
                    view = int(orientation)
                    photoID = int(view)
                    name = name
                    if debug: print file_path
                    self.dropbox.append(
                        [file_path, date, time, view, photoID, name])
        except Exception as e:
           print "Error: unable to fetch data" + str(e)

        session.close()  # disconnect from server

    def readSQL_getSelectedPhotos(self, debug, origin):
        engine, session = self.connect()
        if debug: print "Connection to DB made!"

        if origin == "dropbox":
            selectedPhotos = session.query(self.tableClass.dropbox, self.tableClass.date, self.tableClass.time
                                    ).filter(self.tableClass.photoalbum == self.nameAlbum).filter(self.tableClass.view.in_([20, 21])).all()
        elif origin == "server":
            selectedPhotos = session.query(self.tableClass.name, self.tableClass.date, self.tableClass.time, self.tableClass.pagenumber)\
                             .filter(self.tableClass.photoalbum == self.nameAlbum).filter(self.tableClass.view.in_([20, 21])).all()
        elif origin == "s3":
            selectedPhotos = session.query(self.tableClass.file_path, self.tableClass.date, self.tableClass.time, self.tableClass.pagenumber
                                    ).filter(self.tableClass.photoalbum == self.nameAlbum).filter(self.tableClass.view.in_([20, 21])).all()
        else:
            selectedPhotos = session.query(self.tableClass.file_path, self.tableClass.date, self.tableClass.time, self.tableClass.pagenumber
                                    ).filter(self.tableClass.photoalbum == self.nameAlbum).filter(self.tableClass.view.in_([20, 21])).all()
        try:
            if debug: print "Query executed"
            # Fetch all the rows in a list of lists.
            for a, b, c, d in selectedPhotos:
                self.photoSelection.append([a[1:], b, c, d])
                print [a[1:], b, c, d]
        except Exception as e:
           if debug: print "Error: unable to fetch data" + str(e)
        session.close()  # disconnect from server

    def readImage_data(self, debug, id):
        """Method to run a sql query, pass back results"""
        result=list(self.readSQLcommand(debug, id))
        result.append(id)
        return result

    def readSQLcommand(self, debug, id):
        """Method to run a sql query"""
        engine, session = self.connect()
        try:
            results=session.query(self.tableClass.dropbox_thumbL, self.tableClass.date, self.tableClass.time, self.tableClass.orientation,\
                                    self.tableClass.view, self.tableClass.name, self.tableClass.file_path\
                                    ).filter(self.tableClass.id == id).one()
            return results
        except Exception as e:
            if debug: print "Error: unable to write data to SQL: " + str(e)
        # Rollback in case there is any error
            session.rollback()
        session.close()

    def writeSQL(self, journey, debug):
        """Method to update data"""
        engine, session = self.connect()
        
        for photo in journey.imlist:
            # Prepare SQL query to UPDATE required records
            sql="UPDATE %s SET cluster = '%d', subcluster = '%d', view = '%d', blur = '%d', dominantColor = '%s', numberOfFaces = '%d', \
                            smileratio = '%d', colors  = '%s', imageScore = '%d' WHERE id = '%s'"\
                        % (self.nameDB, photo.cluster, photo.subcluster, photo.view, int(round(100 - photo.sharp)), photo.DominantColor, \
                           photo.amountFaces, photo.smileRatio, photo.ClosestColor, photo.score, photo.photoID)
            try:
                # Execute the SQL command
                session.query(self.tableClass).filter(self.tableClass.id == photo.photoID).update({"cluster": photo.cluster, "subcluster": photo.subcluster, "view": photo.view, \
                                                   "blur": int(round(100 - photo.sharp)),\
                                                   "dominantColor": photo.dominantColor, "numberOfFaces": photo.amountFaces, "smileratio": photo.smileRatio,\
                                                   "colors": photo.ClosestColor, "imageScore": photo.score})
                # Commit your changes in the database
                session.commit()
            except Exception as e:
                if debug: print "Error: unable to write data to SQL: " + str(e)
            # Rollback in case there is any error
                session.rollback()
        session.close()

    def getAlbumInfo(self, debug, origin):
        """Method to run a sql query"""
        engine, session = self.connect()
        
        try:
        # Execute the SQL command
            # Fetch all the rows in a list of lists.
            results=session.query(self.tableClass.title, self.tableClass.subtitle, self.tableClass.numberOfPages)\
                      .filter(self.tableClass.photoalbum == self.nameAlbum).all()
            if debug: print "database connection made"
            for title, subtitle, numberOfPages in results:
                self.title=title
                self.subtitle=subtitle
                if debug: print self.title, self.subtitle
                # print date, time
        except Exception as e:
           if debug: print "Error: unable to fetch data: " + str(e)
        session.close()  # disconnect from server

    def writeAlbumInfo(self, AlbumPDFPath, debug):
        """Method to update data"""
        engine, session = self.connect()
 
        session.query(self.tableClass).filter(self.tableClass.photoalbum ==
                      self.nameAlbum).update({"pathPDF": AlbumPDFPath})
        session.commit()
        session.close()


    def writeFaceInfo(self, amountFaces, smileRatio, photoID, debug):
        """Method to update data"""
        engine, session = self.connect()

        session.query(self.tableClass).filter(self.tableClass.id == int(photoID)).update(
            {"numberOfFaces": amountFaces, 'smileRatio': smileRatio})
        session.commit()
        session.close()

    def writePhotoInfo(self, photo, debug):
        """Method to update data"""
        engine, session = self.connect()
        
        session.query(self.tableClass).filter(self.tableClass.id == int(photoID)).update({"numberOfFaces": photo.amountFaces, 'smileRatio': photo.smileRatio,
                                                                                  'urban': photo.scene['urban'], 'people': photo.scene['people'],
                                                                                  'animals': photo.scene['animals'], 'nature': photo.scene['nature'],
                                                                                  'faceplusplus': str(photo.faceppResult)})
        session.commit()
        session.close()

if __name__ == "__main__":
    uploadsFolderPath="</add/a/path/here>"
    connection=SQL_Exchange(
    "allimages",
    uploadsFolderPath,
     "rMUVoIeryPXB65mxHXHa", user, pwd, url, port, database)
    #connection.readSQL(debug=True)
    #connection.readImage_data(True, 1943)
    #connection.readSQL_getSelectedPhotos(True, 'server')
    #connection.getAlbumInfo(True, 'aa')
    #connection.writeFaceInfo(100,	100,	1944, True)
