from yt_captions.manaual_transcripts import YoutubeCaptions


def main():
    video_id = "GiQ8MxOfmP0"
    a = YoutubeCaptions().get_transcript(video_id, languages=["zh-Hant", "zh-TW", "en"])
    # print("\n".join(v["text"] for v in a))

    # b = YoutubeCaptions.list_transcripts(video_id)
    # print(b)

    c = YoutubeCaptions().get_transcripts([video_id], languages=["zh-TW", "en"])
    # print("\n".join(v["text"] for v in c))
    for id in c[0]:
        print(f"--- Start from {id} ---\n" + "\n".join(v["text"] for v in c[0][id]))


if __name__ == '__main__':
    main()