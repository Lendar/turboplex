import re
from turbofilm import get_url

class Show():
    def __init__(self, htmlItem):
        title_en = htmlItem.xpath('span/span[3]')[0].text
        title_ru = htmlItem.xpath('span/span[4]')[0].text
        id = re.search('(\d+)', htmlItem.xpath('span/span[1]/img')[0].get('src')).group(0)

        self.id = id
        self.url = htmlItem.get('href')
        self.title = '%s / %s' % (title_en, title_ru)
        self.etitle = "subtitle"
        self.thumb = get_url('/media/i/series/%s.png' % id)
        self.info = "info"
        self.art = get_url('/media/i/series/%sts.jpg' % id)

class Season():
    def __init__(self, htmlItem):
        title = htmlItem.xpath('span')[0].text
        url = htmlItem.get('href')

        self.url = url
        self.title = title

class Episode():
    def __init__(self, htmlItem):
        number = re.search('(\d+)', htmlItem.xpath('span/span[2]/span[@class="sserieslistonetxtep"]')[0].text).group(0)
        title_ru = htmlItem.xpath('span/span[2]/span[@class="sserieslistonetxtru"]')[0].text
        title_en = htmlItem.xpath('span/span[2]/span[@class="sserieslistonetxten"]')[0].text

        self.title = "%s. %s" % (number, title_en) + ((" / %s" % title_ru) if title_en != title_ru else "")
        self.url = htmlItem.get('href')
        self.thumb = get_url(htmlItem.xpath("span[@class='sserieslistone']/span[@class='sserieslistoneimg']/img")[0].get('src'))
