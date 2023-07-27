import tempfile
from yt_captions.subtitle import YoutubeCaptions
import os

example_url = "https://www.youtube.com/watch?v=DhUpxWjOhME"


def test_url() -> None:
    cap = YoutubeCaptions(example_url)
    assert cap.captions is not None


def test_print(capture_stdout) -> None:
    cap = YoutubeCaptions(example_url)
    cap.store_xml2srt("en", "xml")
    print(cap.output)
    assert capture_stdout["stdout"] == cap.output + "\n"


def test_write_out() -> None:
    cap = YoutubeCaptions(example_url)
    cap.store_xml2srt("en", "xml")
    filename = "yt_example2.srt"
    cap.write_out(filename)
    # assert os.path.isfile(f"{os.path.dirname(os.path.realpath(__file__))}\\{filename}")
    assert filename in os.listdir(os.getcwd())

    with open(filename, "r") as f:
        file_content = f.read()
    assert cap.output == file_content
    os.remove(filename)


def test_fake_write_out() -> None:
    cap = YoutubeCaptions(example_url)
    cap.store_xml2srt("en", "xml")
    with tempfile.NamedTemporaryFile(prefix="test_", dir=".", delete=False) as f:
        filename = f.name
        with open(filename, "w") as f2:
            f2.write(cap.output)

        with open(filename, "r") as f2:
            assert f2.read() == cap.output
    assert os.path.isfile(filename)
    assert filename.split("\\")[-1] in os.listdir(os.getcwd())
    os.remove(filename)
