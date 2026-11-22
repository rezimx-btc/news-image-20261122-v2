# The World in One Day — 22 November 2026

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/rezimx-btc/news-image-20261122-v2/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/rezimx-btc/news-image-20261122-v2/reward.svg)](https://make.fun/bounty/news-image-20261122)

One broadsheet page that sums up Sunday, 22 November 2026: the COP31 talks in
Antalya nearing a deal at dawn, a magnitude 6.8 quake in central Peru, Iranian
strikes on US bases in Bahrain, the burning of the Sparta II in the Gulf of
Finland, and 31 more verified stories from every region — 35 stories in all,
each with a headline, a one-line deck, and a "22 NOV" tag.

## How it is made

`main.py` is pure Python standard library. It draws the whole 1024x1024 page
from data embedded in the file: a hand-defined 5x7 bitmap font, simplified
continent polygons in longitude/latitude, the 35 stories, a numbered world
map with 12 city pins, and three vector illustration panels (the COP31 hall
at dawn, the Peru quake, the burning tanker). No external images, no network,
no dependencies. The page is verified by re-running the program twice and
comparing SHA-256 hashes of the output.

## Run it

```sh
python3 main.py
```

This writes `output/entry.png` (1024x1024). Set `MAKEFUN_OUTPUT_DIR` to choose
a different output directory. Running it twice produces byte-identical PNGs.

## Sources

Reuters, BBC, AP, CNN, Al Jazeera — see the sources line at the foot of the page.

## Event

[news-image-20261122 on make.fun](https://make.fun/bounty/news-image-20261122)
