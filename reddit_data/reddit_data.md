# Dyslexia Reddit Corpus

DyslexicParents,
LearningDisabilities,
dyscalculia,
dysgraphia,
Dyslexia,
hyperlexia,
neurodiversity,
StructuredLiteracy,
OrtonGillingham,
ADHD,
ADHDwomen,
neurodivergent,
Dyspraxia,
executivedysfunction,
autism,
specialeducation,
SpedTeachers,
CollegeWithADHD,
college,
GradSchool,
studytips,
assistivetech,
Blind,
deaf,
disability,
accessibility,
ChatGPT,
artificial,
OpenAI,
AIAssistants,
productivity,
notetaking,
audiobooks,
speechrecognition,
mentalhealth,
anxiety,
selfesteem,
Parenting,
ParentingADHD,
specialneedsparenting,
careerguidance,
AskReddit,
offmychest,
self,
TIL,
explainlikeimfive,
Dyslexia_Help,
DyslexicReaders,
GiftedAndLearningDisabled,
laterdiagnosis

Subreddit no included( no data)
CollegeWithADHD,
Dyslexia_Help,
DyslexicReaders,
laterdiagnosis,
GiftedAndLearningDisabled

## Structure of datasets

Four layers, each built from the one above:

- **Raw** — `./data/arctic/{subreddit}.csv`. One file per subreddit, written by `arctic_fetch.py`. Each row is a post or comment.
- **Combined** — `data/reuse/subreddit_combined_key.csv`. All raw CSVs concatenated + four derived text columns. 23,480 rows.
- **Flagged** — `data/reuse/subreddit_combined_key_flag.csv`. Combined corpus + one boolean column per topic in `KEYWORDS`. 23,480 rows.
- **Filtered** — `df_all_{anchor_term}.csv`. Rows flagged for the anchor term AND at least one relevant term. 319 rows for `anchor_term = dyslexia`.
- **Summary** — `post_filter_summary.csv`, `keyword_mentions.csv`. Aggregations for figures.

## Meaning of columns

**Raw / Combined (13 base columns):**

| Column | Meaning |
|---|---|
| `kind_desc` | `post` or `comment` |
| `subreddit` | Subreddit name |
| `reddit_id` | Unique Reddit ID |
| `post_id` | Parent post ID (null for posts) |
| `parent_id` | `t3_<id>` for top-level replies, `t1_<id>` for nested replies |
| `depth` | Comment depth (0 = top-level reply); null for posts |
| `title` | Post title (null for comments) |
| `author` | Username or `[deleted]` |
| `timestamp_utc` | Unix epoch seconds |
| `datetime` | `YYYY-MM-DD HH:MM:SS` |
| `text` | `selftext` for posts, `body` for comments |
| `score` | Upvotes minus downvotes |
| `num_comments` | Comment count (null for comments) |

**Derived (added in Combined layer):**

| Column | How derived |
|---|---|
| `full_text` | `title` + `" "` + `text` |
| `text_cleaned` | `full_text` lowercased, URLs and punctuation removed, stopwords removed |
| `datetime` | Reparsed from `timestamp_utc` as real datetime (overrides raw string) |
| `word_count` | Token count of `text_cleaned` |

**Flags (added in Flagged layer):** `has_dyslexia`, `has_ai`, `has_technology`, `has_support`, `has_perception` — `True` if any keyword for that topic matches `full_text` as a whole word.

## Processed vs raw data

| | Raw | Combined | Flagged | Filtered |
|---|---|---|---|---|
| Source | Arctic Shift API | Concat of raw CSVs | Combined + regex flags | Flagged + filter |
| Adds columns | — | 4 text features | 5 `has_<topic>` flags | none |
| Drops rows | — | `word_count < 3` | — | fails `anchor & any(relevant)` |
| Rows | varies | 23,480 | 23,480 | 319 |
| Columns | 13 | 17 | 22 | 22 |

The raw `datetime` string is *replaced* in the combined layer by a parsed `datetime64`. To join combined back to raw, use `reddit_id`, not `datetime`.

## Naming conventions

| Pattern | Used for |
|---|---|
| `{subreddit}.csv` | Raw per-subreddit dump (e.g. `Dyslexia.csv`) |
| `subreddit_combined_key.csv` | Combined corpus |
| `subreddit_combined_key_flag.csv` | Combined + flags |
| `df_all_{anchor_term}.csv` | Filtered subset for one anchor (e.g. `df_all_dyslexia.csv`) |
| `has_{topic}` | Boolean flag column from `KEYWORDS` |
| `{name}_summary.csv` / `{name}_mentions.csv` | Aggregations |
| `parent_id` prefix | `t3_` = post-level parent, `t1_` = comment-level parent |
| Subreddit casing | Preserved from Reddit (`Dyslexia`, `dyscalculia`, `ParentingADHD`) |
| Missing author | Literal `[deleted]` |

## Example records

**Post:**
```
kind_desc      : post
subreddit      : ChatGPT
reddit_id      : 1rf6qox
parent_id      : NaN
depth          : NaN
title          : Can someone please help …
text           : "<post body>"
word_count     : 87
has_dyslexia   : True
has_ai         : True
has_technology : True
```

**Top-level comment** (`depth = 0`, `parent_id` starts with `t3_` → reply to the post):
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

**Nested comment** (`depth = 2`, `parent_id` starts with `t1_` → reply to another comment):
```
kind_desc      : comment
subreddit      : specialeducation
reddit_id      : nwf88v4
parent_id      : t1_nwf7ong
depth          : 2
```