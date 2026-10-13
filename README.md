# Actual Add-ons

A catalog of NVDA add-ons that are actually worth installing. If you came here looking for a YouTube downloader, you took a wrong turn at Albuquerque.

## Contents

- [Our goal](#our-goal)
- [Why this exists](#why-this-exists)
- [What we include](#what-we-include)
- [What we leave out](#what-we-leave-out)
- [Contributing](#contributing)
- [Rejection criteria](#rejection-criteria)
- [History](#history)
- [License](#license)
- [Your add-on is listed here](#your-add-on-is-listed-here)
- [Disclaimers](#disclaimers)
- [FAQ](#faq)

## Our goal

We want blind and low-vision users to open this catalog and find add-ons that earn their keep. One test: does it help someone use a screen reader better? Yes, it is in. No, it does not matter how many five-star reviews it has on the site you downloaded it from at 2 a.m.

We are not collecting add-ons like Pokémon cards. Two hundred tools people actually use beat two thousand where half the entries are "AI assistant that answers questions your search engine already answers, but with vibes."

Worth it beats plentiful. Quantity is how you end up with a junk drawer full of AA batteries and a receipt from 2019.

## Why this exists

NVDA has a wonderful add-on community. It also has an alarming number of things that call themselves add-ons while being, and we cannot stress this enough, video converters.

Our starting dataset had 350 entries. You could have opened a small electronics store with the number of GPU monitors and media tools squatting in there. Someone had stuffed YouTube downloaders next to braille tables like it was a garage sale nobody asked for.

This project draws a hard line. We keep what serves the screen reader. We describe it cleanly. We publish it as one file. And we sleep fine at night, 

## What we include

Add-ons that improve the screen reading experience: braille, speech, navigation, OCR, input tools, text tools, remote assistance, and accessibility modules for real Windows applications.

- ✅ Braille and speech output
- ✅ Navigation and reading tools
- ✅ OCR and image description
- ✅ Input assistance and gesture tools
- ✅ Dictionaries and text processing
- ✅ Remote assistance
- ✅ Accessibility modules for specific Windows applications

If it speaks, braille-s, reads, navigates, or makes Windows behave for screen reader users, we probably want it. ("Braille-s" is not a word. The English language has suffered worse. Move on.)

## What we leave out

Things that are programs pretending to be add-ons. Your GPU temperature has many homes in this world. None of them need to be your screen reader.

- ❌ Media downloaders, converters, and players
- ❌ AI chatbot wrappers
- ❌ Game clients and game helpers
- ❌ System resource monitors (GPU, CPU, network, battery)
- ❌ Generic utilities Windows already provides
- ❌ Descriptions that are not in English
- ❌ Add-ons that add no screen reader value

Every single one of those categories showed up in our starting dataset. Every single one got removed on purpose, often gleefully. We are not sorry. We would do it again. We did do it again. There were five rounds.

## Contributing

Want to add an add-on or fix an entry? See [CONTRIBUTING.md](CONTRIBUTING.md). 

## Rejection criteria

A pull request will get one polite look and then a firm no if the add-on:

- is a media downloader, converter, or player
- is an AI chatbot wrapper
- is a system resource monitor
- has a description that is not in English
- is a repackaged version of someone else's add-on, with the original author's homepage still embarrassingly visible in the metadata (yes, we check, yes, we caught one, no, we will not name it twice)
- adds no screen reader value and exists only to inflate the count

This is not negotiable, not "technically it also announces dialog titles while downloading YouTube videos," and not "but my chatbot has a screen reader mode." Neither does my toaster. It still does not belong here.

## History

This catalog started as a 350 add-on datastore and went through several rounds of difficult, entirely justified, occasionally petty decisions:

- NVDA 2026.1 compatibility filter, 350 to 244. If it could not survive a modern NVDA, it could not survive us either.
- Relevance filter, deleted the media converters, chatbots, games, and monitors. Productivity increased. Disk space decreased. Morale soared.
- Language filter, deleted add-ons whose descriptions were not in English. Ten of them. We had told everyone the rules. Nobody read them. Classic.
- Utility filter, deleted generic tools Windows already handles, down to 215. Yes, we deleted a clock. No, you do not need an add-on to know what time it is. Your PC knows. It has been telling you this whole time.
- Deep audit, deleted one repackaged add-on whose homepage still pointed at the original author like a confession written in marker, trimmed the clipboard pile from eleven add-ons to five because eleven clipboard add-ons is not an ecosystem, it is a cry for help, final count 204.

The original 350 are backed up, because we are dramatic, not reckless.

## License

This catalog is released under CC0 1.0 Universal, which is a public domain dedication. In plain language: the catalog data, the scripts, and the documentation in this repository belong to everyone. You can copy them, modify them, fork this whole project, build a competing catalog out of spite, use it commercially, or print it out and wallpaper your office. No permission needed, no attribution required (though a nod is always nice), no royalties, no strings.

The full legal text lives in the LICENSE file and at https://creativecommons.org/publicdomain/zero/1.0/

One boundary, stated clearly: CC0 covers our catalog and our tooling. It does not cover the add-ons themselves. Every add-on belongs to its author under its own license, usually the GNU GPL, and downloading one grants you exactly the rights that license grants. We are librarians, not owners. The books belong to their writers.

There is no warranty either, which is standard for public domain works and also for most things in life: this catalog is provided as-is, and if something is wrong in it, the remedy is to open a pull request, not a lawsuit.

## Your add-on is listed here

Most of this catalog was built by aggregation: we collected existing add-ons ourselves, wrote clean metadata for them, and published the result, alongside contributions from developers who submitted their own work. If you are an add-on author and you find your add-on listed here, that is why. Nothing was stolen, nothing was re-uploaded, we only link to your files where you published them.

If you are not fine with your add-on being listed, for any reason or no reason, we will happily remove it. No argument, no guilt trip, no "but exposure." Here is how:

1. Open an issue at https://github.com/notex29/actual-add-ons/issues/new saying which add-on is yours and that you want it removed.
2. Include some proof that you actually own it: a link to the repository from the account that maintains it, matching author details, commit history with your name on it, anything a reasonable person would accept.
3. We remove the entry and rebuild the index. Done. Your add-on vanishes from the catalog, your files stay exactly where they always were, and we part as friends.

The same applies if your details are wrong: outdated link, wrong author name, version that makes you wince. Tell us and we fix it.

## Disclaimers

The serious paragraph. Read it once, then go back to the fun sections.

This project is not affiliated with, endorsed by, or sponsored by NV Access, the makers of NVDA. NVDA is their thing and their trademark. We just make a list.

The add-ons in this catalog are third-party software written by third-party humans. We review metadata: names, versions, links, checksums, compatibility claims. We do not audit add-on source code for safety, quality, or good intentions. An entry passing our automated review means its paperwork is in order, not that its code has been blessed. Install add-ons at your own judgment, preferably from authors you trust, and verify the SHA-256 checksum when you care about certainty. That is what it is there for.

Download links point to files hosted by others, mostly GitHub releases. Links die, authors move on, accounts vanish. If a link is dead, open an issue and we will update or delist the entry.

Nothing here is legal, medical, or financial advice, and the catalog is not a guarantee that any add-on works, is safe, or will continue to exist tomorrow. Software rots, authors retire, APIs change. We curate carefully and fix things fast, but the universe makes no promises and neither do we.

## FAQ

Why not just use the official NVDA Add-on Store?

You can, and should use whichever catalog you like. This one has a strict bouncer, a shorter guest list, and zero tolerance for video converters.

Can I add my own add-on?

Yes. See Contributing. Bring something that helps screen reader users, not another weather widget. Windows has weather. It also has a clock, a calculator, and opinions about your battery.

Why is this catalog so small?

Because we deleted things. You would be amazed how good a catalog looks once you remove the things that do not belong in it. It is the same principle as cleaning a garage: painful, revealing, and afterwards you own fewer shovels you never used.

Why is the validation so strict?

Because one broken entry teaches every client to stop trusting the whole catalog. Trust takes years to build and one malformed checksum to destroy, which is also decent relationship advice.

who made you the referee?

Nobody. We just got tired, read the metadata for the 200th time, and started deletions. You know the feeling. Everyone has one. Ours just happened to include a GPU monitor that called itself a productivity suite.
