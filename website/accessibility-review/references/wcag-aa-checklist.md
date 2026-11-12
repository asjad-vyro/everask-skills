# WCAG 2.1 A and AA checklist

Use this to cite the right criterion number and name, to decide what the code or design can prove, and to fill the "could not be confirmed" section of the report.

"From code" says whether reading markup and CSS can settle the criterion: Yes, Partly (only signs of a problem show up) or No (a person has to use the page). "Calculate" means work out the ratio with the script.

This audit covers Levels A and AA. Never report a Level AAA criterion as a failure.

## Perceivable

| Criterion | Level | Look for | From code |
|---|---|---|---|
| 1.1.1 Non-text Content | A | Informative images, icons, image links and image buttons have a text alternative; decorative images have alt=""; charts and diagrams have a longer description | Yes for presence; a person judges quality |
| 1.2.1 Audio-only and Video-only (Prerecorded) | A | Transcript for audio-only; transcript or audio track for silent video | Partly |
| 1.2.2 Captions (Prerecorded) | A | Captions on video with speech (a track element or burned in) | Partly |
| 1.2.3 Audio Description or Media Alternative (Prerecorded) | A | Audio description or a full text alternative for video | Partly |
| 1.2.4 Captions (Live) | AA | Live captions for live video with audio | No |
| 1.2.5 Audio Description (Prerecorded) | AA | Audio description track for prerecorded video | No |
| 1.3.1 Info and Relationships | A | Real headings, lists and tables with th; labels tied to fields; fieldset and legend for groups; landmarks; structure not faked with styled divs | Yes |
| 1.3.2 Meaningful Sequence | A | DOM order matches reading order; CSS order, float or absolute positioning does not scramble it | Partly |
| 1.3.3 Sensory Characteristics | A | Instructions do not rely only on shape, colour, size, position or sound ("the green button", "the box on the right") | Yes (text) |
| 1.3.4 Orientation | AA | Content is not locked to portrait or landscape | Partly |
| 1.3.5 Identify Input Purpose | AA | Name, email, phone, address, card and similar fields carry the right autocomplete value | Yes |
| 1.4.1 Use of Color | A | Colour is not the only way to show errors, required fields, links inside text, chart series or state | Partly |
| 1.4.2 Audio Control | A | Audio that plays by itself for more than 3 seconds can be paused, stopped or turned down | Yes (autoplay) |
| 1.4.3 Contrast (Minimum) | AA | Text 4.5:1; large text (24px, or 18.66px bold) 3:1. Includes placeholder text, text in buttons and text over images. Logos, disabled controls and pure decoration are exempt | Calculate |
| 1.4.4 Resize Text | AA | Text can grow to 200% without loss; the viewport tag does not block zoom; no fixed heights that clip text | Partly |
| 1.4.5 Images of Text | AA | Real text, not pictures of text (logos excepted) | Partly |
| 1.4.10 Reflow | AA | At 320 CSS px wide (400% zoom) no sideways scrolling for normal content (data tables, maps and editors excepted) | No |
| 1.4.11 Non-text Contrast | AA | Input borders, checkbox and radio outlines, meaningful icons, chart elements and the focus ring reach 3:1 against neighbouring colours | Calculate |
| 1.4.12 Text Spacing | AA | Nothing is clipped or overlaps at line height 1.5, paragraph spacing 2x, letter spacing 0.12em, word spacing 0.16em | No |
| 1.4.13 Content on Hover or Focus | AA | Tooltips and pop-ups can be dismissed (Esc), hovered over, and stay until dismissed | No |

## Operable

