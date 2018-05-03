import feedparser
import configparser
from dateutil import parser
from qbittorrent import Client

wanted = list()
completed = list()
countWanted = int()
countCompleted = int()
config = configparser.ConfigParser()
if len(config.read('config.txt'))==0:
    cfgfile = open("config.txt", 'w')
    config.add_section('Default')
    config.add_section('Rss')
    config.add_section('Torrent')
    config.set('Default','wanted', 'wanted.txt')
    config.set('Default','completed', 'completed.txt')
    config.set('Rss','rss', 'http://www.example.org/feed')
    config.set('Torrent', 'qbclient', 'http://127.0.0.1:8080')
    config.write(cfgfile)
    cfgfile.close()

config.read('config.txt')

fileWanted=config['Default']['wanted']
with open(fileWanted) as foWanted:
    for line in foWanted:
        wanted.append(line.rstrip())
        countWanted=countWanted+1
foWanted.close()

fileCompleted=config['Default']['completed']
with open(fileCompleted) as foCompleted:
    for line in foCompleted:
        completed.append(line.rstrip())
        countCompleted=countCompleted+1

print(countWanted, " searchterms are processed")
print(countCompleted, " old downloads are ignored.")

d = feedparser.parse(config['Rss']['rss'])
qb=Client(config['Torrent']['qbclient'])

print(qb.torrents(category='P-NEW'))

for post in d.entries:
    for i in wanted:
        if i in str.lower(post.title):          #Wenn gewünschten Imagesets gefunden werden
            #print(post.title)
            download=2
            if len(completed) > 0:
                for l in completed:
                    if l not in post.link:
                        download=1
                    else:
                        download=0
                        break
            else:
                download=1
            if download==1:
                print(post.title)
                qb.download_from_link(post.link, category='P-NEW')
                completed.append(post.link)

with open(fileCompleted, "w") as foCompleted:
    for i in completed:
        foCompleted.writelines(i + "\n")
foCompleted.close()