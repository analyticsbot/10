import MySQLdb
import os

dir = os.path.dirname(__file__)
serverConfigFile = os.path.join(dir, 'serverSQLtest.cnf')

class SQL_Exchange:
 
    def __init__(self, nameDB, uploadsFolderPath, nameAlbum):
        self.dropbox = []       
        self.nameDB = nameDB
        self.uploadsFolderPath = uploadsFolderPath
        self.nameAlbum = nameAlbum 
        self.photoSelection = []
    
    def connect(self):        
        # Open database connection
        db = MySQLdb.connect(read_default_file=serverConfigFile)        
        return db        
        
    def readSQL(self, debug):
        db = self.connect()
        cursor = db.cursor()
        # Prepare SQL query to INSERT a record into the database.
        sql = "SELECT dropbox_thumbL, date, time, orientation, view, name, file_path FROM %s WHERE photoalbum = '%s'" % (self.nameDB, self.nameAlbum)  #\ WHERE INCOME > '%d'" % (1000)
        
        try:
        # Execute the SQL command
            cursor.execute(sql)
            # Fetch all the rows in a list of lists.
            results = cursor.fetchall()
            if debug: print "database connection made"
            for row in results:                
                    #temp_list = str(row[0]).split("/")
                    #file_path = "/"+temp_list[4]+"/"+temp_list[5]+"/"+temp_list[6]+"/"+temp_list[7] # remove the ../../../../
                    file_path = row[0]
                    try:
                        date = int(row[1])
                    except:
                        date = 0
                    try:
                        time = int(row[2])
                    except:
                        time = 0
                    view = int(row[3])
                    photoID = int(row[4])
                    name = row[5]
                    if debug: print file_path
                    self.dropbox.append([file_path, date, time, view, photoID, name])
        except Exception as e:
           print "Error: unable to fetch data"+str(e)
        #print self.dropbox
        db.close() #disconnect from server
        
    def readSQL_getSelectedPhotos(self, debug, origin):
        db = self.connect()
        cursor = db.cursor()
        # Prepare SQL query to INSERT a record into the database.
        if origin == "dropbox":
            selectedPhotos = "SELECT dropbox, date, time, FROM %s WHERE photoalbum = '%s' AND (view = 20 OR view = 21)" % (self.nameDB, self.nameAlbum)
        elif origin == "server":
            selectedPhotos = "SELECT name, date, time, pagenumber FROM %s WHERE photoalbum = '%s' AND (view = 20 OR view = 21)" % (self.nameDB, self.nameAlbum)
        elif origin == "s3":
            selectedPhotos = "SELECT file_path, date, time, pagenumber FROM %s WHERE photoalbum = '%s' AND (view = 20 OR view = 21)" % (self.nameDB, self.nameAlbum)            
        else:
            selectedPhotos = "SELECT file_path, date, time, pagenumber FROM %s WHERE photoalbum = '%s' AND (view = 20 OR view = 21)" % (self.nameDB, self.nameAlbum)            
        try:
        # Execute the SQL command
            if debug: print "database connection starting"
            cursor.execute(selectedPhotos)
            if debug: print "database connection executed"
            # Fetch all the rows in a list of lists.
            results = cursor.fetchall()
            if debug: print "database connection made"
            for row in results:
                self.photoSelection.append([row[0][1:],row[1],row[2],row[3]])
        except Exception as e:
           if debug: print "Error: unable to fetch data"+str(e)
        db.close() #disconnect from server

    def readImage_data(self, debug, id):
        sql =  "SELECT dropbox_thumbL, date, time, orientation, view, name, file_path FROM %s WHERE id = '%d'" % (self.nameDB, id)
        result = list(self.readSQLcommand(sql, debug))  
        result.append(id)
        return result

    def readSQLcommand(self, sql, debug):
        db = self.connect()
        cursor = db.cursor()        
        try:
            cursor.execute(sql)
            results = cursor.fetchone()            
            return results                 
        except Exception as e:
            if debug: print "Error: unable to write data to SQL: "+str(e)
        # Rollback in case there is any error            
            db.rollback()
        db.close()

    def writeSQLcommand(self, sql, debug):
        db = self.connect()
        cursor = db.cursor()        
        try:
            # Execute the SQL command
            cursor.execute(sql)
            #print "MySQL", self.nameDB,"updated: ", photo.cluster,",", photo.subcluster,",", photo.smallThumbpath,",", photo.date,",", photo.DominantColor,",", photo.path
            # Commit your changes in the database
            db.commit()                   
        except Exception as e:
            if debug: print "Error: unable to write data to SQL: "+str(e)
        # Rollback in case there is any error            
            db.rollback()
        db.close()
        
    def writeSQL(self, journey, debug):
        db = self.connect()
        cursor = db.cursor()        
        for photo in journey.imlist:
            # Prepare SQL query to UPDATE required records
            sql = "UPDATE %s SET cluster = '%d', subcluster = '%d', view = '%d', blur = '%d', dominantColor = '%s', numberOfFaces = '%d', smileratio = '%d', colors  = '%s', imageScore = '%d' WHERE id = '%s'"\
                        % (self.nameDB, photo.cluster, photo.subcluster, photo.view, int(round(100 - photo.sharp)), photo.DominantColor, photo.amountFaces, photo.smileRatio, photo.ClosestColor, photo.score, photo.photoID)
            try:
                # Execute the SQL command
                cursor.execute(sql)
                # Commit your changes in the database
                db.commit()                   
            except Exception as e:
                if debug: print "Error: unable to write data to SQL: "+str(e)
            # Rollback in case there is any error            
                db.rollback()
        db.close()

    def getAlbumInfo(self, debug, origin):
        db = self.connect()
        cursor = db.cursor()
        sql = "SELECT title, subtitle, numberOfPages FROM %s WHERE photoalbum = '%s'" % (self.nameDB, self.nameAlbum)
        try:
        # Execute the SQL command
            cursor.execute(sql)
            # Fetch all the rows in a list of lists.
            results = cursor.fetchall()            
            if debug: print "database connection made"
            for row in results:
                self.title = str(row[0])
                self.subtitle = str(row[1])
                if debug: print self.title, self.subtitle
                #print date, time
        except Exception as e:
           if debug: print "Error: unable to fetch data: "+str(e)
        db.close() #disconnect from server

    def writeAlbumInfo(self, AlbumPDFPath, debug):
        sql =  "UPDATE %s SET pathPDF = '%s' WHERE photoalbum = '%s'" % (self.nameDB, AlbumPDFPath, self.nameAlbum)
        self.writeSQLcommand(sql, debug)    

    def writeFaceInfo(self, amountFaces, smileRatio, photoID, debug):
        sql =  "UPDATE %s SET numberOfFaces = '%s', smileRatio = '%1.2f'  WHERE id = '%d'" % (self.nameDB, amountFaces, smileRatio, int(photoID))
        self.writeSQLcommand(sql, debug)        

    def writePhotoInfo(self, photo, debug):
        sql =  "UPDATE %s SET numberOfFaces = '%s', smileRatio = '%1.2f', urban =  '%1.2f', people = '%1.2f', animals = '%1.2f', nature = '%1.2f', faceplusplus = '%s' WHERE id = '%d'" % (self.nameDB, photo.amountFaces, photo.smileRatio, photo.scene['urban'], photo.scene['people'], photo.scene['animals'], photo.scene['nature'], str(photo.faceppResult), int(photo.photoID))
        self.writeSQLcommand(sql, debug) 

if __name__=="__main__":
    uploadsFolderPath = "</add/a/path/here>"
    connection = SQL_Exchange("allimages", uploadsFolderPath, "rMUVoIeryPXB65mxHXHa")
    connection.connect()
    connection.readSQL(debug=True)
    
