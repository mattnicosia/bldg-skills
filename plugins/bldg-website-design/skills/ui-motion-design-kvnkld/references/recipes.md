# Motion recipes

Longer implementation patterns referenced from SKILL.md. Read the section you need; do not paste all of it. All recipes assume the tokens in `assets/tokens.css` are already loaded.

## Table of contents
1. Blur-in entrance
2. Expand / collapse (grid-rows, no max-height hack)
3. FLIP (moving an element between containers)
4. Draggable physics (momentum, friction, soft edges)
5. Two-zone magnetic snap points
6. Spring for un-animatable values (counters, live numbers)
7. Working-state micro-interactions (shimmer, digit roll, icon cross-fade)

---

## 1. Blur-in entrance

Entrances never just fade. Combine opacity, a small upward shift, and a tiny blur that clears. The blur is the secret ingredient: content focuses into place instead of flicking on. The curve is just the smooth preset, nothing new.

```css
@keyframes entrance {
  from { opacity: 0; transform: translateY(6px); filter: blur(2px); }
  to   { opacity: 1; transform: translateY(0);   filter: blur(0); }
}
.enter {
  animation: entrance var(--duration-slow) var(--ease-smooth) both;
}
```

Tooltips use the same idea at a smaller scale: fade + lift 4px + clear a 2px blur on `--duration-fast`. Never an instant pop-in.

---

## 2. Expand / collapse

Animating `max-height: 9999px` is jittery and times wrong. Animate CSS grid rows instead. It resolves to the content's real height with no guesswork.

```css
.reveal {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows var(--duration-normal) var(--ease-smooth);
}
.reveal[data-open="true"] { grid-template-rows: 1fr; }
.reveal > * { overflow: hidden; }
```

---

## 3. FLIP (First, Last, Invert, Play)

For an element that moves across the layout (a card flying into a different container), measure where it starts, measure where it ends, jump it back to the start visually, then animate to the end. Two position measurements, impossibly smooth.

```js
function flip(el, mutate) {
  const first = el.getBoundingClientRect();   // First
  mutate();                                    // change the DOM / container
  const last = el.getBoundingClientRect();     // Last
  const dx = first.left - last.left;
  const dy = first.top  - last.top;
  el.style.transform = `translate(${dx}px, ${dy}px)`; // Invert
  el.style.transition = 'transform 0s';
  requestAnimationFrame(() => {                // Play
    el.style.transition = 'transform var(--duration-slow) var(--ease-smooth)';
    el.style.transform = '';
  });
}
```

---

## 4. Draggable physics

A timed animation on a drag handle feels dead. Real interfaces have momentum, friction, and resistance. Three things make a drag feel alive:

- **Velocity tracking**, smoothed over recent frames, so a flick carries weight.
- **Momentum on release**: keep moving and decay gradually until rest, like something sliding across a table.
- **Soft boundaries**: at the edge, stretch a little and spring back instead of stopping dead. This is the difference between "web slider" and "iOS".

```js
let pos = 0, velocity = 0, dragging = false, last = 0, lastT = 0;
const FRICTION = 0.92;     // higher = glides longer
const STRETCH  = 0.35;     // resistance past the edge (rubber-band)
const MIN = 0, MAX = 300;

function onMove(x) {
  const now = performance.now();
  const dt = Math.max(now - lastT, 1);
  velocity = velocity * 0.7 + ((x - last) / dt) * 0.3 * 16; // smoothed
  let next = pos + (x - last);
  if (next < MIN) next = MIN + (next - MIN) * STRETCH;       // soft edge
  if (next > MAX) next = MAX + (next - MAX) * STRETCH;
  pos = next; last = x; lastT = now;
  render(pos);
}

function onRelease() {
  dragging = false;
  (function coast() {
    if (dragging) return;
    velocity *= FRICTION;
    pos += velocity;
    if (pos < MIN) { pos += (MIN - pos) * 0.2; velocity *= 0.5; }  // spring back
    if (pos > MAX) { pos += (MAX - pos) * 0.2; velocity *= 0.5; }
    render(pos);
    if (Math.abs(velocity) > 0.1 || pos < MIN || pos > MAX) requestAnimationFrame(coast);
  })();
}
```

When prompting for this, skip the jargon and describe the feel: "Make the slider feel like a real physical object. When I flick it, it keeps gliding and coasts to a stop on its own, like sliding something across a table. At the edge it stretches a little and springs back."

---

## 5. Two-zone magnetic snap points

Hardware gives haptic clicks; on the web you fake the same satisfaction with snapping. The trick that makes it feel real is two zones: a tight pull-in zone to snap in, and a larger release zone to break free. Once snapped, the user has to mean it to pull away. Pulse the label when it catches for a micro flash of feedback.

```js
const SNAPS = [0, 100, 200, 300];
const PULL_IN = 8;    // tight: enter snap within 8px
const RELEASE = 22;   // loose: must travel 22px to escape

let snapped = null;
function applySnap(raw) {
  if (snapped !== null) {
    if (Math.abs(raw - snapped) < RELEASE) return snapped;  // resist leaving
    snapped = null;
  }
  for (const s of SNAPS) {
    if (Math.abs(raw - s) < PULL_IN) {
      if (snapped !== s) pulseLabel();   // flash on catch
      snapped = s;
      return s;
    }
  }
  return raw;
}
```

---

## 6. Spring for un-animatable values

Counters and live numbers can't ride a fixed-duration transition cleanly. Drive them with a spring tuned for stiffness, bounce, and weight instead of a time.

```js
function spring(target, value = target, v = 0, stiffness = 0.08, damping = 0.75) {
  return function step(onFrame) {
    const force = (target - value) * stiffness;
    v = (v + force) * damping;
    value += v;
    onFrame(value);
    if (Math.abs(v) > 0.01 || Math.abs(target - value) > 0.01) {
      requestAnimationFrame(() => step(onFrame));
    }
  };
}
```

---

## 7. Working-state micro-interactions

These are discovered by building, not specced up front. A few that recur:

**Shimmer sweep** on a label while a task runs (calm and alive, not a flashy spinner):

```css
@keyframes shimmer { to { background-position: 200% center; } }
.working {
  background: linear-gradient(90deg,
    currentColor 0%, color-mix(in srgb, currentColor 40%, transparent) 50%, currentColor 100%);
  background-size: 200% auto;
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  animation: shimmer 2s linear infinite;
}
```

**Digit roll**: numbers roll digit-by-digit instead of hard-cutting. Stack each digit in a vertical column and translate it; transition `transform` on `--ease-smooth`.

**Icon cross-fade**: play/pause (or any icon swap) cross-fade and scale between each other rather than swapping instantly. Both icons absolute-positioned in the same box; toggle opacity + a slight scale on `--duration-fast`.
