# -*- coding: UTF-8 -*-
# (updated 7-19-2022)
'''
    Infinity Internal Scrapers
'''

from json import loads as jsloads
from resource.lib.modules import source_utils
import requests

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

    def results(self, data):
        sources = []
        if not data: return sources
        append = sources.append
        try:
            from resource.lib.modules import log_utils
            aliases = data['aliases']
            year = data['year']
            imdb = data['imdb_id']
            season = None
            episode = None
            if data['media_type'] == 'movie':
                title = data['title'].replace('&', 'and').replace('/', ' ')
                episode_title = None
                hdlr = year
                link = self.movieSearch_link % imdb
            else:
                title = data['title'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
                episode_title = data['ep_name']
                season = data['season']
                episode = data['episode']
                hdlr = 'S%02dE%02d' % (int(season), int(episode))
                link = self.tvSearch_link % (imdb, season, episode)
            url = '%s%s' % (self.base_link, link)
            # log_utils.log('url = %s' % url, level=log_utils.LOGDEBUG)
            r = requests.get(url, headers=headers, timeout=6).text
            if not r: return sources
            r = jsloads(r)
            results = r['streams']
        except Exception as e:
            from resource.lib.modules import log_utils
            log_utils.log('davio scraper Exception\n' + str(e), level=log_utils.LOGERROR)
            return sources

        for item in results:
            try:
                url = item['url']
                description = item['description']
                try:
                    size = description.split('💾')[1]
                except:
                    size = 0
                try:
                    file_name = description.split('\n')[0]
                except:
                    file_name = 'Unknown'
                origname = file_name.replace('.mp4', '').replace('.mkv', '')
                name = source_utils.clean_title(origname)
                if not source_utils.check_title(title, name, aliases, year, season, episode): continue
                name_info = source_utils.release_info_format(name)
                # if source_utils.remove_lang(name_info, check_foreign_audio): continue
                # if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

                # link_header = client.request(url, output='headers', timeout=5) # to slow to check validity of links
                # if not any(value in str(link_header) for value in ('stream', 'video/mkv')): continue

                try:
                    isize = _size(size)
                except:
                    isize = 0
                quality, info = source_utils.get_file_info(name_info)

                append(
                    {'name': file_name, 'display_name': origname, 'quality': '1080p', 'size': isize, 'size_label': size,
                     'extraInfo': info, 'url_dl': url, 'down_url': url, 'id': url, 'local': False, 'direct': True,
                     'source': 'Davio',
                     'scrape_provider': self.scrape_provider})
            except Exception as e:
                from resource.lib.modules import log_utils
                log_utils.log('davio scraper Exception\n' + str(e), level=log_utils.LOGERROR)
        source_utils.internal_results(self.scrape_provider, sources)
        return sources

    def _size(size):
        try:
            from resource.lib.modules import log_utils
            size = size.split(' ')
            log_utils.log('_size\n' + str(size), level=log_utils.LOGDEBUG)
            isize = float(size[0])
            options = {'GB': isize * (1024 * 1024 * 1024),
                       'MB': isize * (1024 * 1024)}
            fsize = int(options[size[1]])
        except Exception as e:
            from resource.lib.modules import log_utils
            log_utils.log('_size\n' + str(e), level=log_utils.LOGERROR)
        return fsize
