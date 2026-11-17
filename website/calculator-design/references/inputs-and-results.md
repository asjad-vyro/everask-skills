# Inputs and results

## Inputs
- Necessary: if an input does not change the output, drop it. A form with many fields and a short formula reads as sales qualification dressed as a calculator.
- Easy: use the visitor's likely units (per month, per seat), show an example in the placeholder, and add help text saying where to find the number.
- Types: number for money and counts; slider for estimates in a range (adoption, conversion); dropdown for fixed categories; toggle for yes/no or scenario A/B; free text almost never.
- Defaults: a default is a claim. Use a sourced value, the user's own figure, or leave the field empty with a placeholder. Mark every default the maker supplied as an assumption the visitor can edit. Stale defaults erode trust, so show the date they were last checked.
- Progressive disclosure: put the three or four inputs that drive most of the result first; tuck refinements under "Adjust assumptions".
- Validate: reject negatives and non-numbers with a plain message, and show nothing rather than NaN or Infinity.

## Results
- Specific: a number with units ("per year", "months"), not "significant savings" or "up to".
- Contextual: compare with the visitor's current state so the number means something.
- Actionable: a next step such as "share this with your finance lead" or "download the report".
- Breakdown: the parts must add up to the headline; if they do not, the page has a bug.
- No false precision: round to what the inputs support and say it is an estimate.
- Visible at once: result above the marketing, updated live, inputs kept on screen.
- Shareable: the result must carry its inputs and method, so a colleague can read it cold.
- Ranges: when inputs are uncertain, show a low and high case instead of one confident figure.
