from distutils.log import Log #tmp
from stubs import Prefs #tmp
from stubs import HTTP, HTML, JSON #tmp

from models import Show, Episode, Season
from xml.etree.ElementTree import tostring

SITE = "http://turbofilm.tv"

def get_url(path=""):
    return SITE + path

class API():
    def __init__(self):
        self.authed = False

    def auth(self, user, passwd):
        if self.authed:
            return True
        req = HTTP.Request(get_url('/Signin'), values={"login": user, "passwd": passwd})
        if "signinform" in str(req):
            Log("Oooops, wrong pass or no creds")
            return False
        Log("Ok, i'm in!")
        self.authed = True
        return True

    def fetch_html(self, url):
        try:
            html = HTML.ElementFromURL(url)
        except:
            Log('Need auth or bad html')
            html = None
        if html is None or 'signinform' in tostring(html):
            f = self.auth(Prefs['username'], Prefs['password'])
            if not f:
                return None
            html = HTML.ElementFromURL(url)
        return html

    def FetchShowsList(self):
        """
        @rtype: Show[]
        """
        showsList = []
        html = self.fetch_html(get_url())
        if html is None:
            return None
        for item in html.xpath('//html/body/div/div/div/div/div/a'):
            show = Show(item)
            showsList.append(show)
        showsList.sort(lambda x,y: -1 if x.title < y.title else 1)
        return showsList


    def FetchSeasonsList(self, url):
        seasonsList = []
        html = self.fetch_html(get_url(url))
        if html is None:
            return None
        for item in html.xpath('//html/body/div/div[2]/div[3]/div[@class="seasonnum"]/a'):
            show = Season(item)
            seasonsList.append(show)

        seasonsList.sort(lambda x,y: -1 if x.title < y.title else 1)

        return seasonsList

    def FetchEpisodesList(self, season_url):
        episodesList = []
        html = self.fetch_html(get_url(season_url))
        if html is None:
            return None
        htmlEpisodes = html.xpath('//html/body/div/div[2]/div[3]/div[2]/a')
        Log('Fetched %s episodes for: %s' % (len(htmlEpisodes), season_url))
        for item in htmlEpisodes:
            episodesList.append(Episode(item))

        return episodesList
