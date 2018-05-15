import sys
try:
    import feedparser
except ImportError:
    print("Needed module 'feedparser' is not installed.")
    sys.exit(1)
try:
    import configparser
except ImportError:
    print("Needed module 'configparser' is not installed.")
    sys.exit(1)
try:
    from qbittorrent import Client
except ImportError:
    print("Needed module 'qBittorrent' is not installed.")
    sys.exit(1)
try:
    import pendulum
except ImportError:
    print("Needed module 'pendulum' is not installed.")
    sys.exit(1)
try:
    import logging
except ImportError:
    print("Needed module 'logging' is not installed.")
    sys.exit(1)
try:
    import apprise                                      #Notification System
except ImportError:
    print("Needed module 'apprise' is not installed.")
    sys.exit(1)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
loghandler = logging.FileHandler('ReasonSS.log')
logger.addHandler(loghandler)

def mid(s, offset, amount):
    return s[offset-1:offset+amount-1]

def left(s, amount):
    return s[:amount]

def messaging(title,body):
    apobj = apprise.Apprise()
    if config['Notification']['Pushover']:
        apobj.add(config['Notification']['Pushover'])
        apobj.notify(
            title=title,
            body=body,
        )

wanted = list()
completed = list()
completedsave = list()
countWanted = int()
countCompleted = int()
Downloadlist = list()
newdownloads = int()
logger.info('---------------------------------------------------------------------------------------')

logger.info('Run at: %s', pendulum.now())

config = configparser.ConfigParser()
if len(config.read('config.txt'))==0:                           #if config file isn't found, create it
    cfgfile = open("config.txt", 'w')
    config.add_section('Default')
    config.add_section('Rss')
    config.add_section('Torrent')
    config.add_section('Notification')
    config.set('Default','wanted', 'wanted.txt')                #Every Searchterm in a line in the wanted file
    config.set('Default','completed', 'completed.txt')          #Torrents which have been sent to qBittorrent
    config.set('Default', 'purge', '30')                        #How old downloads should be monitored? (in days)
    config.set('Notification', '#Pushover', 'pover://user@token')#see more @ https://github.com/caronc/apprise
                                                                ###other configs will follow
    config.set('Notification', '#Boxcar', 'boxcar://hostname')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Discord', 'discord://webhook_id/webhook_token')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Emby', 'emby://user@hostname/')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Boxcar', 'boxcar://hostname')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Faast', 'faast://authorizationtoken')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Growl', 'growl://password@hostname:port')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#IFTT', 'ifttt://webhooksID/EventToTrigger')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Join', 'join://apikey/device')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#KODI', 'kodi://hostname')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Mattermost', 'mmost://hostname/authkey')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Prowl', 'prowl://apikey')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Pushalot', 'palot://authorizationtoken')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#PushBullett', 'pbul://accesstoken')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Pushjet', 'pjet://secret')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Rocketchat', 'rocket://user:password@hostname/RoomID/Channel')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Slack', 'slack://TokenA/TokenB/TokenC/Channel')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Stride', 'stride://auth_token/cloud_id/convo_id')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Telegram', 'tgram://bottoken/ChatID')  #see more @ https://github.com/caronc/apprise
    config.set('Notification', '#Twitter', 'tweet://user@CKey/CSecret/AKey/ASecret')  # see more @ https://github.com/caronc/apprise
    config.set('Notification', '#mailto://', 'mailto://userid:pass@domain.com')  # see more @ https://github.com/caronc/apprise

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

#messaging("Test","Test")

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
        date=pendulum.parse(left(line.rstrip(), sep), strict=False)
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

newdownloads=0
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
                    tmpLogger="Added: " + post.title
                    logger.info(tmpLogger)
                    messaging("New Download added",tmpLogger)
                    newdownloads+=1
                except:
                    logger.critical("Download could not be added to qBittorrent\n")

if newdownloads==0:
    logger.info("No new downloads found/added.")
with open(fileCompleted, "w") as foCompleted:
    for i in reversed(completedsave):
        foCompleted.writelines(i + "\n")
foCompleted.close()