| Criterion | Level | Look for | From code |
|---|---|---|---|
| 2.1.1 Keyboard | A | Everything works with the keyboard alone: no click-only div or span, no hover-only menus, custom widgets handle keys | Partly; test by hand |
| 2.1.2 No Keyboard Trap | A | Focus can always leave modals, menus, embedded players and editors | No |
| 2.1.4 Character Key Shortcuts | A | Single-key shortcuts can be turned off or remapped, or work only while the control has focus | Partly |
| 2.2.1 Timing Adjustable | A | Session timeouts, timed redirects (meta refresh) and timed forms can be turned off, adjusted or extended | Partly |
| 2.2.2 Pause, Stop, Hide | A | Carousels, marquees, autoplay video and animation lasting over 5 seconds have a pause control | Partly |
| 2.3.1 Three Flashes or Below Threshold | A | Nothing flashes more than 3 times a second | No |
| 2.4.1 Bypass Blocks | A | A skip link or a main landmark lets users jump past repeated navigation | Yes |
| 2.4.2 Page Titled | A | Each page has a unique, descriptive title | Yes |
| 2.4.3 Focus Order | A | Tab order follows the visual and logical order; no positive tabindex; modals move focus in and give it back | Partly |
| 2.4.4 Link Purpose (In Context) | A | Link text, or its surrounding context, says where it goes; no bare "click here"; image links have alt | Yes |
| 2.4.5 Multiple Ways | AA | More than one way to find a page (navigation plus search or a sitemap) | Partly |
| 2.4.6 Headings and Labels | AA | Headings and labels describe their topic or purpose | Yes |
| 2.4.7 Focus Visible | AA | Keyboard focus is clearly visible; outline:none with no replacement fails | Partly |
| 2.5.1 Pointer Gestures | A | Pinch, swipe, multi-finger and path gestures have a single-tap alternative | Partly |
| 2.5.2 Pointer Cancellation | A | Actions run on release (click), not on press (mousedown), and can be aborted | Partly |
| 2.5.3 Label in Name | A | A control's accessible name contains its visible label text | Yes |
| 2.5.4 Motion Actuation | A | Shake or tilt features have a button alternative and can be switched off | Partly |

## Understandable

| Criterion | Level | Look for | From code |
|---|---|---|---|
| 3.1.1 Language of Page | A | html element has a valid lang attribute | Yes |
| 3.1.2 Language of Parts | AA | Passages in another language carry their own lang | Partly |
| 3.2.1 On Focus | A | Focusing a control does not change the page or open something unexpected | Partly |
| 3.2.2 On Input | A | Changing a field does not submit or navigate unless the user was warned (a select that navigates on change fails) | Yes |
| 3.2.3 Consistent Navigation | AA | Repeated navigation keeps the same order on every page | No (needs several pages) |
| 3.2.4 Consistent Identification | AA | The same function has the same name and icon everywhere | No |
| 3.3.1 Error Identification | A | Errors are described in text and the field in error is identified, not shown by colour alone | Partly |
| 3.3.2 Labels or Instructions | A | Every input has a visible label, plus any needed format or required hint | Yes |
| 3.3.3 Error Suggestion | AA | Error messages say how to fix the problem | Partly |
| 3.3.4 Error Prevention (Legal, Financial, Data) | AA | Submissions with legal, financial or data consequences can be reviewed, corrected or reversed | Partly |

## Robust

| Criterion | Level | Look for | From code |
|---|---|---|---|
| 4.1.1 Parsing | A | In WCAG 2.1 only (removed in 2.2): duplicate ids and broken nesting. Report duplicate ids only when they break a label or ARIA reference | Yes |
| 4.1.2 Name, Role, Value | A | Every control exposes a name, role and state; native elements first; aria-expanded, aria-checked and similar kept current; no aria-hidden on focusable elements | Names and roles yes; live behaviour no |
| 4.1.3 Status Messages | AA | Result counts, success and error messages are announced without moving focus (role="status", role="alert", aria-live) | Partly |

## Not an AA requirement

