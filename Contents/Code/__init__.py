# these imports just for make my IDE happy.
# they will be removed on packaging because it crashes plex.
from py2app.bundletemplate.lib.site import L
from stubs import Plugin
from api.networkkit import HTTP
from objects import MediaContainer, DirectoryItem, VideoItem, MessageContainer, Function, InputDirectoryItem, PrefsItem

VIDEO_PREFIX = "/video/turbofilm"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART  = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################

def Start():

    ## make this plugin show up in the 'Video' section
    ## in Plex. The L() function pulls the string out of the strings
    ## file in the Contents/Strings/ folder in the bundle
    ## see also:
    ##  http://dev.plexapp.com/docs/mod_Plugin.html
    ##  http://dev.plexapp.com/docs/Bundle.html#the-strings-directory
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList")
    Plugin.AddViewGroup("List")

    ## set some defaults so that you don't have to
    ## pass these parameters to these object types
    ## every single time
    ## see also:
    ##  http://dev.plexapp.com/docs/Objects.html
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(ICON)
    VideoItem.thumb = R(ICON)
    
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'

# see:
#  http://dev.plexapp.com/docs/Functions.html#ValidatePrefs
def ValidatePrefs():
    u = Prefs['username']
    p = Prefs['password']
    ## do some checks and return a
    ## message container
    if u and p:
        return MessageContainer(
            "Success",
            "User and password provided ok"
        )
    else:
        return MessageContainer(
            "Error",
            "You need to provide both a user and password"
        )

  


#### the rest of these are user created functions and
#### are not reserved by the plugin framework.
#### see: http://dev.plexapp.com/docs/Functions.html for
#### a list of reserved functions above



#
# Example main menu referenced in the Start() method
# for the 'Video' prefix handler
#

def VideoMainMenu():

    # Container acting sort of like a folder on
    # a file system containing other things like
    # "sub-folders", videos, music, etc
    # see:
    #  http://dev.plexapp.com/docs/Objects.html#MediaContainer
    dir = MediaContainer(viewGroup="InfoList")


    # see:
    #  http://dev.plexapp.com/docs/Objects.html#DirectoryItem
    #  http://dev.plexapp.com/docs/Objects.html#function-objects
    dir.Append(
        Function(
            DirectoryItem(
                CallbackExample,
                "directory item title",
                subtitle="subtitle",
                summary="clicking on me will call CallbackExample",
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )
  
    # Part of the "search" example 
    # see also:
    #   http://dev.plexapp.com/docs/Objects.html#InputDirectoryItem
    dir.Append(
        Function(
            InputDirectoryItem(
                SearchResults,
                "Search title",
                "Search subtitle",
                summary="This lets you search stuff",
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )

  
    # Part of the "preferences" example 
    # see also:
    #  http://dev.plexapp.com/docs/Objects.html#PrefsItem
    #  http://dev.plexapp.com/docs/Functions.html#CreatePrefs
    #  http://dev.plexapp.com/docs/Functions.html#ValidatePrefs 
    dir.Append(
        PrefsItem(
            title="Your preferences",
            subtile="So you can set preferences",
            summary="lets you set preferences",
            thumb=R(ICON)
        )
    )

    # ... and then return the container
    return dir

def CallbackExample(sender):

    ## you might want to try making me return a MediaContainer
    ## containing a list of DirectoryItems to see what happens =)

    return MessageContainer(
        "Not implemented",
        "In real life, you'll make more than one callback,\nand you'll do something useful.\nsender.itemTitle=%s" % sender.itemTitle
    )

# Part of the "search" example 
# query will contain the string that the user entered
# see also:
#   http://dev.plexapp.com/docs/Objects.html#InputDirectoryItem
def SearchResults(sender,query=None):
    return MessageContainer(
        "Not implemented",
        "In real life, you would probably perform some search using python\nand then build a MediaContainer with items\nfor the results"
    )
    
  
