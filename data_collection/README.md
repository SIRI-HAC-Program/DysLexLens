
# Data Collection

Collects posts and comments from a curated list of subreddits via the Arctic Shift archive, deduplicates them, and saves one CSV per subreddit. Downstream notebooks combine, flag, and filter this raw output.

---

## Data source

Public Reddit posts and comments, retrieved from the **Arctic Shift** archive (not scraped directly from Reddit). Subreddits to collect are listed in `input_csv` (`ID`, `SUBREDDIT`, `SRC`, `DES`). The curated list scopes the dataset to topics relevant to the research.

---

## Collection method / API

**API:** [Arctic Shift](https://arctic-shift.photon-reddit.com/) — public Reddit archive. Endpoints used:

- Posts: `https://arctic-shift.photon-reddit.com/api/posts/search`
- Comments: `https://arctic-shift.photon-reddit.com/api/comments/search`

**Per subreddit:**

1. **Fetch posts** — paginated GETs filtered by `subreddit`; pagination uses `created_utc` of the last item as the `after` cursor. Stops on short or empty page.
2. **Fetch comments per post** — paginated GETs filtered by `link_id = t3_<post_id>`, same cursor scheme.
3. **Compute comment depth** — walk `parent_id`: `t3_` → depth 0; `t1_` → parent depth + 1. Memoized in `depth_cache`.

**Request settings** (from `config.yaml`): page `limit` 100, request `timeout` 100s, `DELAY` 2s between requests, browser User-Agent.

---

## Filtering process

- **Subreddit-level:** only subreddits in `input_csv` are queried.
- **Field-level:** only fields needed for analysis are kept (see schema); other API fields discarded.
- **Skipped rows:** items with missing IDs.
- **No keyword filtering at this stage** — that happens downstream.

---

## Ethical considerations

- **Public data only.** No private messages, private subreddits, or authenticated endpoints.
- **Identifiers.** Usernames are retained as published. Pseudonymise or remove before any downstream sharing.
- **Quotation.** Direct quotes can re-identify users via search engines even with usernames removed; paraphrase or aggregate.
- **Deleted content.** `[deleted]` indicates removal by the user — exclude from verbatim use.
- **Rate limiting.** 2-second delay between requests.
- **Vulnerable communities.** Subreddits on health, disability, or other sensitive topics warrant extra care: minimise quotation, avoid re-identifying attribute combinations, follow the project's ethics framework.
- **No redistribution of raw data.** Raw CSVs are intermediate; follow the project's data-handling plan.

---

## Data cleaning steps

1. **Schema normalisation** — posts and comments mapped to a unified schema so they share one CSV.
2. **Timestamp formatting** — `created_utc` (epoch) → `datetime` string; original kept in `timestamp_utc`.
3. **Missing authors** — default to `[deleted]`.
4. **Depth assignment** — computed and stored.
5. **Per-stream deduplication** — accumulated in dicts keyed by `reddit_id`.
6. **Final deduplication** — `drop_duplicates(subset=['reddit_id'])` as a safety net.
7. **Empty results** — subreddits returning nothing are skipped with `False` status in the report; no empty CSV is written.
8. **Remove no meaning words** - word length less than 3

---

## File descriptions

**Input**

| File | Purpose |
|---|---|
| `config.yaml` | HTTP settings, endpoints, paths, report path |
| `input_csv` | List of subreddits to collect |

**Code**

| File | Purpose |
|---|---|
| `arctic_fetch.py` | Main collection script |
| `utils/file.py` | `read_yaml`, `read_csv`, `write_json` |
| `utils/logger.py` | `get_logger(__name__)` |

**Output**

| File | Purpose |
|---|---|
| `{OUTPUT_DIR}/{subreddit}.csv` | One CSV per subreddit, posts and comments combined |
| `{report_config.output_file}` | JSON run report: counts, status, execution time per subreddit |

**Output CSV schema**

| Column | Type | Description |
|---|---|---|
| `kind_desc` | str | `post` or `comment` |
| `subreddit` | str | Subreddit name |
| `reddit_id` | str | Unique post or comment ID |
| `post_id` | str / null | Parent post ID (null for posts) |
| `parent_id` | str / null | `t3_...` or `t1_...`; null for posts |
| `depth` | int / null | Comment depth (0 = top-level reply); null for posts |
| `title` | str / null | Post title; null for comments |
| `author` | str | Username or `[deleted]` |
| `timestamp_utc` | float | Unix epoch seconds |
| `datetime` | str | `YYYY-MM-DD HH:MM:SS` |
| `text` | str | `selftext` for posts, `body` for comments |
| `score` | int | Upvotes minus downvotes |
| `num_comments` | int / null | Comment count on post; null for comments |

---

## Concept dictionary

Defined in `keywords.py` as `KEYWORDS`. Each topic has **seed keywords** (canonical terms) and **related keywords** (fuzzy variants — misspellings, spacing variants, near-neighbours surfaced during keyword expansion).

Five topics:

| Topic | Role | Seed examples | Related (fuzzy) examples |
|---|---|---|---|
| `dyslexia` | Population anchor | `dyslexia`, `dyslexic`, `reading disability`, `phonological`, `decoding` | `dislexia`, `dyselxia`, `learning disabilities`, `reading difficulties` |
| `ai` | AI framing | `ai`, `chatgpt`, `llm`, `claude`, `gemini`, `openai` | `chat gpt`, `machines learning`, `language code` |
| `technology` | Tools (AI + assistive) | `assistive technology`, `grammarly`, `speechify`, `read&write`, `google docs` | `readwrite`, `grammrly`, `google doc`, `accessibility low` |
| `support` | Functional support | `text to speech`, `dictation`, `audiobook`, `spell checker`, `note taking` | `read loud`, `audibook`, `spell check`, `note making` |
| `perception` | Experiences | `helpful`, `accessible`, `frustrating`, `doesn't work` | `doesnt work`, `frustration`, `acessible` |

Each topic produces a boolean flag column `has_{topic}` in the downstream flagged layer. To add or remove topics, edit `KEYWORDS` in `keywords.py`.

---

## Sample posts

A small sample of filtered records is included to illustrate the shape of the data. The full corpus (raw per-subreddit CSVs and the combined/flagged/filtered datasets) is not redistributed here — please request access from **Dana** (contact email).

**Post example:**
```
kind_desc      : post
subreddit      : ChatGPT
reddit_id      : 1rf6qox
title          : Can someone please help …
text           : "<post body>"
word_count     : 87
has_dyslexia   : True
has_ai         : True
has_technology : True
```

**Top-level comment** (`depth = 0`, `parent_id` starts with `t3_`):
```
kind_desc      : comment
subreddit      : Blind
reddit_id      : o7g9nkz
post_id        : 1reyprl
parent_id      : t3_1reyprl
depth          : 0
has_dyslexia   : True
has_technology : True
```

**Nested comment** (`depth = 2`, `parent_id` starts with `t1_`):
```
kind_desc      : comment
subreddit      : specialeducation
reddit_id      : nwf88v4
parent_id      : t1_nwf7ong
depth          : 2
```

Full data can be requested to drezazadegan@swin.edu.au


---

## Running

```bash
python3 arctic_fetch.py
```

Reads `./config.yaml`, iterates subreddits in `input_csv`, writes one CSV per subreddit to `OUTPUT_DIR`, writes a JSON report to `report_config.output_file`.
