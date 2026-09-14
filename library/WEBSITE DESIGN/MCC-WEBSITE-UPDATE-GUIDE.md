# Montana Contracting Corp — Website Update Instructions

**Live site:** [montanacontracting.com](https://montanacontracting.com)
**Hosting:** Vercel (auto-deploys from `fable-v5/` on push)
**Source file:** `montana-fable.html` (master edit location)
**Production folder:** `fable-v5/` (deployed to Vercel)

---

## How Changes Work

The entire website is a **single-page application (SPA)** built inside one HTML file: `montana-fable.html`. Every section (hero, recognition, video, projects, contact) lives in this file. There is no CMS, no build system, no framework. It's pure HTML + CSS + JavaScript.

To change anything on the site, you edit `montana-fable.html`, copy it to `fable-v5/index.html`, and deploy.

---

## Step-by-Step: Make a Change and Deploy

### 1. Open the source file

```
montana-fable.html
```

This is the master file. All edits go here first.

### 2. Make your edit

Find the section you want to change. The file is organized by comments:

| Section | What it controls |
|---|---|
| `<!-- HERO -->` | Homepage hero image and text |
| `<!-- RECOGNITION -->` | Press logos carousel (Vogue, NYT, AD, Dwell, ArchDaily) |
| `<!-- FILM -->` | Twisted Ridge video section |
| `<!-- APPROACH -->` | Our Approach section |
| `<!-- VALUES -->` | Core Values section |
| `<!-- STATS -->` | Stats (years, projects, licensed) |
| `<!-- FEATURED -->` | Featured Projects grid |
| `<!-- ALL PROJECTS -->` | Full project overlay |
| `<!-- PRE-CON -->` | Pre-construction page |
| `<!-- FINANCING -->` | Financing section |
| `<!-- CONTACT -->` | Contact form and footer |

Edit the HTML directly. Save the file.

### 3. Copy to production folder

```bash
cp montana-fable.html fable-v5/index.html
```

### 4. Deploy to Vercel

```bash
cd fable-v5
vercel --prod --yes
```

This pushes `fable-v5/` to Vercel's production servers. The site goes live in about 30 seconds.

### 5. Verify

Open [montanacontracting.com](https://montanacontracting.com) and confirm your change appears.

---

## Adding or Updating Project Photos

**Location:** `fable-v5/assets/photos/projects/`

Each project gets a folder. Name it with lowercase, hyphens (e.g., `tuxedo-residence/`). Drop JPEG files inside. Name them sequentially:

```
project-name-01.jpg
project-name-02.jpg
...
```

**Photo specs:**
- Format: JPEG (`.jpg`)
- Max width: 2400px (for performance)
- Quality: 80-85% is fine for web
- Aspect ratio: landscape preferred (16:9 or 3:2)

**After adding photos:** Edit `montana-fable.html` and find the project's photo array in the JavaScript. Add the new file paths to the array. Copy to `fable-v5/` and deploy.

---

## Adding a Brand New Project

This requires editing the JavaScript in `montana-fable.html`. Each project is defined as an object in a `projects` array. Find the array (search for `const projects =`) and add a new entry:

```javascript
{
  id: 'project-slug',
  name: 'Project Name',
  location: 'City, NY',
  year: '2024',
  type: 'Custom Home',
  cover: 'assets/photos/projects/project-name/cover.jpg',
  photos: [
    'assets/photos/projects/project-name/photo-01.jpg',
    'assets/photos/projects/project-name/photo-02.jpg',
  ],
  description: 'Project description text here.'
}
```

Save, copy, deploy.

---

## Changing the Video

The video is a native HTML5 `<video>` tag, not an embed. The current file is:

```
fable-v5/assets/video/twisted-ridge-film.mp4
```

**To replace it:** Drop a new `.mp4` file in `fable-v5/assets/video/`, then edit the `<video>` tag in `montana-fable.html` (search for `twisted-ridge-film.mp4`) to point to the new filename.

**Video specs:**
- Format: MP4 (H.264)
- Resolution: 1920x1080 recommended
- Keep file size under 20MB (use HandBrake or `ffmpeg` to compress)
- The video loops automatically and plays muted

---

## Changing the Logo

Two versions exist in `fable-v5/assets/`:
- `montana-logo.svg` — dark version (for light backgrounds)
- `montana-logo-white.svg` — white version (for dark backgrounds)

**To replace:** Drop a new SVG into `fable-v5/assets/` with the same filename. It will swap automatically.

The email logo PNG (`montana-logo-email.png`) is separate. To update it, regenerate from the SVG and host at the same path.

---

## Changing Contact Info, Phone, Address, etc.

Search `montana-fable.html` for the text you want to change (e.g., `(845)`, `info@montana`, `Congers`). Edit directly. Save, copy, deploy.

---

## Important Rules

1. **Always edit `montana-fable.html` first**, then copy to `fable-v5/index.html`. Never edit `fable-v5/index.html` directly — it gets overwritten on every copy.

2. **Never use em-dashes or en-dashes** (`—` or `–`). Use periods, commas, or hyphens instead.

3. **Brand colors are locked:**
   - Navy: `#0028cc`
   - Off-white: `#f4f5f8`
   - Near-black: `#070912` / `#080c14`

4. **Fonts are locked:** TT Commons Pro (display) + system fonts for body. No other web fonts.

5. **No AI-isms in copy:** No "seamlessly," "elevated," "curated," "world-class." Write like a builder, not a brochure.

6. **Project photos must not duplicate.** Check existing projects before adding new ones.

---

## Quick Reference: Common Tasks

| Task | Edit location | Deploy command |
|---|---|---|
| Change hero image | `montana-fable.html` → `.hero__bg img` | `cp montana-fable.html fable-v5/index.html && cd fable-v5 && vercel --prod --yes` |
| Add project photos | `fable-v5/assets/photos/projects/` + JS array | Same |
| Update phone number | `montana-fable.html` → search phone number | Same |
| Replace video | `fable-v5/assets/video/` + `<video>` tag | Same |
| Add press logo | `fable-v5/assets/press/` + Recognition section HTML | Same |

---

## Need Help?

Ask Kron (the AI assistant in Hermes) to make the change. Say what you want changed, and it will edit the file and deploy for you. No need to touch Terminal unless you want to.
