/**
 * ===========================================================================
 *  SKETCH SKELETON for a generative-art piece (p5.js 1.7, global mode)
 * ===========================================================================
 *
 * This file shows the SHAPE every sketch must have, plus helpers you may copy.
 * It is not a pattern to reuse: the philosophy you wrote decides what is drawn.
 *
 * The page that scripts/build_art.py builds around your sketch already provides:
 *   - setup(): makes the canvas (size from "canvas" in spec.json), then calls initializeSystem()
 *   - params: { seed, <one number per slider in spec.json>, colorPalette: [hex, ...] }
 *   - the seed box (Go, Prev, Next, Random), the sliders, the colour pickers,
 *     Regenerate, Reset, Pause and Download PNG
 *
 * Your sketch.js defines:
 *   - function initializeSystem()   REQUIRED. Runs on load and again whenever the seed, a colour or
 *                                   a slider (once released) changes, or the user presses Regenerate.
 *   - function draw()               OPTIONAL. Define it for an animated piece (it runs every frame).
 *                                   Leave it out for a static piece: draw everything inside initializeSystem().
 *   - your own classes, helpers and top-level state (plain values only, see rule 3)
 *
 * Never define setup(). Never declare params, defaultParams, SPEC or Studio. Never call createCanvas().
 * Use function declarations (function draw() { ... }), not const draw = () => { ... }.
 */

// ===========================================================================
// 1. READING THE SETTINGS
// ===========================================================================
// params.seed          the current seed (whole number)
// params.count         a slider with id "count" in spec.json (any id you chose)
// params.colorPalette  hex strings in the order of "colors" in spec.json, e.g. params.colorPalette[0]
//
// Read params inside initializeSystem() and draw(), never once at the top of the file:
// the user changes them while the piece runs. Every slider id in the spec must be read somewhere.

// ===========================================================================
// 2. STATE: declare at the top level, fill in initializeSystem()
// ===========================================================================
let agents = [];
let inks = [];   // p5 colours made from the palette
let bg;          // background colour
let tick = 0;    // your own clock. Do not use frameCount, millis() or Date for the art:
                 // Regenerate and a seed jump must replay exactly the same piece.

// ===========================================================================
// 3. initializeSystem(): seed first, then rebuild everything from scratch
// ===========================================================================
function initializeSystem() {
  randomSeed(params.seed);   // 1. always first: same seed, same picture
  noiseSeed(params.seed);

  tick = 0;                  // 2. reset your clock and every piece of state

  bg = color(params.colorPalette[0]);                       // 3. build colours here (p5 is ready now)
  inks = params.colorPalette.slice(1).map(function (hex) { return color(hex); });

  background(bg);            // 4. paint the starting canvas

  agents = [];               // 5. create the elements. random() and noise() are seeded, so they repeat
  for (let i = 0; i < params.count; i++) {
    agents.push(new Agent());
  }

  // STATIC piece: draw everything right here and do NOT define draw().
  // ANIMATED piece: define draw() below. Do not call noLoop() in this function.
}

// ===========================================================================
// 4. draw(): one frame of an animated piece
// ===========================================================================
function draw() {
  tick++;

  // Soft trails: lay a low-alpha wash of the background over the last frame.
  noStroke();
  fill(red(bg), green(bg), blue(bg), 18);
  rect(0, 0, width, height);

  for (const a of agents) {
    a.update();
    a.display();
  }

  // A piece that finishes can stop itself. Download PNG then saves the finished picture,
  // and the Pause button still works. initializeSystem() restarts it.
  // if (tick > 900) noLoop();
}

// ===========================================================================
// 5. CLASSES: use them when many things share behaviour
// ===========================================================================
class Agent {
  constructor() {
    this.x = random(width);              // seeded
    this.y = random(height);
    this.tint = random(1);               // position along the palette, decided once
    this.size = random(0.8, 2.2);
  }

  update() {
    // Move along a noise field: smooth, organic, and fully determined by the seed.
    const angle = noise(this.x * 0.003, this.y * 0.003, tick * 0.002) * TWO_PI * 2;
    this.x += cos(angle) * 1.2;
    this.y += sin(angle) * 1.2;

    // Respawn at a random edge point when leaving the canvas (still seeded).
    if (this.x < 0 || this.x > width || this.y < 0 || this.y > height) {
      this.x = random(width);
      this.y = random(height);
    }
  }

  display() {
    stroke(paletteBlend(inks, this.tint));
    strokeWeight(this.size);
    point(this.x, this.y);
  }
}

// ===========================================================================
// 6. HELPERS (copy what you need)
// ===========================================================================

// Smooth colour along a list of p5 colours; t runs from 0 to 1.
function paletteBlend(list, t) {
  if (list.length === 1) return list[0];
  const f = constrain(t, 0, 1) * (list.length - 1);
  const i = Math.min(floor(f), list.length - 2);
  return lerpColor(list[i], list[i + 1], f - i);
}

// Same colour with its own alpha (0 to 255).
function withAlpha(c, a) {
  return color(red(c), green(c), blue(c), a);
}

// Wrap a value into 0..max so elements leave one edge and enter the opposite one.
function wrap(v, max) {
  return ((v % max) + max) % max;
}

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// ===========================================================================
// 7. RULES THAT KEEP THE PAGE WORKING
// ===========================================================================
// 1. All randomness comes from random(), randomGaussian() and noise() after the two seed calls.
//    No Math.random(), Date or frameCount in the art.
// 2. Everything is rebuilt in initializeSystem(): no leftovers from the previous seed or settings.
// 3. p5 is not ready while the file loads. At the top level keep only plain values
//    (numbers, strings, [], {}). Anything like color(...), random(...), width, height,
//    TWO_PI, floor(...) or createVector(...) belongs inside a function.
// 4. Do not name your own variables or functions like p5 ones (color, noise, random, map, scale,
//    rotate, translate, filter, text, image, line, point, min, max, key ...).
// 5. Use width and height for sizes, never the window size.
// 6. No outside files, network calls, fonts or images. Generate everything in code.
// 7. Keep it light: at most about 5,000 moving elements at 1200 x 1200, no loadPixels()
//    on the whole canvas every frame, no nested loops over thousands of elements.
//    Keep initializeSystem() quick too (it runs when a slider is released or a colour changes):
//    no warm-up of more than about 30 frames.
// 8. Marks must be clearly visible. Trails come from the low-alpha background wash in draw()
//    (alpha 10 to 30); draw the marks themselves with alpha of at least 80, or opaque.
//    A wash that erases faster than the marks are drawn leaves a blank canvas. blendMode(ADD)
//    makes single marks dim: use it only on a dark background with every mark at alpha 60 or more.
// 9. Slider values arrive as numbers. A slider that only changes how things move (speed) can be
//    marked "live": true in the spec and read each frame; any other slider restarts the piece.
