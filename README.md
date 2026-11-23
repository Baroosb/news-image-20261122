# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Baroosb/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Baroosb/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

One page that sums up Sunday 22 November 2026: a drawn broadsheet of the day's world news — COP31 ending in Antalya with no deal at all, Iran's overnight strikes on US bases in Bahrain, RSF drones hitting Khartoum and a UN building, and 34 more stories across seven regions — with a stat strip, a region tally, a dotted world map with numbered pins, an "Also on Sunday" index of 24 more stories, and a date check that keeps other days' news (Friday's Bayelsa boat sinking, Saturday's Sparta II ship fire, the UK–EU deal) off the page. Every story was fact-audited against dated original reporting before it was drawn: STORIES.md is the frozen story set the page was built from, and AUDIT.md is the audit trail behind it. build.py renders the whole page programmatically with Pillow at 2048×2048 (kept as entry-master.png) and downscales it to the 1024×1024 entry.png; main.py copies entry.png to /output/entry.png, byte-identical on every run. Regenerate the image with `python3 build.py` (needs Pillow and the Noto Serif / Noto Sans fonts; DejaVu is the fallback).

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/output python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=5hnf181h&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
