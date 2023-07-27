# sort file with name or type + name
from typing import List


def sort_filename(filelist) -> List:
    """
    sort by filename (not check file types)
    add digits to be same -> lexicographic order
    """
    file = filelist.copy()
    max_len = 0
    for i in file:
        if len(i) > max_len:
            max_len = len(i)
    for i, v in enumerate(file):
        if len(v) != max_len:
            file[i] = v[0] + '0' * (max_len - len(v)) + v[1:]
    file = sorted(file)

    for i, v in enumerate(file):
        file[i] = v.replace('0.', '..').replace('0', '').replace('..', '0.')
    return file


def sort_by_filetypes_and_filename(filelist) -> List:
    """
    sort by filename and file types
    add digits to be same -> lexicographic order
    """
    filelist.sort(key=lambda x: x[x.index(".")+1:])
    ans = []
    prev = None
    left = 0
    for i in range(len(filelist)):
        file_type = filelist[i][filelist[i].index(".")+1:]
        if prev is not None and prev != file_type:
            ans.extend(sort_filename(filelist[left:i]))
            left = i
        prev = file_type
    ans.extend(sort_filename(filelist[left:]))

    return ans


def main():
    _list = ['a182.txt', 'a12.wav', 'a8.txt', 'b10.txt', 'b100.txt', 'b2.txt', 'b19.txt', 'c8.bat', 'a3.txt', 'c999.txt']
    print(f"original list: {_list}")
    print(f"sort_by_filename:. {sort_filename(_list)}")
    print(f"sort_by_filetypes_and_filename: {sort_by_filetypes_and_filename(_list)}")


if __name__ == '__main__':
    main()