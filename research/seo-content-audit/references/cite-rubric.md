# Citation-readiness checklist (30 items)

Four areas: Clear answer, Include primary stats, Timestamp freshness and Entity authority (CITE). The checklist describes pages whose passages are easy for an AI answer engine to lift and attribute. It is a working checklist: a high score does not guarantee a citation, and a low one does not rule it out.

## Marking rules

Use the same marks and rules as the E-E-A-T checklist: ✓ (met), ~ (partly met), ✗ (not met) or ? (can't tell), with evidence for each. **[page]** items depend on the published page (displayed dates, structured data): judge them from the fetched page, and mark them ? for pasted text unless the text shows them. Use ? too when an item cannot apply (for example the year in the title of an evergreen piece).

- Area score = (✓ + 0.5 × ~) ÷ (items marked ✓, ~ or ✗) × 100, rounded. The four counts must add up to the number of items in the area (8, 8, 7, 7).
- If fewer than half of an area's items are marked ✓, ~ or ✗, report it as "not scored" and leave it out of the composite.
- CITE composite = the average of the scored areas.

## Auto-fail checks (3)

Any one triggered means NO PUBLISH. Report each one as present or missing (or triggered or not), with evidence.

1. **No clear answer in the first 300 words.** AI answer engines read the early paragraphs; if the answer is not there, the page is unlikely to be cited. Quote the sentence that answers the target keyword, or say there is none.
2. **No date on time-sensitive content.** "Best X 2024" published in 2026 with no last-updated indicator gets passed over. A date written into the text counts as well as a displayed one. On a pasted draft the CMS will usually add the publish date, so trigger this only when the time-sensitive claims themselves carry no dates in the text (for example "current pricing" with no "as of"). Not time-sensitive: not applicable.
3. **No entity disambiguation for proper-noun topics.** A page about "Apple" that does not say whether it means the company or the fruit loses to clearer pages. Applies only when the topic is a brand, product, person or place that could be confused with another. Otherwise not applicable.

## 1. Clear answer (8 items)

The answer is findable, fast and direct.

1. The primary question or topic of the piece is answered in the first 200 words.
2. The first paragraph is 60 words or fewer and stands alone as a TL;DR.
3. The answer is stated in declarative sentences ("X is...", not "many people wonder whether X might be...").
4. Headings preview the answer ("How long does X take?" followed by "X takes 4 to 6 weeks", not "Let's explore the timeline").
5. Lists, tables or step blocks present the answer in scannable form where that fits.
6. Numbers, dates and named entities appear in the answer: specifics an AI answer can extract.
7. The answer comes first and the supporting context after it, not the other way round.
8. No clickbait deferral ("read on to find out..."). The answer is given, then explained.

## 2. Include primary stats (8 items)

The piece references concrete data, with attribution.

1. At least one statistic, percentage or number is cited in the first half.
2. Sources are linked inline next to the stat, not in a footnote pile at the end.
3. Sources are primary (the original study, government data, the company's own report), not aggregator sites.
4. The date of the data is stated near the stat ("per the 2025 X report").
5. Multiple stats triangulate the same claim where possible (one source, then a corroborating one).
6. The methodology of cited data is briefly given (sample size, population, time window).
7. Original data the author generated (survey, analysis, A/B test) is presented with its methodology.
8. Where data is contested, the piece says so and does not cherry-pick.

## 3. Timestamp freshness (7 items)

The reader, and an AI answer engine, can tell when the piece is from.

1. Original publish date visible on the page. **[page]**
2. Last-updated date visible, and different from the publish date if the piece was updated. **[page]**
3. The year appears in the title, URL or first H1 if the topic is time-sensitive.
4. Schema.org `datePublished` and `dateModified` are populated correctly (ISO 8601). **[page]** Extracted text rarely shows structured data, so this is usually ?.
5. Time-sensitive claims (for example "current pricing", "best as of") carry explicit dates.
6. An updates log is visible if the piece was substantively revised. **[page]**
7. Old data points (more than 2 years old, judged against today's date) are flagged or replaced.

## 4. Entity authority (7 items)

Brands, products, people and places are named clearly and authoritatively.

1. The primary entity (brand, product, person, place) is named with its full identifier at first mention ("Apple Inc.", not just "Apple").
2. Disambiguation (a Wikipedia or Wikidata reference, or clear context) tells the reader which entity is meant.
3. Schema.org markup includes the entity (`Organization`, `Person`, `Product`, `Place`) with `sameAs` links to authoritative profiles. **[page]** Usually ?.
4. The author byline links to a profile that establishes the author's expertise on this entity.
5. The brand name is consistent across the piece, with no informal abbreviations that confuse an AI reader.
6. Related entities are introduced with their own brief disambiguation, especially in B2B or niche topics.
7. Citations include canonical references (a DOI for papers, official URLs for products).

## Calibration

- For news content, Timestamp items 1, 2, 3 and 5 should all be ✓: undated news is dead.
- For evergreen topics, Timestamp items 5 to 7 confirm the freshness window; do not chase dates.
- For brand content, where being cited matters most, Entity authority should be 80% or more.
- For commercial content, Include primary stats is what lifts a piece from marketing fluff to decision-grade: put fixes there.
