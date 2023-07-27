from yt_captions.subtitle import CapItem, Order


def test_length():
    order = Order()
    order.caption_items.append(CapItem(0, "", 1, 2))
    order.caption_items.append(CapItem(1, "A", 3, 4))
    assert order.length().split()[2] == "2"
