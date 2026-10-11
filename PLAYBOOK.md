
# Tab Scriptoria daily TikToks

Andrew Yi owns Tab Scriptoria (tabscriptoria.com): guitar recording → tab/sheet music with chord names, fingerings, slow-down/loop, MIDI/text export, plus **Solo ideas** and **Song → guitar**. This skill produces the day's three TikTok posts for his account and gets them live after his OK. Keep messages to Andrew short.

## Daily mix (US Eastern)
| Slot | Format | Job |
|---|---|---|
| 12:30 PM | 5–6 slide education carousel (practice steps, fingering tips, theory) | saves |
| 5:00 PM | 15–35 s test/story video ("can it tab this?", POV memes over Andrew's silent clips, founder log) | trust, comments |
| 8:00 PM | 8–20 s demo video (recording → tab, Solo ideas challenge ≤2×/week, Song → guitar on public-domain input) | sign-ups |

Every post must contain **new** material (new progression, key, style, piece or clip). Never re-upload or re-crop the same media; reuse templates, not footage. Log each post in `data/log.json` (date, slot, format, hook, inputs, Postiz id) and check it before choosing inputs.

## Setup
1. `add_repo` andrewyi-jpg/tabscriptoria-promo with push access, then `git clone --depth 1 https://github.com/andrewyi-jpg/tabscriptoria-promo /home/claude/tabscriptoria-promo`. Commit with the environment's default git identity (never Andrew's email: the repo is public).
2. Check `curl -sS -o /dev/null -w "%{http_code}" https://tabscriptoria.com/`. If it is blocked, tell Andrew in one line (the cloud environment's Custom network list must include tabscriptoria.com) and fall back to his laptop: the in-app browser fetches files, downloads go to Downloads (ask him first), then `device_stage_files`.
3. Renderers live in `scripts/` (`tslib.py` brand + tab drawing + encoder; `carousel_steps.py`, `solo_relay.py`, `pov_meme.py`). Copy and adapt them for new variants; keep the brand look.

## Inputs that need no filming
- **Solo ideas API (no login):** `POST https://tabscriptoria.com/solo-ideas` with JSON `{chords:"Am F C G", tempo:92, style, neck:"full"|"box", position:5, tuning:"standard"|"half-step-down"|"drop-d", seed, level, sourceRun:null}` → `{id}`. Styles: melodic, blues, arpeggio (chord tones/fingerstyle), funk, jazz, flamenco, metal, classical. Levels: map, rhythm, guide, approach, idea (practice steps 1–4). Files: `/ideas/{id}/idea.json` (results.solo.notes: pitch, string 0=high e, fret, start, duration; annotations = chords; practice.steps/phrases/maps), `idea.wav` (idea + backing, 22 kHz mono), `trade.wav`, `backing.wav`, `idea.mid`, `idea.txt`.
- **App screenshots:** `assets/ui/` (transcribe form, Solo ideas form). Capture new ones with the in-app browser at a 432×768 viewport when the laptop is online; crop out the "Free · N s left" badge.
- **Andrew's clips:** only original or public-domain material; each clip is a transcription input once, or silent hand footage at most twice a week.

## Rules
- **Copyright:** no copyrighted songs in the audio or as on-screen tab/notation. Use original progressions and public-domain pieces in Andrew's own arrangement.
- **AI framing:** sell "it transcribes, you play"; Solo ideas output is "solos to learn", never "AI-made music". Any post whose audio is app playback shows "App playback" on screen and sets `video_made_with_ai: true`. No invented first-person stories; write scenarios as "POV:".
- **Claims (verified 2026-10-11, recheck /billing if unsure):** signed-in users get 5 min transcription + 5 min song analysis free per month; guests 1 min. Packs: Starter 60 min $5, Plus 200 min $12, Studio 600 min $30; beta membership 120 min/month for $5. Competitor facts only with a source (Songsterr AI and Klangio free clips stop at 20 s). No accuracy percentages.
- **Layout:** 1080×1920; text and tab inside x 64–950, y 150–1450; hook in the first frame; ≤2 text lines on screen at once; high contrast.
- **Specs:** video H.264 30 fps, AAC, about -14 LUFS; carousels JPEG ≤1080p, 5–6 slides, slide 1 = hook ≤8 words, last slide = call to action.
- **Captions:** start with the search phrase, say "Tab Scriptoria" or tabscriptoria.com, 1–3 specific hashtags, end with a question. Photo posts also need a `title` ≤90 chars.
- **Music:** videos attach a Commercial Music Library track by ID (`data/cml_tracks.json`, rotate, never the same twice in a row) via the `music` setting; `audio_volume` ~70 over silent clips, ~15–20 under guitar, none under app playback. Photo posts: `autoAddMusic: "yes"`. Never bake CML audio into files.

## Hosting, review, posting
1. Render into `out/YYYY-MM-DD/`, check stills of every render (safe area, typos, timing), commit and push.
2. `uploadFromUrlTool` each file with `https://raw.githubusercontent.com/andrewyi-jpg/tabscriptoria-promo/main/<path>`.
3. Send Andrew the three files (SendUserFile) with caption and slot for each, then ask him to reply **post** (or name changes).
4. Only after he says post: `integrationSchedulePostTool` for integration `cmv34y4f61avrqz0yhg4ujhgv` (tiktok-business) with `privacy_level: PUBLIC_TO_EVERYONE`, `comment: true`, `duet`/`stitch` true for videos, `brand_organic_toggle: true`, `brand_content_toggle: false`, `content_posting_method: DIRECT_POST`. Dates are UTC (ET = UTC-4 until Nov 1, then UTC-5). Posts can't be edited or deleted through Postiz tools; Andrew does that in the Postiz app.
5. Update `data/log.json`, commit, push. Report in one or two lines.

## Measuring
Once a week, list posts with `postsListTool`; ask Andrew for TikTok analytics if he wants a review. Judge formats after 5–7 posts against the account's own median; expand top-quarter formats, drop bottom-quarter ones.
