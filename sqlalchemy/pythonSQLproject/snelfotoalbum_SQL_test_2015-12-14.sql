# ************************************************************
# Sequel Pro SQL dump
# Version 4499
#
# http://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# Host: 127.0.0.1 (MySQL 5.5.42)
# Database: snelfotoalbum_SQL_test
# Generation Time: 2015-12-14 15:43:40 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table _orders
# ------------------------------------------------------------

DROP TABLE IF EXISTS `_orders`;

CREATE TABLE `_orders` (
  `photoalbum` varchar(20) NOT NULL DEFAULT '',
  `title` varchar(40) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table algorithmconfiguration
# ------------------------------------------------------------

DROP TABLE IF EXISTS `algorithmconfiguration`;

CREATE TABLE `algorithmconfiguration` (
  `IDconfiguration` int(11) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `numberOfSelected` varchar(45) DEFAULT NULL,
  `selectionTreshold` varchar(45) DEFAULT NULL,
  `mode` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`IDconfiguration`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table allimages
# ------------------------------------------------------------

DROP TABLE IF EXISTS `allimages`;

CREATE TABLE `allimages` (
  `name` varchar(100) NOT NULL,
  `pagenumber` varchar(1) NOT NULL,
  `date` varchar(11) NOT NULL DEFAULT '',
  `time` varchar(10) NOT NULL DEFAULT '',
  `cluster` int(11) NOT NULL,
  `subcluster` int(11) NOT NULL,
  `view` int(2) NOT NULL,
  `blur` int(1) NOT NULL,
  `dropbox_thumbL` longblob NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `execution_time` varchar(30) DEFAULT NULL,
  `lat` varchar(255) NOT NULL,
  `long1` varchar(255) NOT NULL,
  `dominantColor` varchar(255) NOT NULL,
  `photoalbum` varchar(20) NOT NULL DEFAULT '',
  `orientation` int(1) NOT NULL,
  `portrait` int(200) DEFAULT NULL,
  `pagetype` varchar(20) NOT NULL DEFAULT 'page',
  `numberOfFaces` int(11) DEFAULT NULL,
  `smileRatio` double DEFAULT NULL,
  `imageScore` double DEFAULT NULL,
  `colors` varchar(200) DEFAULT NULL,
  `ruleOfThirds` varchar(45) DEFAULT NULL,
  `exposureLevel` int(11) DEFAULT NULL,
  `openEyesRatio` double DEFAULT NULL,
  `symmetry` double DEFAULT NULL,
  `HOG` varchar(100) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `urban` float DEFAULT NULL,
  `people` float DEFAULT NULL,
  `animals` float DEFAULT NULL,
  `nature` float DEFAULT NULL,
  `smiles` int(11) DEFAULT NULL,
  `faceplusplus` varchar(5000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1949 DEFAULT CHARSET=latin1;

LOCK TABLES `allimages` WRITE;
/*!40000 ALTER TABLE `allimages` DISABLE KEYS */;

INSERT INTO `allimages` (`name`, `pagenumber`, `date`, `time`, `cluster`, `subcluster`, `view`, `blur`, `dropbox_thumbL`, `file_path`, `execution_time`, `lat`, `long1`, `dominantColor`, `photoalbum`, `orientation`, `portrait`, `pagetype`, `numberOfFaces`, `smileRatio`, `imageScore`, `colors`, `ruleOfThirds`, `exposureLevel`, `openEyesRatio`, `symmetry`, `HOG`, `id`, `urban`, `people`, `animals`, `nature`, `smiles`, `faceplusplus`)
VALUES
	('zBspNU9LTkXRwk6GIWUGIG1gw3ea2M7HbjZw5r6ag127lzHx5iolx8D1ZYuT.jpg','','20131017','161423',0,0,21,0,X'75706C6F6164732F7468756D62732F7468756D622D7A4273704E55394C546B5852776B3647495755474947316777336561324D3748626A5A7735723661673132376C7A487835696F6C783844315A5975542E6A7067','/Users/martijnjansen/Documents/Programming/MemoryAtlas/Snelfotoalbum_Application/public/uploads/zBspNU9LTkXRwk6GIWUGIG1gw3ea2M7HbjZw5r6ag127lzHx5iolx8D1ZYuT.jpg',NULL,'','','','rMUVoIeryPXB65mxHXHa',1,0,'page',0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1943,0.2,0.67,0.04,0.09,NULL,NULL),
	('6JBVzZN0d3G2GB6hcsXKyb6fLtPJ0QTnez5SNv3ywRqni7c5LS5owfx5xmXg.JPG','','20071225','121855',0,0,21,0,X'75706C6F6164732F7468756D62732F7468756D622D364A42567A5A4E3064334732474236686373584B796236664C74504A3051546E657A35534E7633797752716E693763354C53356F77667835786D58672E4A5047','/Users/martijnjansen/Documents/Programming/MemoryAtlas/Snelfotoalbum_Application/public/uploads/6JBVzZN0d3G2GB6hcsXKyb6fLtPJ0QTnez5SNv3ywRqni7c5LS5owfx5xmXg.JPG',NULL,'','','','rMUVoIeryPXB65mxHXHa',1,0,'page',1,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1944,0.01,0.9,0.1,0,NULL,NULL),
	('1uDaID1SagPk617eOF2D8AvqRB7GVs6bskJF2oZS0kGOoT3edrQfI6qGO5A5.jpg','','20121207','072404',0,0,21,0,X'75706C6F6164732F7468756D62732F7468756D622D31754461494431536167506B363137654F463244384176715242374756733662736B4A46326F5A53306B474F6F54336564725166493671474F3541352E6A7067','/Users/martijnjansen/Documents/Programming/MemoryAtlas/Snelfotoalbum_Application/public/uploads/1uDaID1SagPk617eOF2D8AvqRB7GVs6bskJF2oZS0kGOoT3edrQfI6qGO5A5.jpg',NULL,'','','','rMUVoIeryPXB65mxHXHa',1,0,'page',0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1945,0.06,0.69,0.15,0.1,NULL,NULL),
	('V7GACUpnAerUZTFE78oHdsJVzZ8ZaETs4ngdCl8eobD4nuul2pEQOOokrjUY.JPG','','20131016','145110',0,0,21,0,X'75706C6F6164732F7468756D62732F7468756D622D563747414355706E416572555A54464537386F4864734A567A5A385A61455473346E6764436C38656F6244346E75756C327045514F4F6F6B726A55592E4A5047','/Users/martijnjansen/Documents/Programming/MemoryAtlas/Snelfotoalbum_Application/public/uploads/V7GACUpnAerUZTFE78oHdsJVzZ8ZaETs4ngdCl8eobD4nuul2pEQOOokrjUY.JPG',NULL,'','','','rMUVoIeryPXB65mxHXHa',1,0,'page',1,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1946,0.08,0.91,0,0,NULL,NULL),
	('cover_back','b','','',0,0,20,0,X'75706C6F6164732F7468756D62732F7468756D622D7A4273704E55394C546B5852776B3647495755474947316777336561324D3748626A5A7735723661673132376C7A487835696F6C783844315A5975542E6A7067','/Users/martijnjansen/Documents/Programming/MemoryAtlas/Snelfotoalbum_Application/public/uploads/zBspNU9LTkXRwk6GIWUGIG1gw3ea2M7HbjZw5r6ag127lzHx5iolx8D1ZYuT.jpg',NULL,'','','','rMUVoIeryPXB65mxHXHa',0,0,'cover',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1947,NULL,NULL,NULL,NULL,NULL,NULL),
	('cover_front','f','','',0,0,20,0,X'75706C6F6164732F7468756D62732F7468756D622D31754461494431536167506B363137654F463244384176715242374756733662736B4A46326F5A53306B474F6F54336564725166493671474F3541352E6A7067','/Users/martijnjansen/Documents/Programming/MemoryAtlas/Snelfotoalbum_Application/public/uploads/1uDaID1SagPk617eOF2D8AvqRB7GVs6bskJF2oZS0kGOoT3edrQfI6qGO5A5.jpg',NULL,'','','','rMUVoIeryPXB65mxHXHa',0,0,'cover',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1948,NULL,NULL,NULL,NULL,NULL,NULL);

/*!40000 ALTER TABLE `allimages` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table discount
# ------------------------------------------------------------

DROP TABLE IF EXISTS `discount`;

CREATE TABLE `discount` (
  `IDdiscount` int(11) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `startTime` timestamp NULL DEFAULT NULL,
  `endTime` timestamp NULL DEFAULT NULL,
  `discountRate` varchar(45) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`IDdiscount`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table eventlog
# ------------------------------------------------------------

DROP TABLE IF EXISTS `eventlog`;

CREATE TABLE `eventlog` (
  `IDevent` int(11) NOT NULL,
  `time` timestamp NULL DEFAULT NULL,
  `eventType` varchar(45) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `message` varchar(45) DEFAULT NULL,
  `eventSeverity` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`IDevent`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table migrations
# ------------------------------------------------------------

DROP TABLE IF EXISTS `migrations`;

CREATE TABLE `migrations` (
  `migration` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `batch` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;



# Dump of table orders
# ------------------------------------------------------------

DROP TABLE IF EXISTS `orders`;

CREATE TABLE `orders` (
  `IDorder` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(40) DEFAULT NULL,
  `pathPDF` varchar(150) DEFAULT NULL,
  `pathSpine` varchar(150) DEFAULT NULL,
  `peechoOrderID` varchar(45) DEFAULT NULL,
  `peechoState` varchar(45) DEFAULT NULL,
  `peechoProduct` varchar(45) DEFAULT NULL,
  `peechoPrice` varchar(45) DEFAULT NULL,
  `customerPrice` varchar(45) DEFAULT NULL,
  `deliveryAddressStreet` varchar(70) DEFAULT NULL,
  `deliveryAddressNumber` varchar(10) DEFAULT NULL,
  `deliveryAddressCity` varchar(45) DEFAULT NULL,
  `deliveryAddressCountry` varchar(45) DEFAULT NULL,
  `deliveryAddressPostcode` varchar(45) DEFAULT NULL,
  `numberOfPhotos` int(11) DEFAULT NULL,
  `numberOfPages` int(11) DEFAULT NULL,
  `photoalbum` varchar(20) NOT NULL,
  `subtitle` varchar(20) NOT NULL,
  PRIMARY KEY (`IDorder`),
  UNIQUE KEY `photoalbum` (`photoalbum`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;

INSERT INTO `orders` (`IDorder`, `title`, `pathPDF`, `pathSpine`, `peechoOrderID`, `peechoState`, `peechoProduct`, `peechoPrice`, `customerPrice`, `deliveryAddressStreet`, `deliveryAddressNumber`, `deliveryAddressCity`, `deliveryAddressCountry`, `deliveryAddressPostcode`, `numberOfPhotos`, `numberOfPages`, `photoalbum`, `subtitle`)
VALUES
	(5,'blabl',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'rMUVoIeryPXB65mxHXHa','ablal');

/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table user
# ------------------------------------------------------------

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `IDuser` int(11) NOT NULL,
  `username` varchar(45) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `role` varchar(45) DEFAULT NULL,
  `firstName` varchar(45) DEFAULT NULL,
  `lastName` varchar(45) DEFAULT NULL,
  `registeredTime` timestamp NULL DEFAULT NULL,
  `lastVisit` timestamp NULL DEFAULT NULL,
  `lastIP` varchar(45) DEFAULT NULL,
  `country` varchar(45) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `postcode` varchar(45) DEFAULT NULL,
  `accountStatus` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`IDuser`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table visitors
# ------------------------------------------------------------

DROP TABLE IF EXISTS `visitors`;

CREATE TABLE `visitors` (
  `photoalbum` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `visitors` WRITE;
/*!40000 ALTER TABLE `visitors` DISABLE KEYS */;

INSERT INTO `visitors` (`photoalbum`)
VALUES
	('1xXNidOHk9ATR0DTTlIr'),
	('09qvlfU7fCs8R23uZr0L'),
	('jiCuOeXdXNIbRUnvZJf0'),
	('n0ASAEHGiaSCjSfA9Pnj'),
	('5KjiXKVAuzw2xFEPVl5N'),
	('l9O8hvdrZe674iEXKp9v'),
	('9aXoYCZU7WwvIYCBSWSl'),
	('VNvBXfcNwLtiEmhN6YXh'),
	('rMUVoIeryPXB65mxHXHa'),
	('7kayvKaGwOTqVBLlXniJ'),
	('0thpL6EAHWvRC7Da0EgB');

/*!40000 ALTER TABLE `visitors` ENABLE KEYS */;
UNLOCK TABLES;



/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
