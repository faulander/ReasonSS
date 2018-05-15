# ReasonSS
Automatic Python RSS &amp; qBittorrent Downloader
The following python modules need to be installed:
- feedparser
- configparser
- qbittorrent
- Pendulum
- Apprise

Description:
ReasonSS loads a list of searchterms (standard = 'wanted.txt') and checks a given RSS-Feed for this terms.
If it finds any, it sends the magnet-links to qBitorrent.
Config can be adjusted in 'config.txt'

To-Do:
- Feedback from qBittorrent --> Waiting for new version of qBittorrent
- Transmission integration
- additional rss feeds

News:
+ Logging
+ Integration of several Notification Services like Pushover, Slack, Pushbullett etc.
+ Purging now works on age of downloads ('purge' in config.txt, counted in days)
+ Better Error Handling
