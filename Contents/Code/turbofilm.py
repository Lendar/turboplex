from distutils.log import Log #tmp
from stubs import Prefs #tmp
from stubs import HTTP, HTML, JSON #tmp

from models import Show, Episode, Season
from utils import get_url
from xml.etree.ElementTree import tostring

authed = False

def auth(user, passwd):
    global authed
    if authed:
        return True
    req = HTTP.Request(get_url('/Signin'), values={"login": user, "passwd": passwd})
    if "signinform" in str(req):
        Log(str(req))
        Log("Oooops, wrong pass or no creds")
        return False
    Log("Ok, i'm in!")
    authed = True
    return True

def fetch_html(url):
    try:
        html = HTML.ElementFromURL(url)
    except:
        Log('Need auth or bad html')
        html = None
    if html is None or 'signinform' in tostring(html):
        f = auth(Prefs['username'], Prefs['password'])
        if not f:
            return None
        html = HTML.ElementFromURL(url)
    return html

def fetch_shows_list():
    """
    @rtype: Show[]
    """
    showsList = []
    html = fetch_html(get_url())
    if html is None:
        return None
    @parallelize
    def create_shows_list():
        for item in html.xpath('//html/body/div/div/div/div/div/a'):
            @task
            def create_show(i=item):
                show = Show(i)
                showsList.append(show)

    showsList.sort(lambda x,y: -1 if x.title_en < y.title_en else 1)

    return showsList


def fetch_seasons_list(url, tvshow_tvdb_id):
    seasonsList = []
    html = fetch_html(get_url(url))
    if html is None:
        return None
    for item in html.xpath('//html/body/div/div[2]/div[3]/div[@class="seasonnum"]/a'):
        show = Season(item, tvshow_tvdb_id)
        seasonsList.append(show)

    return seasonsList

def fetch_episodes_list(season_url):
    episodesList = []
    html = fetch_html(get_url(season_url))
    if html is None:
        return None
    htmlEpisodes = html.xpath('//html/body/div/div[2]/div[3]/div[2]/a')
    Log('Fetched %s episodes for: %s' % (len(htmlEpisodes), season_url))
    for item in htmlEpisodes:
        episodesList.append(Episode(item))

    return episodesList