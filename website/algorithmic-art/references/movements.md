# Directions to start from

Pick one, combine two, or invent your own. The philosophy comes first: choose the direction that fits it, not the other way round. Each one runs fine in a browser at 1200 x 1200 if you keep to the sizes given.

## Algorithms

**Organic Turbulence (flow field).** Chaos held by natural law. Many particles follow the angle `noise(x * s, y * s, tick * t) * TWO_PI * k` from a layered noise field (add a second octave at two or three times the scale for turbulent and calm zones). Draw short translucent segments so trails build up into density. Colour by speed, angle or age. Respawn particles that leave at seeded random points. Sliders worth offering: particle count (1000 to 5000), noise scale (0.001 to 0.01), turbulence k (1 to 4), speed, trail fade. Let it settle after 600 to 900 ticks so a saved PNG is a finished picture.

**Quantum Harmonics (wave interference).** Discrete points showing wave behaviour. Place 3 to 7 sources at seeded positions. At each point of a 6 to 12 px grid, sum `sin(dist_i * frequency - tick * speed + phase_i)` over the sources. Draw a dot or short line there, sized and coloured by the sum: bright where waves reinforce, empty where they cancel. Sliders: number of sources, frequency, speed, grid spacing, dot size.

**Recursive Whispers (branching).** Self-similarity across scales. `branch(x, y, angle, len, depth)` draws a line, then 2 or 3 children turned by plus or minus 15 to 35 degrees plus a little noise, with `len` times 0.7 to 0.8 (0.618 for a golden feel) and thinner strokes at each level. Stop at depth 9 to 11 and keep the total under about 30,000 segments. A static piece: draw it all in `initializeSystem()`. Sliders: depth, branch angle, length ratio, wind (noise bend), number of trunks.

**Field Dynamics (forces).** Invisible forces made visible by their effect. Place 3 to 8 seeded charges with signed strengths. Particles accelerate along the summed force, strength divided by (distance squared plus a small softening term), with some drag. Draw only the traces. Respawn particles that reach a charge or an edge. Sliders: number of charges, strength, drag, particle count.

**Stochastic Crystallization (packing and cells).** Random processes settling into order. Circle packing: try up to N seeded random points; the radius is the largest that touches no existing circle and no edge; keep the circle if it is above a minimum radius. Checking every circle is fine up to about 1,500 circles. Colour by radius or position. For a Voronoi look use 40 to 80 seeded sites and colour a coarse grid (4 px cells) by nearest site; checking every pixel at full size is too slow. Sliders: attempts, minimum radius, gap, palette bias.

**Harmonograph (damped pendulums).** `x(t) = sum of A_i * sin(f_i * t + p_i) * exp(-d_i * t)` with two or three terms, and the same for `y`. Use frequencies near simple ratios (1, 2, 3, 3/2) with a small detune. Plot thousands of tiny low-alpha segments, advancing `t` a little each frame. Suits music and album art. Sliders: detune, damping, line opacity, frequency set.

**Strange attractor (Clifford).** Iterate `x' = sin(a * y) + c * cos(a * x)`, `y' = sin(b * x) + d * cos(b * y)` from a seeded start, and plot 5,000 to 20,000 points per frame at low alpha, mapping roughly -3 to 3 onto the canvas. Take a and b in -2 to 2 and c and d in -1.5 to 1.5. Skip the first 100 iterations. Some settings collapse to a plain loop: check that the first few hundred points spread out, and if not draw new values from the seeded generator. Sliders: a, b, c, d, point opacity.

**Truchet tiling.** A grid of 24 to 60 px cells; each cell picks one of two or three orientations (two quarter-arcs, a diagonal) from the seeded random, or from a noise threshold so regions flow together. Static, cheap, always composed. Sliders: cell size, line weight, noise scale, mix.

**Flocking.** 200 to 400 agents with separation, alignment and cohesion inside a radius. Use a coarse grid for neighbour lookups. Draw short oriented triangles with fading trails. Steer or wrap at the edges. Sliders: separation, alignment, cohesion, radius, speed.

## The conceptual thread

One quiet idea from the request that shapes a rule, a parameter or the palette, never a literal picture of it:

- Ocean currents: the noise field drifts on a slow cycle like a tide, and the fastest particles are the foam-coloured ones.
- Art for a slow song: low speed, long trails, wide spacing. For a fast song: high speed, short trails, tight spacing.
- A coffee brand: warm layers that settle like sediment, with the lightest tone only at the top.

## Palette starting points

Adjust to the request. The first colour is the background and the rest are inks. Names in the spec labels should say what each colour does.

- Deep sea: `#0b1f33`, `#1f6f8b`, `#2ec4b6`, `#cbf3f0`, accent `#ff9f1c`
- Dusk: `#1b1330`, `#5b3a8c`, `#c3447a`, `#ff8a5b`, `#ffe3b3`
- Paper and ink: `#f3efe6`, `#1f2933`, `#c8553d`, `#588157`, `#3a5a7a`
- Neon night: `#07060f`, `#ff2e88`, `#2ee6ff`, `#7a5cff`, `#f5f0ff`
- Moss and stone: `#16201a`, `#3d5a40`, `#a3b18a`, `#dad7cd`, `#bc6c25`
