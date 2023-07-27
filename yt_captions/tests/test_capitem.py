import pytest
from yt_captions.subtitle import CapItem


@pytest.mark.parametrize("test_input, expected", [
    (CapItem(7, "t testing", 0, 2810),
     f"8\n00:00:00:000 --> 00:00:02:810\nt testing\n\n"),
    (CapItem(113, "114 text ", 10076, 59683),
     f"114\n00:00:10:076 --> 00:01:09:759\n114 text \n\n"),
    (CapItem(388, "Thanks again for watching.", 48763, 123456),
     f"389\n00:00:48:763 --> 00:02:52:219\nThanks again for watching.\n\n"),
])
def test_time_parser(test_input, expected):
    assert test_input.normalization() == expected


def test_scope():
    cap = CapItem(0, "", start=123, elapsed_time=456)
    assert cap.scope() == 579

