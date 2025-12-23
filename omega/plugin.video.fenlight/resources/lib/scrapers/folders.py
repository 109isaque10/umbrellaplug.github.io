# -*- coding: UTF-8 -*-
# (updated 7-19-2022)
'''
    Infinity Internal Scrapers
'''

from json import loads as jsloads
import requests
from modules import source_utils

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:137.0) Gecko/137.0 Firefox/137.0'}

class source:
    priority = 1
    pack_capable = False
    hasMovies = True
    hasEpisodes = True
    def __init__(self):
        self.language = ['en']
        self.scrape_provider = 'folders'
        self.base_link = "https://davio.327835.xyz"
        self.movieSearch_link = "/eyJkYXZJZCI6ImN1c3RvbSIsIm5hbWUiOiJDdXN0b20iLCJzaG9ydE5hbWUiOiJEQVYiLCJ1cmwiOiJodHRwczovL2Rhdi4zMjc4MzUueHl6IiwidXNlcm5hbWUiOiJqZWxseSIsInBhc3N3b3JkIjoiUTdpRm42bFBQM0YzbTZOb1BLeTVYcWxZRjlXYTc0Iiwicm9vdCI6Ii9GaWxtZXMvIiwicm9vdFRWIjoiL1NlcmlhZG9zLyJ9/stream/movie/%s.json"
        self.tvSearch_link = "/eyJkYXZJZCI6ImN1c3RvbSIsIm5hbWUiOiJDdXN0b20iLCJzaG9ydE5hbWUiOiJEQVYiLCJ1cmwiOiJodHRwczovL2Rhdi4zMjc4MzUueHl6IiwidXNlcm5hbWUiOiJqZWxseSIsInBhc3N3b3JkIjoiUTdpRm42bFBQM0YzbTZOb1BLeTVYcWxZRjlXYTc0Iiwicm9vdCI6Ii9GaWxtZXMvIiwicm9vdFRWIjoiL1NlcmlhZG9zLyJ9/stream/series/%s:%s:%s.json"
        
    def results(self, data, hostDict):
        sources = []
        if not data: return sources
        append = sources.append
        try:
            aliases = data['aliases']
            year = data['year']
            imdb = data['imdb']
            if 'tvshowtitle' in data:
                title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
                episode_title = data['title']
                season = data['season']
                episode = data['episode']
                hdlr = 'S%02dE%02d' % (int(season), int(episode))
                link = self.tvSearch_link % (imdb, season, episode)
            else:
                title = data['title'].replace('&', 'and').replace('/', ' ')
                episode_title = None
                hdlr = year
                link = self.movieSearch_link % imdb
            url = '%s%s' % (self.base_link, link)
            # log_utils.log('url = %s' % url)
            r = requests.get(url, headers=headers, timeout=30)
            if not r: return sources
            r = jsloads(r)
            results = r['streams']
        except:
            source_utils.scraper_error('Davio')
            return sources

        for item in results:
            try:
                url = item['url']
                description = item['description']
                try: size = description.split('💾')[1]
                except: size = 0
                try: name = description.split('\n')[0]
                except: name = 'Unknown'
                name = source_utils.clean_name(name)
                if not source_utils.check_title(title, aliases, name, hdlr, year): continue
                name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
                #if source_utils.remove_lang(name_info, check_foreign_audio): continue
                #if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

                # link_header = client.request(url, output='headers', timeout=5) # to slow to check validity of links
                # if not any(value in str(link_header) for value in ('stream', 'video/mkv')): continue

                quality, info = source_utils.get_release_quality(name_info, url)
                try:
                    dsize, isize= source_utils._size(size)
                    if isize: info.insert(0, isize)
                except: dsize = 0
                info = ' | '.join(info)

                append({'scrape_provider': 'folders', 'source': 'folders', 'quality': '1080p', 'name': name, 'name_info': name_info, 'language': "en",
                            'url_dl': url, 'id': url, 'info': info, 'direct': True, 'debridonly': False, 'size': dsize})
            except:
                source_utils.scraper_error('Davio')
        source_utils.internal_results(self.scrape_provider, sources)
        return sources
