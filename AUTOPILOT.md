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

- Images: add 3 to 5 real stills from `site/assets` (the work page lists which file is which project, by alt text) with `![caption](/assets/file.jpg)` on their own line. Never use stock or generated images, never caption a still with a client it does not belong to.
- Internal links: add the new slug to `NEXT` (2 articles it should point to) and to the matching `RELATED` lists in `tools/inject.py`, and add it to `NEXT` of 1 or 2 older articles, so it gets inbound links on day one.

## 4. Improve one existing page
- Run `python3 tools/build.py` then `python3 tools/audit.py`.
- Pick ONE issue from the audit (most valuable first: thin articles under 600 words, missing inbound links, long titles or descriptions) and fix it. For a thin article, expand it with genuinely useful sections. For inbound links, add a natural sentence with a link in a related article.

## 5. Build, check, publish
- `python3 tools/build.py` and `python3 tools/audit.py` again. The new article must have no issues.
- Quick sanity: `python3 -c "import xml.etree.ElementTree as E;E.parse('site/sitemap.xml')"` must pass, and `site/journal-<slug>.html` must exist.
- Mark the topic row `done (YYYY-MM-DD)` in `content/topics.md`.
- Commit with a message like `Article: <title>` and push to `main` (the repo is the backup and history; Netlify is NOT linked to it).
- Build the deploy zip: `python3 tools/make_zip.py /mnt/user-data/outputs`. It must be under 29 MB. If it is bigger, re-encode the largest files in `tools/lite/videos` with ffmpeg (same size 640x640, lower bitrate, no audio), commit them, and rebuild.
- Send the zip to Bilawal with SendUserFile (status proactive). He drags it onto Netlify > Deploys himself. That is the only way the site goes live.

## 6. Report
- Write `reports/YYYY-MM-DD.md` with: what was published (title, URL, target phrase, word count), what the top competing results cover and how ours differs, the improvement made, the remaining audit issues, live checks (WebFetch the live sitemap and note whether the previous run's article is live, which tells you if Bilawal deployed the last zip), and the next 3 topics.
- Commit and push the report.
- Email the report to mediavibescape@gmail.com with the Gmail connector, subject `Vibescape SEO report YYYY-MM-DD: <article title>`. Short, scannable, Roman Urdu and English mix is fine. Put this at the very top: "Naya deploy zip tayyar hai. Is run ka session kholo, zip download karo, Netlify > Deploys pe drag karo." plus this session's link if you know it.
- If any step failed (push refused, build error), still send the email and say exactly what failed and what Bilawal needs to do.
