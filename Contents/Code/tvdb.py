import re, time, unicodedata, hashlib, types
from distutils.log import Log #tmp
from xml.etree.ElementTree import tostring
from stubs import HTTP, XML #tmp
from objects import MetadataSearchResult #tmp

# Define proxy for TVDB.
TVDB_SITE  = 'thetvdb.com'
TVDB_PROXY = 'thetvdb.plexapp.com'
TVDB_GUID_SEARCH  = 'http://freebase.plexapp.com/tv/guid/'
TVDB_API_KEY    = 'D4DDDAEFAD083E6F'
TVDB_SERIES_URL = '%%s/api/%s/series/%%s' % TVDB_API_KEY
TVDB_SERIES_URL = '%%s/api/%s/series/%%s' % TVDB_API_KEY
TVDB_ZIP_URL    = '%s/all/%%s.zip' % TVDB_SERIES_URL
TVDB_SERIES_URL = '%s/%%s.xml' % TVDB_SERIES_URL
TVDB_BANNER_URL = '%s/banners/'

netLock = Thread.Lock()
Dict['ZIP_MIRROR'] = 'http://' + TVDB_PROXY
Dict['IMG_MIRROR'] = 'http://' + TVDB_PROXY

MIN_RETRY_TIMEOUT = 2
RETRY_TIMEOUT = MIN_RETRY_TIMEOUT
TOTAL_TRIES   = 1
BACKUP_TRIES  = -1

headers = {'User-agent': 'Plex/Nine'}

def GetResultFromNetwork(url, fetchContent=True):
  global successCount, failureCount, RETRY_TIMEOUT

  try:
    netLock.acquire()
    Log("Retrieving URL: " + url)

    tries = TOTAL_TRIES
    while tries > 0:

      try:
        result = HTTP.Request(url, headers=headers, timeout=60)
        if fetchContent:
          result = result.content

        failureCount = 0
        successCount += 1

        if successCount > 20:
          RETRY_TIMEOUT = max(MIN_RETRY_TIMEOUT, RETRY_TIMEOUT/2)
          successCount = 0

        # DONE!
        return result

      except Exception, e:

        # Fast fail a not found.
        if e.code == 404:
          return None

        failureCount += 1
        Log("Failure (%d in a row)" % failureCount)
        successCount = 0
        time.sleep(RETRY_TIMEOUT)

        if failureCount > 5:
          RETRY_TIMEOUT = min(10, RETRY_TIMEOUT * 1.5)
          failureCount = 0

      # On the last tries, attempt to contact the original URL.
      tries = tries - 1
      if tries == BACKUP_TRIES:
        url = url.replace(TVDB_PROXY, TVDB_SITE)
        Log("Falling back to non-proxied URL: " + url)

  finally:
    netLock.release()

  return None


def lev_ratio(s1,s2):
    distance = Util.LevenshteinDistance(safe_unicode(s1), safe_unicode(s2))
    max_len  = float(max([ len(s1), len(s2) ]))

    ratio = 0.0
    try:
        ratio = float(1 - (distance/max_len))
    except:
        pass

    return ratio

def safe_unicode(s,encoding='utf-8'):
    if s is None:
      return None
    if isinstance(s, basestring):
      if isinstance(s, types.UnicodeType):
        return s
      else:
        return s.decode(encoding)
    else:
      return str(s).decode(encoding)

def titleyear_guid(title, year=None):
    if title is None:
      title = ''

    if year == '' or year is None or not year:
      string = u"%s" % identifierize(title)
    else:
      string = u"%s_%s" % (identifierize(title), year)
    return guidize(string)

def identifierize(string):
    string = re.sub( r"\s+", " ", string.strip())
    string = unicodedata.normalize('NFKD', safe_unicode(string))
    string = re.sub(r"['\"!?@#$&%^*\(\)_+\.,;:/]","", string)
    string = re.sub(r"[_ ]+","_", string)
    string = string.strip('_')
    return string.strip().lower()

def guidize(string):
    hash = hashlib.sha1()
    hash.update(string.encode('utf-8'))
    return hash.hexdigest()


def searchByGuid(lang, title, year=None):
    # Compute the GUID
    guid = titleyear_guid(title, year)

    # Now see if we have any matches.
    score = 70
    maxLevBonus = 10
    maxPctBonus = 30

    try:
        res = XML.ElementFromURL(TVDB_GUID_SEARCH + guid[0:2] + '/' + guid + '.xml')
        matchesGroupedById = {}
        for match in res.xpath('//match'):
            id = match.get('guid')
            count = int(match.get('count'))
            pct = int(match.get('percentage'))
            titleBonus = int(lev_ratio(match.get('title'), title) * maxLevBonus)
            titleBonus += len(Util.LongestCommonSubstring(match.get('title'), title))
            bonus = titleBonus
            if matchesGroupedById.has_key(id):
                i = matchesGroupedById.get(id).get('i')
                matchesGroupedById[id] = {
                    'guid': id,
                    'count': matchesGroupedById.get(id).get('count') + count,
                    'pct': matchesGroupedById.get(id).get('pct') + pct,
                    'bonus': matchesGroupedById.get(id).get('bonus') + bonus,
                    'i': i + 1,
                    }
            else:
                matchesGroupedById[id] = {'guid': id, 'count': count, 'pct': pct, 'bonus': bonus, 'i': 1}

        # get the summarized items sorted by the sumed 'count' field
        matches = matchesGroupedById.values()
        matches.sort(lambda x, y: cmp(y['pct'], x['pct']))

        for match in matches:
            # i.e. http://thetvdb.plexapp.com/api/D4DDDAEFAD083E6F/series/108611/en.xml
            xml = XML.ElementFromURL(TVDB_SERIES_URL % (Dict['ZIP_MIRROR'], match.get('guid'), lang))
            match['summary'] = xml.xpath('//Data/Series/Overview')[0].text
            match['year'] = xml.xpath('//Data/Series/FirstAired')[0].text.split('-')[0]

        return matches

    except Exception, e:
      Log(repr(e))
      pass
