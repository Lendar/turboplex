import re
import urllib
import turbofilm as api
import tvdb
from utils import get_url

from distutils.log import Log #tmp
from stubs import HTTP, CACHE_1HOUR #tmp

TVDBAPI_HOST = "http://tvdbapi.appspot.com"
#TVDBAPI_HOST = "http://localhost:8080"

class Show():
    def __init__(self, htmlItem):
        title_en = htmlItem.xpath('span/span[3]')[0].text
        title_ru = htmlItem.xpath('span/span[4]')[0].text
        id = re.search('(\d+)', htmlItem.xpath('span/span[1]/img')[0].get('src')).group(0)

        self.id = id
        self.url = htmlItem.get('href')
        self.title_en = title_en
        self.title_ru = title_ru
        self.summary = ''
        self.poster = "%s/%s/poster" % (TVDBAPI_HOST, urllib.quote(self.title_en))
        self.info = "info"
        self.art = "%s/%s/fanart" % (TVDBAPI_HOST, urllib.quote(self.title_en))

class Season():
    def __init__(self, htmlItem):
        title = htmlItem.xpath('span')[0].text
        url = htmlItem.get('href')

        self.tvdb_id = tvshow_tvdb_id
        self.url = url
        self.title = title
        self.poster = "http://thetvdb.com/banners/_cache/seasons/11-11-2.jpg"

    def episodes_count(self):
        return len(api.fetch_episodes_list(self.url))

class Episode():
    def __init__(self, htmlItem):
        number = re.search('(\d+)', htmlItem.xpath('span/span[2]/span[@class="sserieslistonetxtep"]')[0].text).group(0)
        title_ru = htmlItem.xpath('span/span[2]/span[@class="sserieslistonetxtru"]')[0].text
        title_en = htmlItem.xpath('span/span[2]/span[@class="sserieslistonetxten"]')[0].text

        self.title = "%s. %s" % (number, title_en) + ((" / %s" % title_ru) if title_en != title_ru else "")
        self.url = htmlItem.get('href')
        self.thumb = get_url(htmlItem.xpath("span[@class='sserieslistone']/span[@class='sserieslistoneimg']/img")[0].get('src'))
