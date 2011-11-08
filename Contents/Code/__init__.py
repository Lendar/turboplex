# these imports just for make my IDE happy.
# they will be removed on packaging because it crashes plex.
from distutils.log import Log #tmp
import timeit
import time
from stubs import R, Prefs, L, CACHE_1HOUR #tmp
from stubs import Plugin, HTTP #tmp
from objects import MediaContainer, DirectoryItem, VideoItem, MessageContainer, Function, PrefsItem #tmp

import turbofilm as api

VIDEO_PREFIX = "/video/turbofilm"

NAME = L('Title')
ART  = 'art-default.jpg'
ICON = 'icon-default.png'

LOCALE = Locale.CurrentLocale

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
    # TODO: auth and show 'all series' directory item if prefereces changed.
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
    episodes = api.fetch_episodes_list(season_url)

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

def AllSeasons(sender, tvshow_tvdb_id, tvshow_url, tvshow_art):
    mc = MediaContainer(viewGroup="Seasons")
    seasons = api.fetch_seasons_list(tvshow_url, tvshow_tvdb_id)
    
    if seasons is None:
        return MessageContainer("Error", "error")
    else:
        episodes_count = {}
        @parallelize
        def get_episodes_count_for_season():
            for season in seasons:
                @task
                def get_count(s=season):
                    episodes_count[s.url] = s.episodes_count()

    for season in seasons:
        Log(season.poster)
        mc.Append(
            Function(
                DirectoryItem(
                    AllEpisodes,
                    title = season.title,
                    thumb = season.poster,
                    art = season.poster,
                    leafCount = episodes_count[season.url],
                    viewedLeafCount = 0
                ),
                season_url = season.url,
                season_art = tvshow_art,
            )
        )

    return mc

def AllTVShows(sender):
    mc = MediaContainer(viewGroup="InfoList")
    shows = api.fetch_shows_list()
    if shows is None:
        return MessageContainer("Error", "Can't do that.\nCheck preferences or refill your ballance!")
    for show in shows:
        mc.Append(
            Function(
                DirectoryItem(
                    AllSeasons,
                    title = show.title_ru if (LOCALE == 'ru') else show.title_en,
                    subtitle = show.title_ru if (LOCALE != 'ru') else show.title_en,
                    summary = show.summary,
                    # TODO: this doesn't works.
                    thumb = show.poster,
                    art = show.art
                ),
                tvshow_tvdb_id = show.tvdb_id,
                tvshow_url = show.url,
                tvshow_art = show.art
            )
        )
    return mc

def ClearCache(sender):
    HTTP.ClearCache()
    return MessageContainer(
        L("Done"), 
        L("Cache cleared")
    )

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
