from ..utils import int_or_none, try_get
from .common import InfoExtractor
import re


class DradioShareIE(InfoExtractor):
    IE_NAME = 'dradio:share'
    _VALID_URL = r'https?://(?:share|srv)\.deutschlandradio\.de/dlf-audiothek-audio-teilen\.(?:3265\.de\.)?html\?(?:mdm:)?audio_id=(?P<id>(?:dira_(?:DLF|DRK|DRW)_[a-f0-9]{8})|\d+)'
    _TESTS = [{
        'url': 'https://share.deutschlandradio.de/dlf-audiothek-audio-teilen.html?audio_id=dira_DRK_9f52c214',
        'info_dict': {
            'ext': 'mp3',
            'id': 'dira_DRK_9f52c214',
            'duration': 381,
            'thumbnail': 'https://assets.deutschlandfunk.de/6bfce715-b38b-4e03-b0e4-2e00d59c42d4/original.jpg?t=1643216095319',
            'title': 'Versandhändler zahlt 5.000 Euro an impfwillige Mitarbeiter',
            'description': 'md5:3047008025a2fb79c2351eb752207e5e',
            'creator': 'Bernhard, Henry; Brink, Nana',
        }
    }, {
        'url': 'https://srv.deutschlandradio.de/dlf-audiothek-audio-teilen.3265.de.html?mdm:audio_id=911081',
        'info_dict': {
            'ext': 'mp3',
            'id': 'dira_DLF_8b1977f6',
            'duration': 343,
            'thumbnail': 'https://assets.deutschlandfunk.de/FILE_0cedfda47911b71109ab377b0b154892/original.jpg?t=1616155532872',
            'title': 'Digitales Reisedokument für Geimpfte - Wie der EU-Impfausweis funktionieren könnte',
            'description': 'md5:10fa6297370cf5a8b7be9d4ea9f02e0b',
            'creator': 'Von Peter Welchering',
        }
    }]

    def _real_extract(self, url):
        aid = self._match_id(url)
        pg = self._download_webpage(url, aid)
        src = self._parse_json(self._html_search_regex(r'<div class="js-audio-player" data-json="(.+)">', pg, 'audio URL'), aid)
        authors = self._html_search_regex(r'<p class="box-details-author">(.+)</p>', pg, 'authors', fatal=False)
        # Generate canonical audio ID to ensure download archive consistency
        if re.match(r'^\d+$', aid):
            pub_map = {'deutschlandfunk': 'DLF', 'deutschlandfunk-nova': 'DRW', 'deutschlandfunk-kultur': 'DRK'}
            short_id = self._search_regex(r'([a-f0-9]+)(?:\.mp3)$', src['audioUrl'], 'canonical audio ID', fatal=False)
            site_abbr = try_get((pub_map, src), lambda p, s: p[s['siteName']])
            if short_id and site_abbr:
                aid = f'dira_{pub_map[src["siteName"]]}_{short_id}'
            else:
                self.report_warning('Could not extract canonical audio ID. Download archives may be inaccurate.')

        return {
            'id': aid,
            'url': src['audioUrl'],
            'duration': int_or_none(src.get('duration')),
            'title': self._html_search_meta(['og:title', 'twitter:title'], pg),
            'description': self._html_search_meta(['description', 'og:description', 'twitter:description'], pg),
            'thumbnail': self._html_search_meta(['og:image', 'twitter:image'], pg),
            'creator': authors
        }
