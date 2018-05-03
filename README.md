# ReasonSS
Automatic Python RSS &amp; qBittorrent Downloader
The following python modules need to be installed:
- feedparser
- configparser
- qbittorrent

Description:
ReasonSS loads a list of searchterms (standard = 'wanted.txt') and checks a give RSS-Feed for this terms.
If it finds any, it sends the magnet-links to qBitorrent.
Config can be adjusted in 'config.txt'

To-Do:
- Error Handling
- Feedback from qBittorrent
- Transmission integration
- additional rss feeds
