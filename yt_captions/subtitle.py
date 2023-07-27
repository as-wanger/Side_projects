# deprecated

from pytube import YouTube
from bs4 import BeautifulSoup
from typing import Tuple, List, Optional
from datetime import timedelta
from dataclasses import dataclass, field


class YoutubeCaptions:
    def __init__(self, url: str):
        self.url = url
        self._captions = YouTube(url).captions
        self._output = ""

    @property
    def captions(self) -> Optional:
        return self._captions

    @property
    def output(self) -> str:
        return self._output

    def store_xml2srt(self, language: str, features: str) -> None:
        soup = BeautifulSoup(self.captions[language].xml_captions, features=features)
        ps = soup.findAll("p")
        caps_order = Order()
        for i, p in enumerate(ps):
            caps_order.caption_items.append(CapItem(i, p.text, int(p["t"]), int(p["d"])))

        self._output += caps_order.total

    def write_out(self, filename) -> None:
        with open(f".\\{filename}", "w") as f:
            f.write(self._output)
            print("file content")


@dataclass
class CapItem:
    index: int
    text: str
    start: int  # 開始時間
    elapsed_time: int  # 持續時間

    def scope(self) -> int:
        return self.start + self.elapsed_time

    def normalization(self) -> str:
        t = timedelta(milliseconds=self.start)
        t2 = timedelta(milliseconds=(self.start + self.elapsed_time))

        def time_parser(time) -> Tuple[int, ...]:
            hour, minute, second, millisecond = (time.seconds // 3600,
                                                 (time.seconds // 60) % 60,
                                                 time.seconds % 60,
                                                 time.microseconds // 1000)
            return hour, minute, second, millisecond

        h, m, s, ms = time_parser(t)
        h2, m2, s2, ms2 = time_parser(t2)

        return f"{str(self.index + 1)}\n" \
               f"{h:02d}:{m:02d}:{s:02d}:{ms:03d} --> " \
               f"{h2:02d}:{m2:02d}:{s2:02d}:{ms2:03d}\n" \
               f"{self.text}\n\n"


@dataclass
class Order:
    caption_items: List[CapItem] = field(default_factory=list)

    @property
    def total(self) -> str:
        return "".join(cap.normalization() for cap in self.caption_items)

    def length(self):
        return f"there are {len(self.caption_items)} captions."


def main():
    cap = YoutubeCaptions("https://www.youtube.com/watch?v=DhUpxWjOhME")
    print(cap.captions)
    cap.store_xml2srt("en", "xml")
    print(cap.output)
    # cap.write_out()
    print("YT_Captions downloaded successfully.")


if __name__ == '__main__':
    main()
