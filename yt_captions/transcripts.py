import html.parser
from html import unescape

import requests
from requests import HTTPError

from typing import List, Dict, Optional

from xml.etree import ElementTree

import re
import json

from itertools import chain

from url_template import WATCH_URL


def _raise_http_errors(response: Optional[requests.Response], video_id):
    try:
        response.raise_for_status()
        return response
    except HTTPError as error:
        raise Exception(error, video_id)


class TranscriptListFetcher:
    def __init__(self, http_client):
        self._http_client = http_client

    def fetch(self, video_id):
        return TranscriptList.build(
            self._http_client,
            video_id,
            self._extract_captions_json(self._fetch_video_html(video_id), video_id)
        )

    def _extract_captions_json(self, html: str, video_id):
        splitted_html = html.split('"captions":')

        if len(splitted_html) <= 1:
            # Since it's a demo, make it ambiguous and short
            raise Exception

        captions_json = json.loads(
            splitted_html[1].split(',"videoDetails')[0].replace('\n', '')
        ).get('playerCaptionsTracklistRenderer')
        if captions_json is None:
            raise Exception(f"TranscriptsDisabled {video_id}")

        if "captionTracks" not in captions_json:
            raise Exception(f"NoTranscriptAvailable {video_id}")

        return captions_json

    def _create_consent_cookie(self, html, video_id):
        match = re.search('name="v" value="(.*?)"', html)
        if match is None:
            raise Exception(video_id)
        self._http_client.cookies.set('CONSENT', 'YES+' + match.group(1), domain='.youtube.com')

    def _fetch_video_html(self, video_id):
        html = self._fetch_html(video_id)
        if 'action="https://consent.youtube.com/s"' in html:
            self._create_consent_cookie(html, video_id)
            html = self._fetch_html(video_id)
            if 'action="https://consent.youtube.com/s"' in html:
                raise Exception(f"FailedToCreateConsentCookie {video_id}")
        return html

    def _fetch_html(self, video_id):
        response = self._http_client.get(WATCH_URL.format(video_id=video_id))
        return unescape(_raise_http_errors(response, video_id).text)


class TranscriptList:
    def __init__(self, video_id: str, manually_created_transcripts: Dict,
                 generated_transcripts: Dict,
                 translation_languages: List[Dict]):
        self.video_id = video_id,
        self._manually_created_transcripts = manually_created_transcripts,
        self._generated_transcripts = generated_transcripts,
        self._translation_languages = translation_languages

    @staticmethod
    def build(http_client, video_id, captions_json):
        translation_languages = [
            {
                'language': translation_language['languageName']['simpleText'],
                'language_code': translation_language['languageCode'],
            } for translation_language in captions_json['translationLanguages']
        ]

        manually_created_transcripts = {}
        generated_transcripts = {}

        for caption in captions_json['captionTracks']:
            if caption.get('kind', '') == 'asr':
                transcript_dict = generated_transcripts
            else:
                transcript_dict = manually_created_transcripts

            transcript_dict[caption['languageCode']] = Transcript(
                http_client,
                video_id,
                caption['baseUrl'],
                caption['name']['simpleText'],
                caption['languageCode'],
                caption.get('kind', '') == 'asr',
                translation_languages if caption.get('isTranslatable', False) else []
            )

        return TranscriptList(
            video_id,
            manually_created_transcripts,
            generated_transcripts,
            translation_languages,
        )

    def __iter__(self):
        return iter(chain(self._manually_created_transcripts,
                          self._generated_transcripts))

    def find_transcript(self, language_codes):
        return self._find_transcript(language_codes, [self._manually_created_transcripts, self._generated_transcripts])

    def find_generated_transcript(self, language_codes):
        return self._find_transcript(language_codes, [self._generated_transcripts, ])

    def find_manually_created_transcript(self, language_codes):
        return self._find_transcript(language_codes, [self._manually_created_transcripts, ])

    def _find_transcript(self, language_codes, transcript_dicts):
        for language_code in language_codes:
            for transcript_dict in transcript_dicts:
                if language_code in transcript_dict[0]:
                    return transcript_dict[0][language_code]

        raise Exception(f"Not found any transcript, {self.video_id}, {language_codes}, {self}")

    def __str__(self):
        return (
            'For this video ({video_id}) transcripts are available in the following languages:\n\n'
            '(MANUALLY CREATED)\n'
            '{available_manually_created_transcript_languages}\n\n'
            '(GENERATED)\n'
            '{available_generated_transcripts}\n\n'
            '(TRANSLATION LANGUAGES)\n'
            '{available_translation_languages}'
        ).format(
            video_id=self.video_id,
            available_manually_created_transcript_languages=self.get_language_description(
                str(transcript) for transcript in self._manually_created_transcripts[0].values()
            ),
            available_generated_transcripts=self.get_language_description(
                str(transcript) for transcript in self._generated_transcripts[0].values()
            ),
            available_translation_languages=self.get_language_description(
                '{language_code} ("{language}")'.format(
                    language=translation_language['language'],
                    language_code=translation_language['language_code'],
                ) for translation_language in self._translation_languages
            )
        )

    def get_language_description(self, transcript_strings):
        description = "\n".join(f" - {transcript}" for transcript in transcript_strings)
        return description if description else "None"


class Transcript:
    def __init__(self, http_client, video_id, url, language, language_code, is_generated, translation_languages):
        """
        You probably don"t want to initialize this directly. Usually you"ll access Transcript objects using a
        TranscriptList
        """
        self._http_client = http_client
        self.video_id = video_id
        self._url = url
        self.language = language
        self.language_code = language_code
        self.is_generated = is_generated
        self._translation_languages = translation_languages
        self._translation_languages_dict = {
            translation_language["language_code"]: translation_language["language"]
            for translation_language in translation_languages
        }

    def fetch(self):
        response = self._http_client.get(self._url)
        return _TranscriptParser().parse(
            _raise_http_errors(response, self.video_id).text,
        )

    def __str__(self):
        return '{language_code} ("{language}"){translation_description}'.format(
            language=self.language,
            language_code=self.language_code,
            translation_description='[TRANSLATABLE]' if self.is_translatable else ''
        )

    @property
    def is_translatable(self):
        return len(self._translation_languages) > 0

    def translate(self, language_code):
        if not self.is_translatable:
            raise Exception("No Translatable")

        if language_code not in self._translation_languages_dict:
            raise Exception("Translation language not available")

        return Transcript(
            self._http_client,
            self.video_id,
            '{url}&tlang={language_code}'.format(url=self._url, language_code=language_code),
            self._translation_languages_dict[language_code],
            language_code,
            True,
            []
        )


class _TranscriptParser:
    # any element except for > in 0 or more count -> all not > elements
    html_tag_regex = re.compile(r'<[^>]*>', re.IGNORECASE)

    def parse(self, plain_data):
        return [
            {
                "text": re.sub(self.html_tag_regex, "", unescape(xml_element.text)),
                "start": float(xml_element.attrib["start"]),
                "duration": float(xml_element.attrib.get("dur", "0.0")),
            }
            for xml_element in ElementTree.fromstring(plain_data)
            if xml_element.text is not None
        ]
