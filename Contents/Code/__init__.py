# these imports just for make my IDE happy.
# they will be removed on packaging because it crashes plex.
from py2app.bundletemplate.lib.site import L #tmp
from distutils.log import Log #tmp
from stubs import Plugin, HTTP, HTML, JSON #tmp
from objects import MediaContainer, DirectoryItem, VideoItem, MessageContainer, Function, InputDirectoryItem, PrefsItem #tmp

from xml.etree.ElementTree import tostring
import models

VIDEO_PREFIX = "/video/turbofilm"

NAME = L('Title')
ART  = 'art-default.jpg'
ICON = 'icon-default.png'
SITE = "http://turbofilm.tv"

####################################################################################################

authed = False

def full_url(url):
    return SITE + url

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList")
    Plugin.AddViewGroup("List")
    Plugin.AddViewGroup("Seasons", viewMode="Seasons")
    Plugin.AddViewGroup("Episodes", viewMode="Episodes")

    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(ICON)
    VideoItem.thumb = R(ICON)
    
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'

    # TODO: just for testing, remove in real use of plugin.
    HTTP.ClearCache()

def ValidatePrefs():
    u = Prefs['username']
    p = Prefs['password']
    ## do some checks and return a
    ## message container
    if u and p:
        return MessageContainer(
            L("PrefsSuccess"),
            L("PrefsSuccessMessage")
        )
    else:
        return MessageContainer(
            L("PrefsError"),
            L("PrefsErrorMessage")
        )

def Authentificate(user, passwd):
    global authed
    if authed:
        return True
    req = HTTP.Request(SITE + '/Signin', values={"login": user, "passwd": passwd})
    if "signinform" in str(req):
        Log("Oooops, wrong pass or no creds")
        return False
    Log("Ok, i'm in!")
    authed = True
    return True

def FetchHTML(url):
    try:
        html = HTML.ElementFromURL(url)
    except:
        Log('Need auth or bad html')
        html = None
    if html is None or 'signinform' in tostring(html):
        f = Authentificate(Prefs['username'], Prefs['password'])
        if not f:
            return None
        html = HTML.ElementFromURL(url)
    return html

def FetchShowsList():
    """
    @rtype: Show[]
    """
    showsList = []
    html = FetchHTML(SITE)
    if html is None:
        return None
    for item in html.xpath('//html/body/div/div/div/div/div/a'):
        show = models.Show(item)
        showsList.append(show)
    showsList.sort(lambda x,y: -1 if x.title < y.title else 1)
    return showsList


def FetchSeasonsList(url):
    seasonsList = []
    html = FetchHTML(full_url(url))
    if html is None:
        return None
    for item in html.xpath('//html/body/div/div[2]/div[3]/div[@class="seasonnum"]/a'):
        show = models.Season(item)
        seasonsList.append(show)

    seasonsList.sort(lambda x,y: -1 if x.title < y.title else 1)

    return seasonsList

def FetchEpisodesList(season_url):
    episodesList = []
    html = FetchHTML(full_url(season_url))
    if html is None:
        return None
    htmlEpisodes = html.xpath('//html/body/div/div[2]/div[3]/div[2]/a')
    Log('Fetched %s episodes for: %s' % (len(htmlEpisodes), season_url))
    for item in htmlEpisodes:
        episodesList.append(models.Episode(item))

    return episodesList

def Episodes(sender, season_url, season_art):
    mc = MediaContainer(viewGroup="Episodes")
    episodes = FetchEpisodesList(season_url)

    if episodes is None:
        return MessageContainer("Error", "error!")

    for episode in episodes:
        mc.Append(
            Function(
                DirectoryItem(
                    CallbackExample,
                    title = episode.title,
                    thumb = episode.thumb,
                    art = season_art
                )
            )
        )

    return mc

def AllSeasons(sender, tvshow_url, tvshow_art):
    mc = MediaContainer(viewGroup="Seasons")
    seasons = FetchSeasonsList(tvshow_url)
    
    if seasons is None:
        return MessageContainer("Error", "error")
    for season in seasons:
        mc.Append(
            Function(
                DirectoryItem(
                    Episodes,
                    title = season.title,
                    art = tvshow_art,
                    leafCount = len(FetchEpisodesList(season.url)),
                    viewedLeafCount = 0
                ),
                season_url = season.url,
                season_art = tvshow_art,
            )
        )

    return mc


def AllTVShows(sender):
    mc = MediaContainer(viewGroup="List")
    shows = FetchShowsList()
    if shows is None:
        return MessageContainer("Error", "Can't do that.\nCheck preferences or refill your ballance!")
    for item in shows:
        mc.Append(
            Function(
                DirectoryItem(
                    AllSeasons,
                    title = item.title,
                    subtitle = item.etitle,
                    summary = item.info,
                    thumb = item.thumb,
                    art = item.art
                ),
                tvshow_url = item.url,
                tvshow_art = item.art
            )
        )
    return mc


def VideoMainMenu():
    dir = MediaContainer(viewGroup="InfoList")
    if Authentificate(Prefs['username'], Prefs['password']):
        dir.Append(
            Function(
                DirectoryItem(
                    AllTVShows,
                    L("TVShowsTitle"),
                    thumb=R(ICON),
                    art=R(ART)
                )
            )
        )
    else:
        Log('No auth!')

    dir.Append(
        PrefsItem(
            title=L("Preferences"),
            summary=L("PreferencesSummary"),
            thumb=R(ICON)
        )
    )

    return dir

def CallbackExample(sender):
    return MessageContainer(
        "Not implemented",
        "In real life, you'll make more than one callback,\nand you'll do something useful.\nsender.itemTitle=%s" % sender.itemTitle
    )
