# Apps Script patterns

Adapt these to the request. Names such as `doTheWork`, `Recipients` and the column positions are placeholders: replace them and move them into `CONFIG`.

## Script structure

```javascript
/**
 * <Project name> - <what it does>
 *
 * INSTALL: Extensions > Apps Script > paste this > Save > Reload sheet
 */

// --- CONFIGURATION ---
const SHEET_NAME = 'Sheet1';

// --- MENU SETUP ---
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('My Menu')
    .addItem('Do Something', 'myFunction')
    .addSeparator()
    .addSubMenu(ui.createMenu('More Options').addItem('Option A', 'optionA'))
    .addToUi();
}
```

## Toast, alert, prompt

```javascript
SpreadsheetApp.getActiveSpreadsheet().toast('Operation complete', 'Title', 5); // seconds, -1 = until dismissed

const ui = SpreadsheetApp.getUi();
const response = ui.alert('Continue?', 'This cannot be undone.', ui.ButtonSet.YES_NO);
if (response === ui.Button.YES) { /* proceed */ }

const result = ui.prompt('Enter a value:', ui.ButtonSet.OK_CANCEL);
if (result.getSelectedButton() === ui.Button.OK) { const text = result.getResponseText(); }
```

## Modal progress dialog

For anything taking more than a few seconds. Menu function calls `showProgress`, the dialog calls the public work function, then closes itself.

