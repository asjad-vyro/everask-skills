# arXiv query syntax and categories

Use this with `search_arxiv.py --raw '<query>'` when the plain options (topic words, `--phrase`, `--title`, `--author`, `--category`, `--since`) cannot say what the user wants. Dates are better done with `--since` and `--until`: the script adds the date range to a raw query for you.

## Field prefixes

| Prefix | Searches | Example |
|--------|----------|---------|
| `all:` | every field (the default) | `all:transformer` |
| `ti:` | title | `ti:"chain of thought"` |
| `abs:` | abstract | `abs:"reinforcement learning"` |
| `au:` | author | `au:hinton` |
| `cat:` | category | `cat:cs.LG` |
| `co:` | the authors' comment (page count, "accepted at ...") | `co:NeurIPS` |
| `jr:` | journal reference | `jr:Nature` |

## Operators

- `AND`, `OR`, `ANDNOT` (write them in capitals), parentheses to group, double quotes for an exact phrase.
- Words in the title only, newest first:
  `--raw 'ti:"retrieval augmented generation"' --sort date`
- Exclude a subtopic:
  `--raw 'all:"language model" ANDNOT all:vision'`
- Two phrasings of one idea:
  `--raw '(abs:"diffusion model" OR abs:"score-based generative") AND cat:cs.CV'`
- Author in a category:
  `--raw 'au:hinton AND cat:cs.LG'`
- A paper the authors say is accepted somewhere:
  `--raw 'co:accepted AND co:ICLR AND all:"reward model"' --since 1y`

If a raw query returns nothing, remove one condition at a time.

## Common categories

| Category | Field |
|----------|-------|
| `cs.AI` | Artificial Intelligence |
| `cs.CL` | Computation and Language (NLP) |
| `cs.CV` | Computer Vision and Pattern Recognition |
| `cs.LG` | Machine Learning |
| `cs.IR` | Information Retrieval |
| `cs.RO` | Robotics |
| `cs.CR` | Cryptography and Security |
| `cs.SE` | Software Engineering |
| `cs.HC` | Human-Computer Interaction |
| `stat.ML` | Machine Learning (Statistics) |
| `eess.AS` | Audio and Speech Processing |
| `eess.IV` | Image and Video Processing |
| `math.OC` | Optimization and Control |
| `quant-ph` | Quantum Physics |
| `q-bio.NC` | Neurons and Cognition |
| `econ.GN` | General Economics |

The full list is at https://arxiv.org/category_taxonomy. `--category` matches a paper's main category and its cross-lists.

## IDs and versions

- New IDs look like `2402.03300`; older ones look like `hep-th/0601001`. The script also accepts `arXiv:2402.03300` and abs or pdf links.
- `https://arxiv.org/abs/<ID>` always shows the latest version. Add `v2` for that exact version. The script prints the version it received (for example `1706.03762v7`); keep that suffix when the user wants a citation.
- If the PDF cannot be read, newer papers often have an HTML version at `https://arxiv.org/html/<ID>`.
- A withdrawn paper has a withdrawal notice in its abstract or comment, and the script prints a WARNING line for it.
