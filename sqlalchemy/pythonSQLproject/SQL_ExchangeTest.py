import os
import urllib
from sqlalchemy import create_engine
from ConfigParser import SafeConfigParser
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy.ext.automap import automap_base

dir = os.path.dirname(__file__)
serverConfigFile = os.path.join(dir, 'serverSQLtest.cnf')
# initializing the config parser
parser = SafeConfigParser()
parser.read(serverConfigFile)

# get values from the config file and
url = parser.get('client', 'url')
user = parser.get('client', 'user')
database = parser.get('client', 'database')
pwd = parser.get('client', 'password')
port = parser.get('client', 'port')

class SQL_Exchange:

    def __init__(self, nameDB, uploadsFolderPath, nameAlbum, user, pwd, url, port, database):
        self.dropbox = []
        self.nameDB = nameDB        
        self.uploadsFolderPath = uploadsFolderPath
        self.nameAlbum = nameAlbum
        self.photoSelection = []
        self.SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}:{}/{}'.format(
            user, pwd, url, port, database)
        self.tableClass = self.getTableClass(self.nameDB)

    def connect(self):
        # Open database connection using the connection string
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind = engine)
        session = Session()
        return engine, session

    def getTableClass(self, tableName):
        engine, session = self.connect()
        metadata = MetaData()
        metadata.reflect(engine)

        Base = automap_base(metadata=metadata)
        Base.prepare()
        tableClass = Base.classes[tableName]
        return tableClass
        
    def readSQL(self, debug):
        engine, session = self.connect()
        
        try:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            results = session.query(self.tableClass.dropbox_thumbL, self.tableClass.date, self.tableClass.time, self.tableClass.orientation,
                                    self.tableClass.view, self.tableClass.name, self.tableClass.file_path
                                    ).filter(self.tableClass.photoalbum == self.nameAlbum).all()
            if debug: print "database connection made"
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
        if debug: print "database connection starting"

        # Prepare SQL query to INSERT a record into the database.
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
            # Execute the SQL command
            if debug: print "database connection executed"
            # Fetch all the rows in a list of lists.
            if debug: print "database connection made"
            for a, b, c, d in results:
                self.photoSelection.append([a[1:], b, c, d])
        except Exception as e:
           if debug: print "Error: unable to fetch data" + str(e)
        session.close()  # disconnect from server

    def readImage_data(self, debug, id):
        result=list(self.readSQLcommand(sql, debug, id))
        result.append(id)
        return result

    def readSQLcommand(self, sql, debug, id):
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

    def writeSQLcommand(self, sql, debug):
        engine, session = self.connect()
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # print "MySQL", self.nameDB,"updated: ", photo.cluster,",", photo.subcluster,",", photo.smallThumbpath,",", photo.date,",", photo.DominantColor,",", photo.path
            # Commit your changes in the database
            db.commit()
        except Exception as e:
            if debug: print "Error: unable to write data to SQL: " + str(e)
        # Rollback in case there is any error
            db.rollback()
        db.close()

    def writeSQL(self, journey, debug):
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
        engine, session = self.connect()
 
        session.query(self.tableClass).filter(self.tableClass.photoalbum ==
                      self.nameAlbum).update({"pathPDF": AlbumPDFPath})
        session.commit()
        session.close()


    def writeFaceInfo(self, amountFaces, smileRatio, photoID, debug):
        engine, session = self.connect()

        session.query(self.tableClass).filter(self.tableClass.id == int(photoID)).update(
            {"numberOfFaces": amountFaces, 'smileRatio': smileRatio})
        session.commit()
        session.close()

    def writePhotoInfo(self, photo, debug):
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
    connection.readSQL(debug=True)