```javascript
function showProgress(message, serverFn) {
  const html = HtmlService.createHtmlOutput(`
    <style>
      body { font-family: Arial, sans-serif; display: flex; flex-direction: column;
        align-items: center; justify-content: center; height: 100%; margin: 0; padding: 20px; box-sizing: border-box; }
      .spinner { width: 36px; height: 36px; border: 4px solid #e0e0e0; border-top: 4px solid #1a73e8;
        border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 16px; }
      @keyframes spin { to { transform: rotate(360deg); } }
      .done { color: #1e8e3e; } .error { color: #d93025; }
    </style>
    <div class="spinner" id="spinner"></div>
    <div id="msg">${message}</div>
    <script>
      google.script.run
        .withSuccessHandler(function(r) {
          document.getElementById('spinner').style.display = 'none';
          var m = document.getElementById('msg'); m.className = 'done'; m.innerText = 'Done. ' + (r || '');
          setTimeout(function() { google.script.host.close(); }, 1200);
        })
        .withFailureHandler(function(err) {
          document.getElementById('spinner').style.display = 'none';
          var m = document.getElementById('msg'); m.className = 'error'; m.innerText = 'Error: ' + err.message;
          setTimeout(function() { google.script.host.close(); }, 3000);
        })
        .${serverFn}();
    </script>
  `).setWidth(320).setHeight(140);
  SpreadsheetApp.getUi().showModalDialog(html, 'Working...');
}

function menuDoWork() { showProgress('Processing data...', 'doTheWork'); }

// Must be public (no trailing underscore) so the dialog can call it
function doTheWork() {
  // ... do the work ...
  SpreadsheetApp.flush();
  return 'Finished';
}
```

## Sidebar

```javascript
function showSidebar() {
  const html = HtmlService.createHtmlOutput(`
    <h3>Quick Entry</h3>
    <input id="name" placeholder="Name">
    <button onclick="submitIt()">Add</button>
    <script>
      function submitIt() {
        google.script.run.withSuccessHandler(function() { alert('Added'); })
          .addRow(document.getElementById('name').value);
      }
    </script>
  `).setTitle('Quick Entry').setWidth(300);
  SpreadsheetApp.getUi().showSidebar(html);
}

function addRow(name) { // public: called from the sidebar
  SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().appendRow([new Date(), name]);
}
```

## Triggers

Simple trigger (no authorisation, but no email, no URL fetch, no dialogs):

```javascript
function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  if (sheet.getName() !== SHEET_NAME) return;
  if (e.range.getColumn() !== 3) return;
  sheet.getRange(e.range.getRow(), 4).setValue(new Date());
}
```

Installable triggers (run `createTriggers` once by hand; guard against duplicates by deleting old ones first):

```javascript
function createTriggers() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('dailyReport').timeBased().atHour(8).everyDays(1).create();
  ScriptApp.newTrigger('onEditFull').forSpreadsheet(SpreadsheetApp.getActive()).onEdit().create();
  ScriptApp.newTrigger('onFormSubmit').forSpreadsheet(SpreadsheetApp.getActive()).onFormSubmit().create();
}
```

Installable on-edit handler that sends mail only when a status column changes, with a lock and a sent marker:

```javascript
function onEditFull(e) {
  if (!e || !e.range) return;
  const sheet = e.range.getSheet();
  if (sheet.getName() !== SHEET_NAME || e.range.getColumn() !== STATUS_COL) return;
  if (e.value !== TARGET_STATUS) return;
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) return;
  try {
    const row = e.range.getRow();
    const values = sheet.getRange(row, 1, 1, sheet.getLastColumn()).getValues()[0];
    // ... build and send the email with MailApp.sendEmail, then mark the row ...
  } finally {
    lock.releaseLock();
  }
}
```

## Email a range

```javascript
function emailRange() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = sheet.getRange('A2:E10').getDisplayValues();
  let body = '<table border="1" cellpadding="8">';
  for (const row of data) {
    if (row[0]) body += '<tr>' + row.map(c => '<td>' + c + '</td>').join('') + '</tr>';
  }
  body += '</table>';
  MailApp.sendEmail({ to: RECIPIENT, subject: 'Sheet summary', htmlBody: body });
}
```

## PDF export

The export parameters are undocumented, so keep this URL shape:

```javascript
function exportSheetAsPdf() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const url = ss.getUrl().replace(/\/edit.*$/, '')
    + '/export?exportFormat=pdf&format=pdf&size=A4&portrait=true'
    + '&fitw=true&sheetnames=false&printtitle=false&gridlines=false'
    + '&gid=' + ss.getActiveSheet().getSheetId();
  const blob = UrlFetchApp.fetch(url, {
    headers: { 'Authorization': 'Bearer ' + ScriptApp.getOAuthToken() }
  }).getBlob().setName('report.pdf');
  MailApp.sendEmail({ to: RECIPIENT, subject: 'Report PDF', body: 'Attached.', attachments: [blob] });
}
```

To export only a selected range, add `&range=A1:F20` (use the active range's `getA1Notation()`).

## External API calls

```javascript
function getApiKey() {
  return PropertiesService.getScriptProperties().getProperty('API_KEY');
}

function fetchData() {
  try {
    const response = UrlFetchApp.fetch(API_URL, {
      headers: { 'Authorization': 'Bearer ' + getApiKey() },
      muteHttpExceptions: true
    });
    if (response.getResponseCode() !== 200) throw new Error('API returned ' + response.getResponseCode());
    return JSON.parse(response.getContentText());
  } catch (e) { Logger.log('Error: ' + e.message); throw e; }
}

function postData(payload) {
  const r = UrlFetchApp.fetch(API_URL, {
    method: 'post', contentType: 'application/json',
    payload: JSON.stringify(payload), muteHttpExceptions: true });
  if (r.getResponseCode() !== 200) throw new Error('API error: ' + r.getContentText());
  return JSON.parse(r.getContentText());
}
```

Writing API results into a sheet: build a 2D array, then one `sheet.getRange(1, 1, rows.length, cols).setValues(rows)`. Clear the old range first with `clearContent()`.

## Data validation dropdowns

```javascript
const rule = SpreadsheetApp.newDataValidation()
  .requireValueInList(['Option A', 'Option B'], true)
  .setAllowInvalid(false).setHelpText('Select an option').build();
sheet.getRange('C3:C50').setDataValidation(rule);

const rule2 = SpreadsheetApp.newDataValidation()
  .requireValueInRange(ss.getSheetByName('Lookups').getRange('A1:A100')).build();
sheet.getRange('B3:B50').setDataValidation(rule2);
```

## Properties Service

`getScriptProperties()` (shared), `getUserProperties()` (per user), `getDocumentProperties()` (per spreadsheet). Use `setProperty(key, value)` and `getProperty(key)`. About 500 KB per store.

## Recipe: auto-archive completed rows

Process bottom-up so row numbers do not shift.

```javascript
function archiveCompleted() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const source = ss.getSheetByName(SOURCE_SHEET);
  const archive = ss.getSheetByName(ARCHIVE_SHEET);
  const data = source.getDataRange().getValues();
  for (let i = data.length - 1; i >= 1; i--) {
    if (data[i][STATUS_INDEX] === DONE_VALUE) { // STATUS_INDEX is 0-based
      archive.appendRow(data[i]);
      source.deleteRow(i + 1);
    }
  }
  SpreadsheetApp.flush();
}
```

## Recipe: duplicate detection

Read the column once with `getValues()`, track seen values in an object, then call `setBackground()` on both the original row and each duplicate row.

## Recipe: batch email sender

Check quota first, skip rows already marked, try/catch each send, write the status per row.

```javascript
function sendBatchEmails() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(RECIPIENT_SHEET);
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;
  const data = sheet.getRange(2, 1, lastRow - 1, 3).getValues(); // Email, Name, Status
  const pending = data.filter(r => r[0] && r[2] !== 'Sent').length;
  const remaining = MailApp.getRemainingDailyQuota();
  if (remaining < pending) {
    SpreadsheetApp.getUi().alert('Only ' + remaining + ' emails left today; ' + pending + ' are pending.');
    return;
  }
  const ui = SpreadsheetApp.getUi();
  if (ui.alert('Send ' + pending + ' emails?', ui.ButtonSet.YES_NO) !== ui.Button.YES) return;
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) { ui.alert('Another run is in progress.'); return; }
  try {
    for (let i = 0; i < data.length; i++) {
      const [email, name, status] = data[i];
      if (!email || status === 'Sent') continue;
      try {
        MailApp.sendEmail({ to: email, subject: SUBJECT, htmlBody: '<p>Hi ' + name + ',</p>' + BODY_HTML });
        sheet.getRange(i + 2, 3).setValue('Sent');
      } catch (err) { sheet.getRange(i + 2, 3).setValue('Error: ' + err.message); }
    }
  } finally { lock.releaseLock(); SpreadsheetApp.flush(); }
}
```

If the list could exceed one 6-minute run, send in chunks and let a time-driven trigger continue from the first row not marked Sent.

## Recipe: summary across tabs

Loop `ss.getSheets()` or numbered tab names with `ss.getSheetByName(tabName)`, read the summary cells from each, write one row per tab into a Summary sheet (`ss.insertSheet('Summary')` if missing), then `autoResizeColumns()` and `flush()`.

## Other APIs worth knowing

- Show or hide rows: `sheet.hideRows()`, `showRows()`.
- Formatting: `setBackground()`, `setFontWeight()`, `setBorder()`, `setNumberFormat()`, conditional formatting rules via `sheet.setConditionalFormatRules()`.
- Protection: `range.protect()`, `setUnprotectedRanges()`.
- Chat webhook: `UrlFetchApp.fetch(webhookUrl, { method: 'post', contentType: 'application/json', payload: JSON.stringify({ text: message }) })`, with the webhook URL kept in Script properties.

## Common mistakes

| Mistake | Fix |
|---|---|
| Dialog or menu cannot call a function | Remove the trailing `_` from its name |
| Slow on large data | Use `getValues()` / `setValues()` |
| Changes not visible after a dialog | `SpreadsheetApp.flush()` before returning |
| `onEdit` cannot send email | Use an installable trigger |
| Custom function times out | 30-second limit: move the work to a regular function |
| `setTimeout` not found | `Utilities.sleep(ms)` |
| Script runs out of time | Process in chunks and continue with a time-driven trigger |
| No permission popup | The user must click Advanced > Go to (unsafe) > Allow |
