import re
import turbofilm as api
import tvdb
from utils import get_url

from distutils.log import Log #tmp
from stubs import HTTP, CACHE_1HOUR #tmp

class Show():
    def __init__(self, htmlItem):
        title_en = htmlItem.xpath('span/span[3]')[0].text
        title_ru = htmlItem.xpath('span/span[4]')[0].text
        id = re.search('(\d+)', htmlItem.xpath('span/span[1]/img')[0].get('src')).group(0)
        search_result = tvdb.searchByGuid('en', title_en) # TODO: get current locale

        self.tvdb_id = search_result[0]['guid']
        self.id = id
        self.url = htmlItem.get('href')
        self.title_en = title_en
        self.title_ru = title_ru
        self.summary = search_result[0]['summary']
        self.poster = "http://thetvdb.com/banners/_cache/posters/%s-1.jpg" % self.tvdb_id
        self.info = "info"
        self.art = "http://thetvdb.com/banners/fanart/original/%s-1.jpg" % self.tvdb_id

        # TODO: precache background images
#        HTTP.PreCache(self.art, cacheTime=CACHE_1HOUR * 24 * 10) # 10 days

class Season():
    def __init__(self, htmlItem):
        title = htmlItem.xpath('span')[0].text
        url = htmlItem.get('href')

        self.tvdb_id = 239761
        self.url = url
        self.title = title
        self.poster = "http://thetvdb.com/banners/_cache/seasons/%s-1.jpg" % self.tvdb_id

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
