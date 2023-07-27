import requests

try:
    import http.cookiejar as cookiejar
    CookieLoadError = (FileNotFoundError, cookiejar.LoadError)
except ImportError:
    import cookielib as cookiejar
    CookieLoadError = IOError

from .transcripts import TranscriptListFetcher, Transcript

from typing import List


class YoutubeCaptions:
    @classmethod
    def list_transcripts(cls, video_id, proxies=None, cookies=None):
        with requests.Session() as http_client:
            if cookies:
                http_client.cookies = cls._load_cookies()
            http_client.proxies = proxies if proxies else {}
            return TranscriptListFetcher(http_client).fetch(video_id)

    @classmethod
    def get_transcripts(cls, video_ids: List[str], languages=("en",), continue_after_error=False,  proxies=None, cookies=None):
        assert isinstance(video_ids, list), "`video_ids` must be a list of strings"

        data = {}
        unretrievable_videos = []

        for video_id in video_ids:
            try:
                data[video_id] = cls.get_transcript(video_id, languages, proxies, cookies)
            except Exception as error:
                if not continue_after_error:
                    raise error

                unretrievable_videos.append(video_id)

        return data, unretrievable_videos

    @classmethod
    def get_transcript(cls, video_id: str, languages=("en",), proxies=None, cookies=None):
        assert isinstance(video_id, str), "`video_ids` must be a string"
        return cls.list_transcripts(video_id, proxies, cookies).find_transcript(languages).fetch()

    @classmethod
    def _load_cookies(cls, cookies, video_id):
        try:
            cookie_jar = cookiejar.MozillaCookieJar()
            cookie_jar.load(cookies)
            if not cookie_jar:
                raise Exception(f"Cookie Invalid {video_id}")
            return cookie_jar
        except Exception as error:
            raise f"{error}, Cookie Path Invalid {video_id}"