- 2.5.5 Target Size (Enhanced) is Level AAA: 44 by 44 CSS px. Report small targets as Minor, "best practice", never as an AA failure.
- 1.4.6 Contrast (Enhanced) is AAA (7:1). Do not require it.
- WCAG 2.2 AA does add 2.5.8 Target Size (Minimum): at least 24 by 24 CSS px, with spacing and inline exceptions.

## WCAG 2.2 additions

Only if the user asks for WCAG 2.2, and then say "Standard: WCAG 2.2 AA". Also check:

- 2.4.11 Focus Not Obscured (Minimum), AA: a focused control is not completely hidden by a sticky header, cookie banner or chat widget.
- 2.5.7 Dragging Movements, AA: anything done by dragging can also be done with a single tap or click.
- 2.5.8 Target Size (Minimum), AA: targets are at least 24 by 24 CSS px, or have enough space around them.
- 3.2.6 Consistent Help, A: help links or contact options sit in the same place on every page.
- 3.3.7 Redundant Entry, A: do not make users retype information they already gave in the same process.
- 3.3.8 Accessible Authentication (Minimum), AA: log-in does not depend on remembering or retyping something without an alternative; allow paste and password managers.
- 4.1.1 Parsing no longer applies.

## Reviewing a design (screenshot, Figma frame or description)

Work from what is visible or stated, and say which it was.

1. Text contrast: take each text colour and its background (hex values given or read from Figma) and run the script. From a picture alone, estimate the colours and write "estimated" next to the ratio.
2. Non-text contrast: input borders, meaningful icons, chart elements, focus ring and selected states at 3:1 against their neighbours.
3. Colour as the only cue: errors, status, required fields, links in text and chart series need a second cue such as an icon, text, pattern or underline.
4. Labels: every field has a visible label that stays on screen; placeholder-only fields are a finding.
5. States: the design shows a visible focus state, and disabled, error and selected states can be told apart.
6. Targets: interactive targets under 24 CSS px (WCAG 2.2 AA) or 44 CSS px (best practice) are Minor findings.
7. Text: no important text inside images; the layout still works with larger text; very small body text is a usability note (WCAG sets no minimum size).
8. Hand-off gaps: list what the spec lacks, such as heading outline, landmarks, reading order, alt text for each image, captions for video, names for icon-only buttons.
9. Motion: animation, autoplay and carousels have a stop control and respect the reduced-motion setting.

## Fix patterns

Use these shapes in the "Fix" line, adapted to the user's own markup.

- Image: `<img src="team.jpg" alt="Three engineers reviewing a dashboard">`. Decorative: `alt=""`. Icon link: `<a href="/cart"><img src="cart.svg" alt="Cart"></a>`. Icon button: `<button type="button" aria-label="Close"><svg aria-hidden="true">...</svg></button>`.
- Field: `<label for="email">Email address</label><input id="email" type="email" name="email" autocomplete="email">`. Hint or error: `aria-describedby="email-hint"`; invalid state: `aria-invalid="true"`. Keep the label visible; a placeholder is not a label.
- Div used as a button: `<button type="button" onclick="submitForm()">Start my subscription</button>`. Only if a div cannot be avoided: `role="button" tabindex="0"` plus an Enter and Space key handler.
- Language: `<html lang="en">`.
- Focus: `:focus-visible { outline: 3px solid #1a5fb4; outline-offset: 2px; }`. Never remove the outline without a replacement.
- Skip link: `<a class="skip-link" href="#main">Skip to main content</a>` and `<main id="main">`.
- Status message: `<div role="status">3 results found</div>`; errors: `role="alert"`.
- Modal: use `<dialog>` with showModal(), or move focus in on open, keep it inside, close on Esc and return focus to the trigger.
- Select that navigates on change: add a Go button and remove the onchange navigation.
- Low contrast: keep the hue and darken the text (or lighten the background) until the script says the pair passes, and give the new hex with its ratio. On white, #767676 is about the lightest grey that passes (4.54:1); check any other suggestion with the script before writing it.
