# Contributing to Actual Add-ons

So you want to add an add-on to the catalog. Good. We like ambition. We also like rules, because rules are what keep this catalog from turning back into the 350-entry junk drawer we rescued it from.

Read this whole file. It is long on purpose. The catalog is small on purpose. These two facts are related. (If forms are more your speed than forks, [the easiest path](#the-easiest-path-fill-in-a-form) is the very next section. We would never make you read all of this just to submit an add-on. Okay, we would, but we also made a shortcut.)

## Contents

- [The easiest path: fill in a form](#the-easiest-path-fill-in-a-form)
- [The agreement](#the-agreement)
- [The lazy path: one click](#the-lazy-path-one-click)
- [The careful path: fork and pull request](#the-careful-path-fork-and-pull-request)
- [Field-by-field requirements](#field-by-field-requirements)
- [The size rule](#the-size-rule)
- [What gets rejected](#what-gets-rejected)
- [Updating an existing entry](#updating-an-existing-entry)
- [What happens after you open a pull request](#what-happens-after-you-open-a-pull-request)
- [FAQ](#faq)

## The easiest path: fill in a form

Do not want to fork, clone, or learn what any of those words mean? Open this link:

**[Submit an add-on (form)](https://github.com/notex29/actual-add-ons/issues/new?template=addon-submission.yml)**

It opens a form asking for everything the catalog needs: the add-on ID, name, version, description, links, checksum, and versions. Fill it in, check every acknowledgment box (the form physically will not submit until you do), and hit submit. That is the whole process from your side.

What happens next, without you doing anything:

1. A workflow reads your issue, validates every field with the same strict reviewer that guards pull requests: no leftover template text, proper version formats, NVDA 2026.1 or newer, a real description in English, a sane download link.
2. The author field is optional. Leave it empty and your GitHub username is used automatically, formatted as @you, so everyone knows whose brilliant work this is.
3. If everything passes, the workflow writes `registry/addons/<your-id>.json`, opens a pull request with your manifest, links it to your issue, and closes the issue as done. Your issue literally becomes a pull request while you watch.
4. If anything fails, you get a comment listing exactly what is wrong, and the issue is closed. Fix it and open a new submission. No humans were bothered at any point in this process.

One rule of the form: the add-on ID must be new. If the add-on is already listed and you want to update it, open a normal blank issue instead.

## The agreement

By contributing to this catalog, you agree to the following. Call it a code of conduct, call it a pact, call it the house rules taped to the fridge. It applies to everyone, including us.

1. **The catalog serves the screen reader.** Every entry must help someone use NVDA better: speech, braille, navigation, reading, OCR, input, or accessibility for a real application. If the add-on could be a standalone program and nobody would notice the difference, it does not belong here.

2. **Worth it beats plentiful.** We would rather list 190 add-ons people use than 2,000 nobody can wade through. Do not submit filler. Do not submit something that already exists under a different name. Do not submit your add-on and your add-on's sequel.

3. **Original work only.** Your submission must be your add-on, or one you maintain with the author's blessing. Repackaged copies get deleted and remembered. We once caught a repack because the thief left the original author's homepage in the metadata, like a burglar leaving a business card. We check.

4. **English descriptions.** The catalog speaks English. If your add-on's description is in another language, the entry cannot be reviewed, which means it cannot be accepted. Translate it first.

5. **Small is a feature.** See [the size rule](#the-size-rule). If your add-on outweighs the screen reader it plugs into, something has gone wrong and we will ask questions you cannot answer.

6. **Honest metadata.** The version must be the real version. The checksum must match the file. The download link must work. If any of these are wrong, the build fails, and so does your pull request. Lying to a validator is a bold strategy with a zero percent success rate.

## The lazy path: one click

Do not want to clone anything? Fine. Click this link:

**[Propose a new add-on](https://github.com/notex29/actual-add-ons/new/main?filename=registry%2Faddons%2Fmy-addon-id.json&value=%7B%0A%20%20%22id%22%3A%20%22my-addon-id%22%2C%0A%20%20%22name%22%3A%20%22My%20Add-on%20Name%22%2C%0A%20%20%22version%22%3A%20%221.0.0%22%2C%0A%20%20%22author%22%3A%20%22Your%20Name%22%2C%0A%20%20%22description%22%3A%20%22Short%20English%20description%20of%20what%20the%20add-on%20does%20and%20who%20it%20helps.%22%2C%0A%20%20%22homepage%22%3A%20%22https%3A%2F%2Fgithub.com%2Fyou%2Fmy-addon%22%2C%0A%20%20%22download_url%22%3A%20%22https%3A%2F%2Fgithub.com%2Fyou%2Fmy-addon%2Freleases%2Fdownload%2Fv1.0.0%2Fmy-addon-1.0.0.nvda-addon%22%2C%0A%20%20%22sha256%22%3A%20%22paste-the-64-character-sha256-of-the-nvda-addon-file-here%22%2C%0A%20%20%22min_nvda_version%22%3A%20%222026.1%22%2C%0A%20%20%22last_tested_nvda_version%22%3A%20%222026.1.0%22%2C%0A%20%20%22last_updated%22%3A%20%222026-10-13%22%0A%7D)**

Here is what happens when you click it:

1. GitHub asks you to fork the repository. Check the fork box. That is the entire ceremony.
2. GitHub opens a brand new file at `registry/addons/my-addon-id.json`, pre-filled with a template. The template has placeholder values waiting for you.
3. Rename the file to your add-on's id, fill in every placeholder with real values, and propose the change.
4. GitHub turns your proposal into a pull request. You are done. Go drink water.

Everything in the template must be replaced. A pull request that still says `"author": "Your Name"` will be closed with a comment that simply reads "who?" and no further explanation.

## The careful path: fork and pull request

Prefer the terminal? Respect.

1. Fork `notex29/actual-add-ons` and clone your fork.
2. Create or edit exactly one file: `registry/addons/<your-addon-id>.json`.
3. Make sure the `id` field matches the filename. The validator has strong feelings about this.
4. Run the validator locally before pushing:
   `python scripts/build_registry.py`
   If it prints errors, fix them. If it prints a count, you are good.
5. Commit, push, open a pull request.

One add-on per pull request. Do not bundle three add-ons and a readme typo into one PR like a variety pack. Variety packs get closed.

## Field-by-field requirements

Every field is required. Every field must be a non-empty string. Here is what each one actually means, because "sha256" is not self-explanatory to everyone and we refuse to be gatekept by jargon.

- `id` - The add-on's identifier, and it must match the filename exactly. If the file is `registry/addons/speechHistory.json`, the id is `speechHistory`. Not `SpeechHistory`. Not `speech-history`. Computers are picky and we have chosen to side with the computers.

- `name` - The human-readable display name, the one users see. Make it the real name of the add-on, not a slogan, not a paragraph, not "BEST NVDA ADDON 2026 FREE DOWNLOAD."

- `version` - The add-on's version in semver form: numbers like `1.0.0` or `2026.1.0`. This must be the version of the file your download link points to. If the file says 2.0 and your manifest says 1.5, the catalog is now fiction, and fiction belongs elsewhere.

- `author` - Who made it. A name, not a username salad. If multiple people built it, list them the way the add-on itself credits them.

- `description` - A short description in English explaining what the add-on does and who it helps. One or two sentences is ideal. This is the text users read when deciding whether to install, so "does stuff with NVDA" is grounds for rejection on vibes alone.

- `homepage` - A working http(s) link to the add-on's home: its repository, its documentation page, somewhere a user can learn more. A dead link is a broken promise, and we count broken promises.

- `download_url` - A direct http(s) link to the `.nvda-addon` file, and it must end in `.nvda-addon`. Not a releases page. Not a zip file. Not a Google Drive link that expires when Mercury is in retrograde. The actual file.

- `sha256` - The SHA-256 checksum of the add-on file: 64 lowercase hex characters. This is how users verify the file they downloaded is the file you published. On Windows, you can compute it with `certutil -hashfile file.nvda-addon SHA256` in a terminal. Copy it carefully. One wrong character and the validator will reject it, because checksums do not do "close enough."

- `min_nvda_version` - The oldest NVDA this add-on works with, written as year and release like `2026.1`. 

- `last_tested_nvda_version` - The NVDA version the add-on was last tested against, like `2026.1.0`. This must be 2026.1 or newer. If your add-on was last tested on something older, test it on something newer first. That is the entire point of this catalog: everything here works on a modern NVDA.

- `last_updated` - The date of this entry, in `YYYY-MM-DD` format. The date goes last in the file. Order matters to us the way seasoning matters to cooks.

## The size rule

Here is the deal, stated plainly: **if your add-on is bigger than the screen reader itself, it gets rejected.**

NVDA is a full Windows screen reader that fits in a few dozen megabytes. It reads the internet out loud and fits in less space than a single phone photo backup. If your add-on for announcing clipboard changes somehow needs more disk space than the entire program it plugs into, that is not an add-on, that is a roommate who brought a couch.

Practical guidance:

- Keep downloads as small as you honestly can. Strip what you do not ship.
- Bundled models, voices, and datasets are the usual suspects. If your add-on ships a neural network the size of a season of television, host the model separately and let the add-on download it on demand, or reconsider whether the catalog is the right home for it.
- Anything wildly oversized will be rejected even if it is otherwise perfect. "Otherwise perfect" does not pay the download bill for users on slow connections.

## What gets rejected

The short version lives in the README. This is the long version, with commentary.

- Media downloaders, converters, and players. Your video converter is a fine program. It is not an add-on. It never was.
- AI chatbot wrappers. If the add-on's main feature is "asks an AI a question," the user already has a browser. The browser is right there.
- System resource monitors. GPU, CPU, network, battery. Windows has Task Manager. Task Manager is free. Task Manager was there the whole time.
- Game clients and game helpers. Games are fun. This catalog is not a game store.
- Generic utilities Windows already provides. Clocks, calculators, weather, calendars, reminders. We deleted a clock once and we would do it again.
- Non-English descriptions. Translate first, submit second.
- Anything not supporting NVDA 2026.1 or newer. The 64-bit era is here. Update or rest in peace.
- Repackaged copies of someone else's work. We check homepages against source URLs. We have caught one. We will catch the next one.
- Duplicates and near-duplicates of add-ons already listed. Eleven clipboard managers walked in once. Five walked out. Do the math before submitting.
- Oversized add-ons, per the size rule above.

## Updating an existing entry

New version of your add-on? Update its file: bump `version`, update `download_url`, recompute `sha256`, refresh `last_tested_nvda_version` and `last_updated`. Same one-file pull request. The index rebuilds itself, because the robots handle that part and the robots never sleep.

## What happens after you open a pull request

1. A robot reviews your submission first. It checks for leftover template text, version formatting, the NVDA 2026.1 testing floor, description quality, and download-link sanity. If anything fails, the pull request is commented on and closed automatically. No human has to lift a finger, and no junk ever waits in the queue. Push fixes to your branch and reopen the PR for a fresh review.
2. CI validates every manifest in the repository, not just yours. One bad file fails the whole build. This is by design and it is not up for debate.
3. A human reads your submission against the agreement above. Humans are slower than CI but better at spotting video converters in disguise.
4. If it passes, your file is merged and the index rebuilds automatically. Your add-on appears in `dist/index.json` without you lifting another finger.
5. If a human finds a problem the robot missed, you get a comment explaining why. Fix it and push again. We do not bite. We do, however, close pull requests that still say "Your Name."

## FAQ

Do I need to edit `dist/index.json` myself?

No. Never. CI rebuilds it. Editing it by hand is like rearranging price tags in a store: technically possible, immediately overwritten, and everyone can tell.

My add-on is great but slightly oversized. Can I get an exception?

No exceptions, only architecture changes. Split the heavy parts out, download them on demand, shrink the package. Then submit.

My description is in another language but the add-on is amazing.

Translate the description. Amazing is language-independent. Metadata is not.

Why was my pull request closed so fast?

Either the validator failed, the add-on breaks a rule above, or the file still contains template placeholders. The speed of the closure is proportional to how obvious the problem was.

Who do I complain to?

Open an issue. Complaints with specific suggestions get read carefully. Complaints that are just "why" get a link back to this file.
