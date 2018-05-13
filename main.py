try:
    import sys
    import feedparser
    import configparser
    from qbittorrent import Client
    import pendulum                                         #Datetime conversions
    import logging

except ImportError:
    print("Needed Modules are not installed.\n")
    print("use:\n")
    print("pip install feedparser\n")
    print("pip install configparser\n")
    print("pip install qbittorrent\n")
    print("pip install pendulum\n")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
loghandler = logging.FileHandler('ReasonSS.log')
logger.addHandler(loghandler)

def mid(s, offset, amount):
    return s[offset-1:offset+amount-1]

def left(s, amount):
    return s[:amount]

wanted = list()
completed = list()
completedsave = list()
countWanted = int()
countCompleted = int()
Downloadlist = list()
newdownloads = int()
logger.info('---------------------------------------------------------------------------------------')

today=pendulum.now()
today.format('DD-MM-YYY HH:mm')
logger.info('Run at: %s', today)

config = configparser.ConfigParser()
if len(config.read('config.txt'))==0:                           #if config file isn't found, create it
    cfgfile = open("config.txt", 'w')
    config.add_section('Default')
    config.add_section('Rss')
    config.add_section('Torrent')
    config.set('Default','wanted', 'wanted.txt')                #Every Searchterm in a line in the wanted file
    config.set('Default','completed', 'completed.txt')          #Torrents which have been sent to qBittorrent
    config.set('Default', 'purge', '30')                        #How old downloads should be monitored? (in days)
    config.set('Rss','rss', 'http://www.example.org/feed')      #Feed Adress
    config.set('Torrent','qbclient', 'http://127.0.0.1:8080')   #WEB-Access for qBittorrent must be available
    config.set('Torrent','category','')                         #no category as standard
    config.set('Torrent','login','admin')                       #Login to qBittorrent Client
    config.set('Torrent','password','admin')                    #Password to qBittorrent Client
    config.set('Torrent','download','no')                       #Start Downloads immediately (yes/no)

    config.write(cfgfile)
    cfgfile.close()

try:
    qb=Client(config['Torrent']['qbclient'])
    qb.login(config['Torrent']['login'], config['Torrent']['password'])
    logger.info("Connection to qBittorrent established")
except:
    print("There was an error communcation with qBittorrent!")
    logger.critical("Connection to qBittorrent failed")
    sys._exit(1)
    
config.read('config.txt')                                       #read config
purge=int(config['Default']['purge'])
fileWanted=config['Default']['wanted']                          #read the searchterms for the RSS-Filter
category=config['Torrent']['category']
startdownload=config['Torrent']['download']

logger.info('Purge: %s', purge)
logger.info('Wanted List: %s', fileWanted)
logger.info('Category: %s', category)
logger.info('Start Download: %s', startdownload)

with open(fileWanted) as foWanted:
    for line in foWanted:
        wanted.append(line.rstrip())
        countWanted=countWanted+1
foWanted.close()
logger.info("Wanted: %i", countWanted)

fileCompleted=config['Default']['completed']
with open(fileCompleted) as foCompleted:
    for line in foCompleted:
        sep=line.rstrip().find("|")
        link=mid(line.rstrip(),sep+2, len(line.rstrip())-sep+2)
        completed.append(link)
        date=pendulum.parse(left(line.rstrip(), sep))
        today=pendulum.now()
        purgedate=today.subtract(days=purge)
        if date>purgedate:
            completedsave.append(line.rstrip())
        else:
            logger.info("Old Entry:", line.rstrip())
        countCompleted=countCompleted+1

logger.info("Completed: %s", countCompleted)

try:
    d = feedparser.parse(config['Rss']['rss'])
except:
    logger.debug("Feed %s", config['Rss']['rss'], " couldn't be loaded.")
    sys.exit(1)

#print(qb.torrents(category=config['Torrent']['category']))

for post in d.entries:                                          #check all items from the RSS-Feed
    for i in wanted:                                            #check all searchtermins in wanted
        if i in str.lower(post.title):
            download=2
            if len(completed) > 0:
                for l in completed:                             #check if the file hasn't been already downloaded
                    if l not in post.link:
                        download=1
                    else:
                        download=0
                        break
            else:
                download=1
            if download==1:
                try:
                    qb.download_from_link(post.link,category=category)
                    if startdownload=="yes":
                        qb.resume_all()
                    completedsave.append(post.published + "|" + post.link)
                    tmpLogger="Added: " + left(post.title,40) + "..."
                    logger.info(tmpLogger)
                except:
                    logger.critical("Download could not be added to qBittorrent\n")


with open(fileCompleted, "w") as foCompleted:
    for i in completedsave:
        foCompleted.writelines(i + "\n")
foCompleted.close()
