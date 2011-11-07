# these imports just for make my IDE happy.
# they will be removed on packaging because it crashes plex.
from distutils.log import Log #tmp
from stubs import R, Prefs, L, CACHE_1HOUR #tmp
from stubs import Plugin, HTTP #tmp
from objects import MediaContainer, DirectoryItem, VideoItem, MessageContainer, Function, PrefsItem #tmp

from turbofilm import API

VIDEO_PREFIX = "/video/turbofilm"

NAME = L('Title')
ART  = 'art-default.jpg'
ICON = 'icon-default.png'

api = API()

####################################################################################################

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

def ValidatePrefs():
    u = Prefs['username']
    p = Prefs['password']
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

def AllEpisodes(sender, season_url, season_art):
    mc = MediaContainer(viewGroup="Episodes")
    episodes = api.FetchEpisodesList(season_url)

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
    seasons = api.FetchSeasonsList(tvshow_url)
    
    if seasons is None:
        return MessageContainer("Error", "error")
    for season in seasons:
        mc.Append(
            Function(
                DirectoryItem(
                    AllEpisodes,
                    title = season.title,
                    art = tvshow_art,
                    leafCount = len(api.FetchEpisodesList(season.url)),
                    viewedLeafCount = 0
                ),
                season_url = season.url,
                season_art = tvshow_art,
            )
        )

    return mc

def AllTVShows(sender):
    mc = MediaContainer(viewGroup="List")
    shows = api.FetchShowsList()
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

def ClearCache(sender):
    HTTP.ClearCache()

def VideoMainMenu():
    dir = MediaContainer(viewGroup="InfoList")
    if api.auth(Prefs['username'], Prefs['password']):
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

    dir.Append(
        Function(
            DirectoryItem(
                ClearCache,
                title = L("Clear Cache"),
                thumb = R(ICON)
            )
        )
    )

    return dir

def CallbackExample(sender):
    return MessageContainer(
        "Not implemented",
        "In real life, you'll make more than one callback,\nand you'll do something useful.\nsender.itemTitle=%s" % sender.itemTitle
    )
