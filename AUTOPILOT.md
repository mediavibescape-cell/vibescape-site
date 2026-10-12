# SEO autopilot: what each scheduled run does

Runs Monday, Wednesday and Friday. One run = one new article + one improvement + one report.
Work in this repo. Never touch site/assets/videos or anything outside the steps below.

## 1. Pick the topic
- Open `content/topics.md` and take the first row with status `todo`.
- If none are left, add 6 new rows first (same format, mix of audiences, each linked to a money page), then take the first.

## 2. Research before writing
- Search the target phrase (WebSearch, standard mode). Open the top 3 to 5 results with WebFetch.
- Note what they cover, what they miss, how long they are, and what a buyer would still want to know.
- Never copy text. Never invent statistics, prices, client names or results. If a number is needed, either cite a source you opened (link it) or describe it qualitatively.

## 3. Write the article
- Create `content/articles/YYYY-MM-DD-slug.md` using the front matter format in `tools/articles.py`.
- Title 40 to 60 characters, includes the target phrase or a close variant. Excerpt 120 to 155 characters.
- 900 to 1400 words. Clear `## ` sections, at least one `- ` list, practical and specific.
- Voice: Vibescape (sharp, plain English, one dry line of humour at most, Roman Urdu only as a rare single line). No dashes used as punctuation, no em dashes. Avoid AI filler phrases.
- Ground it in what Vibescape actually does: films for furniture, beauty, food and footwear brands, branding, Meta and Google ads, Shopify and custom sites, web apps, the Desk client portal. Real client names that already appear on the site may be mentioned as examples of categories, never with invented results.
- Link to the pages in the topic's "Link to" column and to 1 or 2 related articles. End with a short call to action linking `/contact` or the matching landing page.
- Set `keyword:` to the target phrase.

## 4. Improve one existing page
- Run `python3 tools/build.py` then `python3 tools/audit.py`.
- Pick ONE issue from the audit (most valuable first: thin articles under 600 words, missing inbound links, long titles or descriptions) and fix it. For a thin article, expand it with genuinely useful sections. For inbound links, add a natural sentence with a link in a related article.

## 5. Build, check, publish
- `python3 tools/build.py` and `python3 tools/audit.py` again. The new article must have no issues.
- Quick sanity: `python3 -c "import xml.etree.ElementTree as E;E.parse('site/sitemap.xml')"` must pass, and `site/journal-<slug>.html` must exist.
- Mark the topic row `done (YYYY-MM-DD)` in `content/topics.md`.
- Commit with a message like `Article: <title>` and push to `main`. Netlify deploys automatically from `main`.

## 6. Report
- Write `reports/YYYY-MM-DD.md` with: what was published (title, URL, target phrase, word count), what the top competing results cover and how ours differs, the improvement made, the remaining audit issues, live checks (open https://vibescapemedia.com/sitemap.xml and the new article URL with WebFetch a few minutes after pushing and note whether they are live), and the next 3 topics.
- Commit and push the report.
- Email the report to mediavibescape@gmail.com with the Gmail connector, subject `Vibescape SEO report YYYY-MM-DD: <article title>`. Short, scannable, Roman Urdu and English mix is fine.
- If any step failed (push refused, build error), still send the email and say exactly what failed and what Bilawal needs to do.
