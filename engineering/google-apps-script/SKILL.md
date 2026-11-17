---
name: Google Sheets Automation Script Writer
description: >
  Writes a ready-to-paste Google Apps Script for a Google Sheet, with install and authorise steps.
  Use it for "write an Apps Script", "add a custom menu to my Sheet", "email when a cell changes", "export to PDF from Sheets", "pull an API into my sheet every morning", "script this in Sheets".
---

# Google Sheets Automation Script Writer

A good result is one complete script the user can paste into Extensions > Apps Script and run, plus short setup steps, the limits that matter for this job, and a note of what you assumed. You cannot run it against their Google account, so say it is untested against their sheet and tell them to try it on a copy.

## Step 1: Decide the design from the request

Do not ask questions. Where the request leaves something open (sheet name, column letters, recipient, schedule), pick a sensible default, put it in a `CONFIG` block at the top of the script, and list it under "Assumptions" in the reply. Never invent the user's real emails, URLs, API keys, sheet names or column layout: use obvious placeholders such as `'Sheet1'` or `'REPLACE_WITH_RECIPIENT_EMAIL'` and mark them as things to change.

Choose the trigger by what the script must do:

- Needs email, URL fetch, other files or dialogs after an edit: use an installable trigger created with `ScriptApp.newTrigger()` plus a one-time `createTriggers()` function. A plain `onEdit(e)` is a simple trigger and cannot send mail or fetch URLs.
- Only light reactions (timestamp, formatting): a simple `onEdit(e)` is enough.
- Runs on a schedule: a time-driven trigger.
- Runs on a Google Form response: an installable `onFormSubmit` trigger.
- User clicks to run: a custom menu from `onOpen()`.

## Step 2: Write the script

1. Read `references/patterns.md` once if the job uses a dialog, sidebar, progress spinner, PDF export, API call, batch email, validation dropdown, archive or duplicate recipe. Skip it for a very simple script.
2. Start with a header comment (name, what it does, install line), then `// --- CONFIGURATION ---` constants, then `onOpen()` if there is a menu, then the functions.
3. Follow the rules below.
4. Keep it to what was asked. Do not add menus, dialogs or extras the user did not ask for.

### Rules that prevent silent failures

- A function whose name ends in `_` is private: `google.script.run` and menu items cannot call it, and nothing reports an error. Name anything a dialog, sidebar or menu calls without a trailing underscore.
- Read and write in bulk with `getValues()` / `setValues()`. Never read cell by cell in a loop.
- Call `SpreadsheetApp.flush()` before returning from functions that change the sheet, especially ones called from dialogs.
- Edit triggers: check `e.range`, the sheet name and the column first and return early. Use `e.range.getRow()` and `e.value` rather than the active cell.
- The column check must test both ends of the edited range, so it passes only when the range actually includes the target column: `if (e.range.getColumn() > CONFIG.STATUS_COL || e.range.getLastColumn() < CONFIG.STATUS_COL) return;`. For single-cell handling, use `if (e.range.getColumn() !== CONFIG.STATUS_COL) return;`. Checking only `getLastColumn()` is not enough. Edits to any other column, including the script's own marker column (for example Sent or Notified), must never trigger a send. Make code comments match what the check really does.
- V8 is the only runtime. There is no `fetch` (use `UrlFetchApp.fetch`), no `setTimeout` (use `Utilities.sleep`), no `URL` or `FormData`.
- Custom cell functions (`=MY_FUNCTION()`) need the `@customfunction` JSDoc tag, run at most 30 seconds, and cannot use `MailApp`, `UrlFetchApp` or `getUi()`.
- Wrap `MailApp`, `UrlFetchApp` and other external calls in try/catch. Use `muteHttpExceptions: true` and check the response code.
- Store API keys in `PropertiesService.getScriptProperties()` (set once by the user in Project Settings > Script properties). Never put a key in the code or in the reply.
- Sending email or posting to other systems: build the script so the user chooses when it runs (menu item or a trigger they create). Where a batch send is involved, add a dry-run option or a confirmation prompt that shows how many messages will go out.
- Avoid hard-coded row numbers and sheet names outside `CONFIG`.

### Limits to mention when they apply

Quote these as commonly documented limits and tell the user to check Google's current Apps Script quotas page, because they change by account type:

- Email recipients per day: about 100 on a free Google account and about 1,500 on Google Workspace. Check `MailApp.getRemainingDailyQuota()` before a batch.
- One execution runs up to about 6 minutes; time-driven triggers can run longer on some plans. For big jobs, process in chunks and continue from a stored position with a time-driven trigger.
- Custom functions: 30 seconds.
- Use `LockService.getScriptLock()` with `tryLock` when a trigger could fire twice at once and both runs write to the sheet or send mail, so a row is not processed twice. Mark each row (for example a Status or Sent column) so a re-run skips finished rows. If `tryLock` fails, do not return silently: log it with `console.warn` including the row number, and say in Assumptions that a skipped edit is not retried automatically.

## Step 3: Check the syntax

If you wrote more than a few lines, check the script with Node in the sandbox:

1. Save the code with `write_file` to `/tmp/.scratch/google-apps-script/code.js`.
2. Run `node --check /tmp/.scratch/google-apps-script/code.js` with `terminal`.
3. Fix any syntax error and repeat. Do not try to run the script: the Google services do not exist in Node.
4. In the reply, say only that the syntax was checked, not that the script works against their sheet.

## Step 4: Write the reply

The reply itself contains the whole deliverable, in this order:

1. **What it does**: two sentences.
2. **The script**: one `javascript` code block, named `Code.gs` in the text above it. If it needs an HTML file (dialog or sidebar), either inline the HTML in the script (as in `references/patterns.md`) or add a second block named for the file.
3. **Install and authorise**:
   1. Open the Google Sheet, then Extensions > Apps Script.
   2. Delete the code in the editor, paste the script, click Save.
   3. If the script has a menu: close the tab and reload the spreadsheet. If it has triggers: pick `createTriggers` in the function dropdown and click Run once.
   4. On first run Google asks for permission. For a script that is not verified, click Advanced > Go to `<project name>` (unsafe) > Allow. Each user does this once.
4. **How to test it**: on a copy of the sheet, with the exact action to try and what should happen. Say where to look if it fails: View > Executions in the Apps Script editor. If you tell the user how to re-send or retry a row, state exactly which edit causes the send. For example: "clear F, then re-enter 'Shipped' in E". Do not suggest an action that silently re-sends.
5. **Assumptions and things to change**: the sheet and column layout you assumed, placeholders to replace, and any limit from the list above that applies.

## Hard rules

- Deliver the full code in the reply. Never say "here is the script" and leave it out.
- No invented data, addresses, keys or numbers. Placeholders are marked as placeholders.
- Do not claim the script was run against their sheet.
- Edit-trigger sends fire only when the edited range includes the target column. Check both `getColumn()` and `getLastColumn()`.
- If the request is not about Google Sheets or Workspace (Docs, Gmail, Drive, Forms, Calendar), the same method applies: choose the right service, keep the same structure and the same reply format.
