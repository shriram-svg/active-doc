# active-doc

**A notes file that organizes itself.**

Just write. Anything that sounds like something you need to do — "call the plumber", "IMPORTANT: renew passport", "waiting on Sam" — automatically bubbles to the top of the file. No checkboxes, no tags, no due dates.

---

## Install (one command)

### On a Mac

Open the **Terminal** app (press ⌘+Space, type `Terminal`, hit enter). Paste this and press enter:

```bash
curl -fsSL https://raw.githubusercontent.com/shriram-svg/active-doc/master/install.sh | bash
```

That's it. The installer will:

- create a folder at `~/active-doc/`
- put a starter `notes.md` file inside it
- start a background job that re-ranks your notes every 30 seconds

When it's done, open your notes file:

```bash
open ~/active-doc/notes.md
```

Or find it in Finder: **Go → Home → active-doc → notes.md**.

### On Linux

Same command:

```bash
curl -fsSL https://raw.githubusercontent.com/shriram-svg/active-doc/master/install.sh | bash
```

Then keep it running with:

```bash
python3 ~/active-doc/engine.py ~/active-doc/notes.md --watch 30
```

---

## How to use it

1. **Open** `~/active-doc/notes.md` in any text editor (TextEdit, VS Code, Obsidian, anything).
2. **Write freely** below the `<!-- active-doc:end -->` line.
3. **Save** the file.
4. Within 30 seconds, the top of the file updates with your most important items.

Example — before:

```
Finish tax return
Had coffee with Jamie
Need to call the dentist tomorrow
Waiting on plumber quote
IMPORTANT: renew passport before August
```

After (the top gets added automatically):

```
## 🔥 Active Focus

1. IMPORTANT: renew passport before August  (score 7)
2. Need to call the dentist tomorrow  (score 6)
3. Waiting on plumber quote  (score 2)
4. Finish tax return  (score 1)

<!-- active-doc:end -->

Finish tax return
Had coffee with Jamie
Need to call the dentist tomorrow
...
```

(`Had coffee with Jamie` isn't an action, so it's not in the focus list — but still in your file.)

---

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/shriram-svg/active-doc/master/uninstall.sh | bash
```

Your notes file is kept. Delete `~/active-doc/` manually if you want it gone.

---

## What counts as "important"?

The engine looks for these cues in your text:

- **Action words**: need to, should, must, finalize, ship, email, call, follow up
- **Urgency**: IMPORTANT, ASAP, urgent, deadline, today
- **Dependencies**: waiting on, blocked by
- **Open questions**: not sure, unclear, lines ending in `?`
- **Emphasis**: `**bold**`, `!!`, the word `IMPORTANT`
- **Staleness**: something you wrote days ago that still hasn't been removed
- **Repetition**: the same concern written multiple times

The more of these a line hits, the higher it ranks.

---

## Troubleshooting

**"It's not updating my file."**
Make sure the background job is running:

```bash
launchctl list | grep activedoc
```

If nothing shows up, re-run the install command.

**"I want to change which file it watches."**
Edit `~/Library/LaunchAgents/com.activedoc.engine.plist` and change the last `<string>` path, then:

```bash
launchctl unload ~/Library/LaunchAgents/com.activedoc.engine.plist
launchctl load ~/Library/LaunchAgents/com.activedoc.engine.plist
```

**"I don't have Python 3."**
On macOS, run `xcode-select --install` in Terminal. That installs it.

---

## For developers

See `engine.py` — a single-file Python script, no dependencies. Run directly:

```bash
python3 engine.py path/to/notes.md            # one-shot
python3 engine.py path/to/notes.md --watch 10 # continuous
python3 engine.py path/to/notes.md --top 8    # surface more items
```
