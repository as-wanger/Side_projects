from __future__ import annotations
from itertools import zip_longest

import dataclasses
from collections.abc import Iterator, Mapping
from typing import TypeVar, overload, Tuple

_K = TypeVar('_K')

_V1 = TypeVar('_V1')
_V2 = TypeVar('_V2')
_V3 = TypeVar('_V3')


@overload
def dict_zip(
        m1: Mapping[_K, _V1],
) -> Iterator[Tuple[_K, _V1]]:
    ...


@overload
def dict_zip(
        m1: Mapping[_K, _V1],
        m2: Mapping[_K, _V2],
) -> Iterator[Tuple[_K, _V1, _V2]]:
    ...


@overload
def dict_zip(
        m1: Mapping[_K, _V1],
        m2: Mapping[_K, _V2],
        m3: Mapping[_K, _V3],
) -> Iterator[Tuple[_K, _V1, _V2, _V3]]:
    ...


def zip_longest_example():
    ids = [1, 2, 3, 4, 5, 6]
    name = ['a', 'b', 'c']
    text = ['one', 'two', 'three', 'four', 'five', 'six']
    for a, b, c in zip_longest(ids, name, text):
        print(f"{a} has {b} and {c}")


def dict_zip(*dicts):
    if not dicts:
        return

    n = len(dicts[0])
    if any(len(d) != n for d in dicts):
        raise ValueError("arguments must have the same length.")

    for key, first_val in dicts[0].items():
        yield key, first_val, *(other[key] for other in dicts[1:])


def dict_zip_intersection(*dicts):
    if not dicts:
        return

    keys = set(dicts[0]).intersection(*dicts[1:])
    for key in keys:
        yield key, *(d[key] for d in dicts)


def dict_zip_union(*dicts, fillvalue=None):
    if not dicts:
        return

    keys = set(dicts[0]).union(*dicts[1:])
    for key in keys:
        yield key, *(d.get(key, fillvalue) for d in dicts)


def combined_dict_example():
    @dataclasses.dataclass
    class ChannelData:
        id: str
        name: str
        sub_count: int

    channels = [
        ChannelData(id='aSDFsdf', name='wanger', sub_count=1_000),
        ChannelData(id='qewcrqwv', name='test title', sub_count=87),
        ChannelData(id='hgjkmomkbmkvkj', name='test content', sub_count=94_000),
    ]

    data = {channel.id: channel for channel in channels}

    for cid, channel in data.items():
        print(f'{channel.name} has {channel.sub_count} subscribers! Watch in here ././{cid}')


def separate_dicts_example():
    names = {'aSDFsdf': "wanger",
             'qewcrqwv': "test title",
             'hgjkmomkbmkvkj': 'test content'}
    sub_counts = {'aSDFsdf': 1_000,
                  'qewcrqwv': 87,
                  'hgjkmomkbmkvkj': 94_000}

    for cid, names, sub_count in dict_zip(names, sub_counts):
        print(f"{names} has {sub_count} subscribers! Watch in here ././{cid}")


if __name__ == '__main__':
    zip_longest_example()
    combined_dict_example()
    separate_dicts_example()
