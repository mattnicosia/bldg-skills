// The Inn at Kirkside, Mapos 75% CD Pricing Set (Sept 2026), simplified massing for the presentation.
// Footprint traced from the roof plan AD-103 (3/16" = 1'-0"), split into wings. Heights read off the AD-200/201
// elevations: two stories to the eaves at about 20 ft, 12:12 gables. Courtyard conservatory, glazed porch, deck,
// terraces, pergola and fire pit placed from the A-003 axonometric and renderings. x east (plan right), y up, z = plan down.
import * as THREE from 'three';
import * as P from '../../kit/tools/glb/parts.js';

export default function build() {
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const M = new P.Model(P.materials());
  const FL = 1.5, EAVE = 20, T = 0.8;
  // wings: [x0, z0, x1, z1, eave, ridge axis 'x' | 'z', pitch]
  const W = [
    [31, 13, 59, 46, EAVE, 'z', 1.0],   // northwest block
    [37, 24, 106, 41, EAVE, 'x', 1.0],  // north wing
    [79, 23, 106, 76, EAVE, 'z', 1.0],  // east block
    [66, 49, 90, 85, EAVE, 'z', 1.0],   // center block
    [51, 66, 85, 97, EAVE, 'z', 1.0],   // south center block
    [16, 66, 41, 97, EAVE, 'z', 1.0],   // southwest block
  ];
  const inside = (x, z, skip) => W.some((w, k) => k !== skip && x > w[0] + 0.3 && x < w[2] - 0.3 && z > w[1] + 0.3 && z < w[3] - 0.3);
  const porch = [16, 97, 84, 110];        // glazed porch on the deck side, one story
  const inPorch = (x, z) => x > porch[0] && x < porch[2] && z > porch[1] && z < porch[3];

  // ---------------------------------------------------------------- foundation
  M.phase = 'foundation';
  for (const [x0, z0, x1, z1] of W) {
    for (const [a, b, c, d] of [[x0, z0, x1, z0 + T], [x0, z1 - T, x1, z1], [x0, z0 + T, x0 + T, z1 - T], [x1 - T, z0 + T, x1, z1 - T]]) M.add(P.abox(a, -9, b, c, FL, d), 'concrete');
    M.add(P.abox(x0 + T, -9.4, z0 + T, x1 - T, -9, z1 - T), 'slab');
  }
  M.el = 'foundation';
  // new grade beams and walls under the porch, the elevator pit
  for (const [a, b, c, d] of [[porch[0], porch[3] - T, porch[2], porch[3]], [porch[0], porch[1], porch[0] + T, porch[3] - T], [porch[2] - T, porch[1], porch[2], porch[3] - T]]) M.add(P.abox(a, -4, b, c, FL, d), 'concrete');
  M.add(P.abox(44, -14, 58, 52, FL, 66), 'concrete');
  M.el = null;

  // ---------------------------------------------------------------- the house
  M.phase = 'house';
  W.forEach(([x0, z0, x1, z1, eave, ax, pitch], k) => {
    // walls
    for (const [a, b, c, d] of [[x0, z0, x1, z0 + T], [x0, z1 - T, x1, z1], [x0, z0 + T, x0 + T, z1 - T], [x1 - T, z0 + T, x1, z1 - T]]) M.add(P.abox(a, FL, b, c, eave, d), 'siding');
    M.add(P.abox(x0 + 0.2, FL - 0.4, z0 + 0.2, x1 - 0.2, FL, z1 - 0.2), 'slab');
    // roof: 12:12 gable, 1.5 ft overhang
    const o = 1.5, span = ax === 'z' ? (x1 - x0) : (z1 - z0), rise = span / 2 * pitch, ridge = eave + rise;
    if (ax === 'z') {
      const xm = (x0 + x1) / 2;
      P.roofPlane(M, V(x0 - o, eave - o * pitch, z1 + o), V(x0 - o, eave - o * pitch, z0 - o), V(xm, ridge, z0 - o), V(xm, ridge, z1 + o), { seams: false, thick: 0.5 });
      P.roofPlane(M, V(x1 + o, eave - o * pitch, z0 - o), V(x1 + o, eave - o * pitch, z1 + o), V(xm, ridge, z1 + o), V(xm, ridge, z0 - o), { seams: false, thick: 0.5 });
      for (const z of [z0, z1]) {   // gable ends
        const wl = new P.Wall(V(x0, 0, z), V(1, 0, 0), V(0, 0, z === z0 ? -1 : 1));
        M.add(wl.slab([[0, eave], [x1 - x0, eave], [(x1 - x0) / 2, ridge - 0.4]], [], -T, 0), 'siding');
      }
    } else {
      const zm = (z0 + z1) / 2;
      P.roofPlane(M, V(x0 - o, eave - o * pitch, z0 - o), V(x1 + o, eave - o * pitch, z0 - o), V(x1 + o, ridge, zm), V(x0 - o, ridge, zm), { seams: false, thick: 0.5 });
      P.roofPlane(M, V(x1 + o, eave - o * pitch, z1 + o), V(x0 - o, eave - o * pitch, z1 + o), V(x0 - o, ridge, zm), V(x1 + o, ridge, zm), { seams: false, thick: 0.5 });
      for (const x of [x0, x1]) {
        const wl = new P.Wall(V(x, 0, z1), V(0, 0, -1), V(x === x0 ? -1 : 1, 0, 0));
        M.add(wl.slab([[0, eave], [z1 - z0, eave], [(z1 - z0) / 2, ridge - 0.4]], [], -T, 0), 'siding');
      }
    }
    // windows on the outside faces, two floors, about every 9 ft
    M.el = 'windows';
    const faces = [[x0, z0, x1, z0, 0, -1], [x0, z1, x1, z1, 0, 1], [x0, z0, x0, z1, -1, 0], [x1, z0, x1, z1, 1, 0]];
    for (const [ax0, az0, ax1, az1, nx, nz] of faces) {
      const L = Math.hypot(ax1 - ax0, az1 - az0), n = Math.floor((L - 4) / 9);
      for (let i = 0; i < n; i++) {
        const t = (i + 0.5) / n, x = ax0 + (ax1 - ax0) * t, z = az0 + (az1 - az0) * t, ox = x + nx * 1.5, oz = z + nz * 1.5;
        if (inside(ox, oz, k) || inside(x + nx * 0.2, z + nz * 0.2, k)) continue;
        const along = nx === 0, porchSide = inPorch(ox, oz);
        for (const [v0, v1] of porchSide ? [[13, 18.2]] : [[4.2, 10.2], [13, 18.2]]) {
          const w = 3.2, bx = (u0, u1, v0_, v1_, w0, w1) => along ? P.abox(x + u0, v0_, z + nz * w0, x + u1, v1_, z + nz * w1) : P.abox(x + nx * w0, v0_, z + u0, x + nx * w1, v1_, z + u1);
          M.add(bx(-w / 2 - 0.4, w / 2 + 0.4, v0 - 0.35, v1 + 0.4, 0.0, 0.06), 'trim');       // casing
          M.add(bx(-w / 2, w / 2, v0, v1, 0.06, 0.12), 'frame');                               // dark sash behind the glass
          M.add(bx(-w / 2 + 0.15, w / 2 - 0.15, v0 + 0.15, v1 - 0.15, 0.12, 0.16), 'glass');
          M.add(bx(-w / 2, w / 2, (v0 + v1) / 2 - 0.08, (v0 + v1) / 2 + 0.08, 0.12, 0.2), 'trim');   // meeting rail
        }
      }
    }
    M.el = null;
  });
  // chimneys that stay
  for (const [x, z, h] of [[47, 20, 36], [94, 33, 37]]) M.add(P.abox(x - 1.5, 18, z - 2, x + 1.5, h, z + 2), 'concrete');

  // ---------------------------------------------------------------- new work: glazed porch, conservatory, elevator
  M.phase = 'new';
  M.el = 'glass';
  { // porch: storefront on the deck side, low roof
    const [x0, z0, x1, z1] = porch, h = 12;
    M.add(P.abox(x0, FL - 0.3, z0, x1, FL, z1), 'slab');
    for (let x = x0; x <= x1 - 1; x += 6) {   // storefront bays
      M.add(P.abox(x + 0.3, FL, z1 - 0.15, x + 5.7, h - 0.5, z1 + 0.05), 'glass');
      M.add(P.abox(x - 0.2, FL, z1 - 0.3, x + 0.3, h, z1 + 0.2), 'frame');
    }
    M.add(P.abox(x0, FL, z0 + 0.5, x0 + 0.4, h, z1), 'glass'); M.add(P.abox(x1 - 0.4, FL, z0 + 0.5, x1, h, z1), 'glass');
    M.add(P.abox(x0 - 1, h, z0, x1 + 1, h + 0.8, z1 + 1.2), 'roof');
    M.add(P.abox(x0 - 1, h - 0.6, z1 + 0.6, x1 + 1, h, z1 + 1.2), 'trim');
  }
  { // conservatory: glass gable roof over the courtyard between the wings
    const x0 = 41, x1 = 51, z0 = 64, z1 = 97, eave = 15, xm = 46, ridge = 20;
    M.add(P.abox(x0, FL - 0.3, z0, x1, FL, z1), 'slab');
    P.roofPlane(M, V(x0 - 0.3, eave, z1), V(x0 - 0.3, eave, z0), V(xm, ridge, z0), V(xm, ridge, z1), { seams: false, thick: 0.12, mat: 'glass', soffit: 'glass', fascia: false });
    P.roofPlane(M, V(x1 + 0.3, eave, z0), V(x1 + 0.3, eave, z1), V(xm, ridge, z1), V(xm, ridge, z0), { seams: false, thick: 0.12, mat: 'glass', soffit: 'glass', fascia: false });
    for (let z = z0; z <= z1 + 0.1; z += 3.3) {   // rafters
      for (const [a, b] of [[V(x0 - 0.3, eave + 0.1, z), V(xm, ridge + 0.1, z)], [V(x1 + 0.3, eave + 0.1, z), V(xm, ridge + 0.1, z)]]) {
        const d = b.clone().sub(a), L = d.length();
        M.add(P.obox(a.clone().addScaledVector(d, 0.5), d.clone().normalize(), V(0, 0, 1), new THREE.Vector3().crossVectors(d.clone().normalize(), V(0, 0, 1)).normalize(), L, 0.25, 0.3), 'frame');
      }
    }
    M.add(P.abox(xm - 0.15, ridge, z0, xm + 0.15, ridge + 0.4, z1), 'frame');
    M.add(P.abox(x0, FL, z1 - 0.2, x1, eave, z1), 'glass');   // glazed end at the porch
  }
  M.el = 'elevator';
  { const x0 = 44, z0 = 58, x1 = 52, z1 = 66;
    for (const [a, b, c, d] of [[x0, z0, x1, z0 + 0.7], [x0, z1 - 0.7, x1, z1], [x0, z0 + 0.7, x0 + 0.7, z1 - 0.7], [x1 - 0.7, z0 + 0.7, x1, z1 - 0.7]]) M.add(P.abox(a, FL, b, c, 37, d), 'siding');
    M.add(P.abox(x0 - 0.6, 37, z0 - 0.6, x1 + 0.6, 38, z1 + 0.6), 'roof');
  }
  M.el = null;

  // ---------------------------------------------------------------- site: deck, terraces, pergola, fire pit, geothermal field
  M.phase = 'site';
  M.el = 'deck';
  { const x0 = 10, x1 = 90;   // stepped Kebony deck, three tiers down toward the lawn
    M.add(P.abox(x0 + 6, 0.6, 110, x1 - 4, FL - 0.05, 136), 'deck');
    M.add(P.abox(x0 + 3, 0.2, 136, x1 - 2, 1.0, 140), 'deck');
    M.add(P.abox(x0, -0.2, 140, x1, 0.5, 145), 'deck');
    M.add(P.abox(48, 0.6, 118, 56, 3.4, 136), 'concrete');   // planter
  }
  M.el = 'terrace';
  { M.add(P.abox(86, 0.0, 99, 112, 0.6, 128), 'concrete');                  // bluestone terrace
    M.add(P.abox(86, 0.0, 99, 112, 2.6, 100.2), 'concrete');                // stone seat wall
    for (let x = 88; x <= 110; x += 5.5) for (const z of [102, 112, 122]) M.add(P.abox(x - 0.3, 0.6, z - 0.3, x + 0.3, 10, z + 0.3), 'timber');
    for (const z of [102, 112, 122]) M.add(P.abox(87, 10, z - 0.25, 111, 10.8, z + 0.25), 'timber');
    for (let x = 88; x <= 110; x += 2) M.add(P.abox(x - 0.12, 10.8, 100.5, x + 0.12, 11.3, 123.5), 'timber');
    M.add(P.cyl(100, 0, 137, 3.5, 1.8, 28), 'concrete');                   // fire pit
  }
  M.el = 'geo';
  { for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) {
      const x = 128 + i * 11, z = 58 + j * 11;
      M.add(P.cyl(x, -10, z, 0.35, 0.05, 10), 'steel');
      M.add(P.cyl(x, 0.02, z, 1.1, 0.25, 20), 'steel');
    }
    M.add(P.abox(107, 0.02, 74, 124, 0.2, 76), 'steel');       // header to the building
    M.add(P.abox(124, 0.02, 57, 126, 0.2, 92), 'steel');
    for (let j = 0; j < 4; j++) M.add(P.abox(126, 0.02, 57.6 + j * 11, 161, 0.2, 58.6 + j * 11), 'steel');
  }
  M.el = null;
  return M.group();
}
