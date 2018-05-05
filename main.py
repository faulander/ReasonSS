try:
    import feedparser
    import configparser
    from qbittorrent import Client
except ImportError:
    print("Needed Modules are not installed.\n")
    print("use:\n")
    print("pip install feedparser\n")
    print("pip install configparser\n")
    print("pip install qbittorrent\n")


wanted = list()
completed = list()
countWanted = int()
countCompleted = int()
Downloadlist = list()

config = configparser.ConfigParser()
if len(config.read('config.txt'))==0:                           #if config file isn't found, create it
    cfgfile = open("config.txt", 'w')
    config.add_section('Default')
    config.add_section('Rss')
    config.add_section('Torrent')
    config.set('Default','wanted', 'wanted.txt')                #Every Searchterm in a line in the wanted file
    config.set('Default','completed', 'completed.txt')          #Torrents which have been sent to qBittorrent
    config.set('Default', 'purge', '1000')                      #How many old downloads should be monitored?
    config.set('Rss','rss', 'http://www.example.org/feed')      #Feed Adress
    config.set('Torrent', 'qbclient', 'http://127.0.0.1:8080')  #WEB-Access for qBittorrent must be available
    config.set('Torrent', 'category','')                        #no category as standard
    config.write(cfgfile)
    cfgfile.close()

qb=Client(config['Torrent']['qbclient'])

config.read('config.txt')                                       #read config
purge=int(config['Default']['purge'])
fileWanted=config['Default']['wanted']                          #read the searchterms for the RSS-Filter
category=config['Torrent']['category']

with open(fileWanted) as foWanted:
    for line in foWanted:
        wanted.append(line.rstrip())
        countWanted=countWanted+1
foWanted.close()

fileCompleted=config['Default']['completed']                    #should be overworked, file will get big!
with open(fileCompleted) as foCompleted:
    for line in foCompleted:
        completed.append(line.rstrip())
        countCompleted=countCompleted+1

print(countWanted, " searchterms are processed")
print(countCompleted, " old downloads are ignored.")
print("Purge at: ", purge)
print("Category: ", category)

d = feedparser.parse(config['Rss']['rss'])
print("Status: ", d.status)

#print(qb.torrents(category=config['Torrent']['category']))

for post in d.entries:                                          #check all items from the RSS-Feed
    #print(post.title)
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
                Downloadlist.append(post.link)

print ("new Downloads: ", len(Downloadlist))

if len(Downloadlist)>0:
    try:
        qb.download_from_link(Downloadlist)
        for i in Downloadlist:
            completed.append(i)
            print("Added: ", i)
    except:
        print("Download could not be added to qBittorrent\n")

lines=0
with open(fileCompleted, "w") as foCompleted:
    for i in completed:
        lines=lines+1
        if lines<purge:
            foCompleted.writelines(i + "\n")
foCompleted.close()