// The Cooper Pool House, Crisp Architects Pool House SK4, A1.1 and A1.2 (October 14, 2026), modeled for the presentation.
// Plan 35'-6" x 16'-0" from A1.1. Heights from the A1.1/A1.2 elevations: 1st floor T.O.P. 9'-1 1/8", 2nd floor S-FL 9'-11 3/8",
// 2nd floor T.O.P. 19'-0 1/2", ridge 26'-6". Opening sizes and positions from the plan dimension strings and elevations.
// x east, y up, z south. West wall x = 0, east wall x = 16, south face z = 0, north face z = -35.5.
import * as THREE from 'three';
import * as P from '../../kit/tools/glb/parts.js';

export default function build() {
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const M = new P.Model(P.materials({
    siding: { color: '#dddbd4', roughness: 0.8 },     // 6" smooth Hardie lap, painted white
    trim: { color: '#f4f3ef', roughness: 0.7 },       // Claymark Solid Gold, painted white
    frame: { color: '#f2f1ed', roughness: 0.5 },      // Marvin Ultimate, white clad
    soffit: { color: '#e6e4de', roughness: 0.8 },
    shingle: { color: '#4a4741', roughness: 0.9 },    // cedar shingles to match the main house
    shingleDk: { color: '#34322f', roughness: 0.95 },
    turf: { color: '#5f7a3f', roughness: 1 },
    cab: { color: '#5d6f82', roughness: 0.6 },        // painted inset Shaker bar cabinets
    oak: { color: '#c9a77c', roughness: 0.55 },
    gypIn: { color: '#cdc7bc', roughness: 0.9 },      // interior finish faces, a step darker so the glass reads
    linen: { color: '#d8d1c4', roughness: 0.95 },     // upholstery seen through the glass
  }));
  const L = 35.5, W = 16, FL = 0.25;                       // floor 3" above the terrace
  const T1 = FL + 9.09, F2 = FL + 9.95, T2 = FL + 19.04, RIDGE = FL + 26.5;
  const SLOPE = (26.5 - 19.04) / 8;                        // 11.2:12
  const yRoof = (x) => RIDGE - SLOPE * Math.abs(x - W / 2); // top of roof at x
  const gTop = (u) => yRoof(u) - 0.45;                     // gable wall top under the roof (south and north walls, u = x or 16 - x)

  // ---------------------------------------------------------------- site: pool terrace, raised grade north and east, stone walls
  M.phase = 'site';
  M.add(P.abox(-10, -0.06, -30, -0.03, 0.02, 8), 'stone');               // bluestone pool terrace to the west
  M.add(P.abox(-0.03, -0.06, 0.03, 17.0, 0.02, 8), 'stone');              // and to the south
  for (let x = -8.6; x < -0.6; x += 2.0) M.add(P.abox(x - 0.03, 0.02, -30, x + 0.03, 0.03, 8), 'gravel');   // bluestone joints
  for (let z = -28.6; z < 8; z += 2.0) M.add(P.abox(-10, 0.02, z - 0.03, -0.6, 0.03, z + 0.03), 'gravel');
  for (let x = 1.4; x < 17; x += 2.0) M.add(P.abox(x - 0.03, 0.02, 0.6, x + 0.03, 0.03, 8), 'gravel');
  for (let z = 2.6; z < 8; z += 2.0) M.add(P.abox(-0.6, 0.02, z - 0.03, 17.0, 0.03, z + 0.03), 'gravel');
  M.add(P.abox(17.0, 0, -44, 18.4, 2.4, 8), 'stone');                   // existing stone retaining wall to remain, east side
  M.add(P.abox(18.4, 0, -44, 26, 2.4, 8), 'turf');
  M.add(P.abox(-4.2, 0, -44, 17.0, 2.4, -35.75), 'turf');                // raised grade north of the pool house
  M.add(P.abox(-10, 0, -44, -4.2, 2.4, -30.15), 'turf');                 // and to the northwest, faced in stone
  M.add(P.abox(-10, 0, -30.15, -4.2, 2.4, -30.0), 'stone');
  M.add(P.abox(-4.35, 0, -35.75, -4.2, 2.4, -30.15), 'stone');
  // west exterior stair from the terrace up to the north grade: stone veneer, 2" bluestone treads
  for (let i = 0; i < 5; i++) {
    const y = 0.48 * (i + 1), z0 = -30 - i * 1.15;
    M.add(P.abox(-4.2, 0, -35.75, -0.7, y - 0.17, z0), 'stone');
    M.add(P.abox(-4.25, y - 0.17, z0 - 1.15, -0.65, y, z0 + 0.12), 'slab');
  }

  // ---------------------------------------------------------------- foundation
  // As carried in the estimate: 24x12 footings, 10" frost walls 48" deep, the east and north walls carried up about 2'-6"
  // against the raised grade, a 4" slab on vapor barrier, R-10 rigid and 6" gravel.
  M.phase = 'foundation';
  const WT = 0.83, FW = 2.0, FD = 1.0, BOT = -4.0;
  const walls = [['S', -0.03, 0.03 - WT, W + 0.03, 0.03, FL], ['N', -0.03, -L - 0.03, W + 0.03, -L - 0.03 + WT, FL],
                 ['W', -0.03, -L - 0.03 + WT, -0.03 + WT, 0.03 - WT, FL], ['E', W + 0.03 - WT, -L - 0.03 + WT, W + 0.03, 0.03 - WT, FL]];
  for (const [k, x0, z0, x1, z1, top] of walls) {
    M.add(P.abox(x0, BOT, z0, x1, top, z1), 'concrete');
    const cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
    if (k === 'S' || k === 'N') M.add(P.abox(x0 - 0.6, BOT - FD, cz - FW / 2, x1 + 0.6, BOT, cz + FW / 2), 'footing');
    else M.add(P.abox(cx - FW / 2, BOT - FD, z0 + 0.6, cx + FW / 2, BOT, z1 - 0.6), 'footing');
  }
  M.add(P.abox(0.82, FL - 0.33, -L + 0.82, W - 0.82, FL - 0.02, -0.82), 'slab');
  M.add(P.abox(0.82, FL - 0.83, -L + 0.82, W - 0.82, FL - 0.33, -0.82), 'gravel');

  // ---------------------------------------------------------------- shared wall helpers
  const SOUTH = new P.Wall(V(0, 0, 0), V(1, 0, 0), V(0, 0, 1));
  const NORTH = new P.Wall(V(W, 0, -L), V(-1, 0, 0), V(0, 0, -1));
  const WEST = new P.Wall(V(0, 0, -L), V(0, 0, 1), V(-1, 0, 0));
  const EAST = new P.Wall(V(W, 0, 0), V(0, 0, -1), V(1, 0, 0));
  const spanAtV = (poly, v) => {   // u range of a wall outline at height v
    const us = [];
    for (let i = 0; i < poly.length; i++) {
      const [a, b] = [poly[i], poly[(i + 1) % poly.length]];
      if ((a[1] <= v && b[1] > v) || (b[1] <= v && a[1] > v)) us.push(a[0] + (b[0] - a[0]) * (v - a[1]) / (b[1] - a[1]));
    }
    us.sort((p, q) => p - q); return us.length >= 2 ? [us[0] + 0.05, us[us.length - 1] - 0.05] : null;
  };
  const polySlab = (wall, poly, holes, w0, w1) => {   // a wall slab with polygon holes (shaped gable units)
    const sh = new THREE.Shape(poly.map(([u, v]) => new THREE.Vector2(u, v)));
    for (const h of holes) sh.holes.push(new THREE.Path(h.map(([u, v]) => new THREE.Vector2(u, v))));
    const g = new THREE.ExtrudeGeometry(sh, { depth: w1 - w0, bevelEnabled: false, curveSegments: 1 });
    g.translate(0, 0, w0);
    const m = new THREE.Matrix4().makeBasis(wall.U, wall.Y, wall.N); m.setPosition(wall.o); g.applyMatrix4(m);
    return g;
  };
  const rectPoly = ([u0, u1, v0, v1]) => [[u0, v0], [u1, v0], [u1, v1], [u0, v1]];
  const bboxOf = (p) => [Math.min(...p.map((q) => q[0])), Math.max(...p.map((q) => q[0])), Math.min(...p.map((q) => q[1])), Math.max(...p.map((q) => q[1]))];
  // 6" smooth lap siding: the board face with the openings cut, a shadow line every 6", stopped at the openings and trim.
  // openings are rects [u0, u1, v0, v1] or polygons [[u, v], ...]
  const lap = (wall, poly, openings, o = {}) => {
    const hp = openings.map((h) => (Array.isArray(h[0]) ? h : rectPoly(h))), hb = hp.map(bboxOf);
    M.add(polySlab(wall, poly, hp, -0.06, 0), 'siding');
    M.add(polySlab(wall, poly, hp, -0.6, -0.06), 'trim');
    M.add(polySlab(wall, poly, hp, -0.64, -0.6), 'gypIn');
    const v0 = Math.min(...poly.map((p) => p[1])), v1 = Math.max(...poly.map((p) => p[1])), pad = 0.36, bands = o.bands || [];
    for (let v = v0 + 0.5; v < v1 - 0.1; v += 0.5) {
      if (bands.some(([a, b]) => v > a - 0.05 && v < b + 0.05)) continue;
      const sp = spanAtV(poly, v); if (!sp) continue;
      let segs = [[sp[0] + (o.cl ?? 0.8), sp[1] - (o.cr ?? 0.8)]];
      for (const h of hb) {
        if (v < h[2] - pad || v > h[3] + pad) continue;
        const out = []; for (const [a, b] of segs) { if (h[1] + pad < a || h[0] - pad > b) { out.push([a, b]); continue; } if (h[0] - pad > a) out.push([a, h[0] - pad]); if (h[1] + pad < b) out.push([h[1] + pad, b]); }
        segs = out;
      }
      for (const [a, b] of segs) if (b - a > 0.2) M.add(wall.box(a, b, v - 0.04, v, 0, 0.05), 'siding');
    }
  };
  const W_ = (wall) => (wall === WEST ? '+west' : '');   // west wall parts carry a second tag, so the cutaways can lift the whole wall
  const glz = (wall, r, o = {}) => { M.el = (o.el || 'win') + W_(wall); P.glazedUnit(M, wall, r, { inset: -0.3, frame: 0.2, cols: 1, rows: 1, ...o }); M.el = null; };
  const cas = (wall, r, o = {}) => { M.el = 'trim' + W_(wall); P.casing(M, wall, r, { width: 0.32, depth: 0.1, ...o }); M.el = null; };
  const casement = (wall, [u0, u1, v0, v1], transom = null) => {   // Marvin Ultimate casement, optional lower transom
    cas(wall, [u0, u1, v0, v1]);
    if (transom) glz(wall, [u0, u1, v0, v1], { panes: [[u0 + 0.2, u1 - 0.2, transom + 0.1, v1 - 0.2, 1, 1], [u0 + 0.2, u1 - 0.2, v0 + 0.24, transom - 0.1, 1, 1]], rails: [transom] });
    else glz(wall, [u0, u1, v0, v1]);
  };
  const unit = (wall, [u0, u1, v0, v1], transom = null) => {   // the glazed unit alone, no casing
    if (transom) glz(wall, [u0, u1, v0, v1], { panes: [[u0 + 0.2, u1 - 0.2, transom + 0.1, v1 - 0.2, 1, 1], [u0 + 0.2, u1 - 0.2, v0 + 0.24, transom - 0.1, 1, 1]], rails: [transom] });
    else glz(wall, [u0, u1, v0, v1]);
  };
  const mullion = (wall, u, v0, v1, w = 0.32) => { M.el = 'trim' + W_(wall); M.add(wall.box(u - w / 2, u + w / 2, v0 + 0.01, v1 - 0.01, 0, 0.12), 'trim'); M.el = null; };
  // ganged units share one casing with a mullion board between them (overlapping casings sit on each other and render black)
  const gang = (wall, u0, n, w, v0, v1, transom) => {
    for (let i = 0; i < n; i++) { const a = u0 + i * w; unit(wall, [a + 0.04, a + w - 0.04, v0, v1], transom); if (i) mullion(wall, a, v0, v1); }
    cas(wall, [u0 + 0.04, u0 + n * w - 0.04, v0, v1]); return [u0, u0 + n * w, v0, v1];
  };
  let shapedN = 0;
  const shaped = (wall, poly, o = {}) => {   // a shaped gable unit: glass slab with a frame along every edge; depths stagger per edge and per unit
    const k = (shapedN++) * 0.02;
    M.el = 'win';
    M.add(wall.slab(poly, [], -0.42, -0.38), 'glass');
    for (let i = 0; i < poly.length; i++) {
      const a = wall.p(poly[i][0], poly[i][1], -0.3), b = wall.p(poly[(i + 1) % poly.length][0], poly[(i + 1) % poly.length][1], -0.3), d = b.clone().sub(a);
      const ax = d.clone().normalize(), az = wall.N.clone(), ay = new THREE.Vector3().crossVectors(az, ax).normalize();
      M.add(P.obox(a.clone().addScaledVector(d, 0.5).addScaledVector(ay, 0.12), ax, ay, az, d.length() + 0.1, 0.22, 0.16 + (i % 2) * 0.012 + k), 'frame');
    }
    M.el = 'trim';
    for (let i = 0; i < poly.length; i++) {
      const a = wall.p(poly[i][0], poly[i][1], 0), b = wall.p(poly[(i + 1) % poly.length][0], poly[(i + 1) % poly.length][1], 0), d = b.clone().sub(a);
      const ax = d.clone().normalize(), az = wall.N.clone(), ay = new THREE.Vector3().crossVectors(az, ax).normalize();
      M.add(P.obox(a.clone().addScaledVector(d, 0.5).addScaledVector(ay, -0.13), ax, ay, az, d.length() + 0.6, 0.3, 0.2 + (i % 2) * 0.015 + k), 'trim');
    }
    M.el = null;
  };
  // Claymark trim: corner boards and pilasters with a cap and base, the belt between floors, the frieze, the skirt
  const pilaster = (wall, u0, u1, v0, v1, d = 0.22) => {
    M.el = 'trim' + W_(wall); const e = EW(wall);
    M.add(wall.box(u0, u1, v0, v1 + e - 0.03, 0, d), 'trim');   // stops under the cap so the two tops never share a face
    M.add(wall.box(u0 - 0.1 - e, u1 + 0.1 + e, v0, v0 + 0.7 + e, 0, d + 0.08 + e), 'trim');             // base
    M.add(wall.box(u0 - 0.12 - e, u1 + 0.12 + e, v1 - 0.55 + e, v1 - 0.35 + e, 0, d + 0.1 + e), 'trim');     // cap
    M.add(wall.box(u0 - 0.18 - e, u1 + 0.18 + e, v1 - 0.35 + e, v1 + e, 0, d + 0.16 + e), 'trim');
    M.el = null;
  };
  const LD = FL + 5.0;                                     // entry landing at door 1
  const BELT = [T1 - 0.3, F2 + 0.05];                       // entablature between floors
  const EW = (wall) => (wall === WEST || wall === EAST ? 0.012 : 0);
  const skirt = (wall, u0, u1) => { M.el = 'trim' + W_(wall); M.add(wall.box(u0, u1, FL, FL + 0.85 + EW(wall), 0, 0.12), 'trim'); M.el = null; };
  const belt = (wall, u0, u1) => {
    M.el = 'trim' + W_(wall); const e = EW(wall);
    M.add(wall.box(u0, u1, BELT[0] + e, BELT[1] - 0.3 + e, 0, 0.18), 'trim');
    M.add(wall.box(u0 - 0.25, u1 + 0.25, BELT[1] - 0.3 + e, BELT[1] - 0.12 + e, 0, 0.42), 'trim');
    M.add(wall.box(u0 - 0.35, u1 + 0.35, BELT[1] - 0.12 + e, BELT[1] + e, 0, 0.6), 'trim');
    M.el = null;
  };

  // ---------------------------------------------------------------- first floor walls, doors and windows
  M.phase = 'first';
  // west wall (seen from the west, u runs north to south): Reeb storage pair 4, bifold window 108 over the bar counter, bifold door 3
  const dW4 = [8.9, 13.9, FL, FL + 7.94], w108 = [15.75, 24.75, FL + 3.0, FL + 8.04], d3 = [25.7, 34.7, FL, FL + 7.96];
  M.el = 'cutwall'; lap(WEST, [[0, FL], [L, FL], [L, T1 + 0.2], [0, T1 + 0.2]], [dW4, w108, d3], { bands: [[FL, FL + 0.85]] }); M.el = null;
  // east wall (u runs south to north): two gangs of three casements and unit 101 at the stair
  const eA = [0.65, 9.65, FL + 2.5, FL + 7.875], eB = [10.67, 19.67, FL + 2.5, FL + 7.875], e101 = [26.27, 29.27, FL + 2.5, FL + 7.875];
  lap(EAST, [[0, FL], [L, FL], [L, T1 + 0.2], [0, T1 + 0.2]], [eA, eB, e101], { bands: [[FL, FL + 0.85]] });
  gang(EAST, 0.65, 3, 3, FL + 2.5, FL + 7.875); gang(EAST, 10.67, 3, 3, FL + 2.5, FL + 7.875); casement(EAST, e101);
  // south wall: bifold door 2 across the gable end
  const d2 = [0.95, 15.05, FL, FL + 7.96];
  // north wall: door 1 at the entry landing, 5'-0" above the floor
  const d1 = [6.44, 9.56, FL + 5.0, FL + 13.17];
  lap(NORTH, [[0, FL], [W, FL], [W, T1 + 0.2], [9.56, T1 + 0.2], [9.56, FL + 5.0], [6.44, FL + 5.0], [6.44, T1 + 0.2], [0, T1 + 0.2]], [], { bands: [[FL, FL + 0.85]], cl: 0.85, cr: 0.85 });
  skirt(WEST, -0.2, L + 0.2); skirt(EAST, -0.2, L + 0.2); skirt(NORTH, -0.2, W + 0.2);
  // bifolds: door 2 (four panels), door 3 (three panels), window 108 (bar pass-through)
  const bf = (wall, r, leaves, rows = 1) => {
    cas(wall, r, { width: 0.4, sill: false });
    const [u0, u1, v0, v1] = r, lw = (u1 - u0) / leaves, panes = [], stiles = [];
    for (let i = 0; i < leaves; i++) { const a = u0 + i * lw; if (i) stiles.push(a); panes.push([a + 0.2, a + lw - 0.2, v0 + 0.3, v1 - 0.2, 1, rows]); }
    glz(wall, r, { el: 'bifold', panes, stiles, stileW: 0.3, frame: 0.22, inset: -0.32 });
  };
  bf(SOUTH, d2, 4); bf(WEST, d3, 3); bf(WEST, w108, 4);
  // Reeb storage doors: painted wood pair with X bracing and a glazed upper half, as drawn
  {
    const [u0, u1, v0, v1] = dW4; cas(WEST, dW4, { sill: false }); M.el = 'cutwall';
    M.add(WEST.box(u0 + 0.02, u1 - 0.02, v0, v1 - 0.02, -0.3, -0.18), 'trim');
    const mid = (u0 + u1) / 2;
    for (const [a, b] of [[u0 + 0.15, mid - 0.04], [mid + 0.04, u1 - 0.15]]) {
      M.add(WEST.box(a, b, v0 + 0.12, v0 + 0.32, -0.18, -0.12), 'trim'); M.add(WEST.box(a, b, v0 + 3.25, v0 + 3.45, -0.18, -0.12), 'trim');
      M.add(WEST.box(a, a + 0.18, v0, v1 - 0.1, -0.18, -0.12), 'trim'); M.add(WEST.box(b - 0.18, b, v0, v1 - 0.1, -0.18, -0.12), 'trim');
      for (const [p, q] of [[[a, v0 + 0.32], [b, v0 + 3.25]], [[b, v0 + 0.32], [a, v0 + 3.25]]]) {
        const A = WEST.p(p[0], p[1], -0.15), Bq = WEST.p(q[0], q[1], -0.15), dd = Bq.clone().sub(A);
        M.add(P.obox(A.clone().addScaledVector(dd, 0.5), dd.clone().normalize(), new THREE.Vector3().crossVectors(WEST.N, dd).normalize(), WEST.N, dd.length(), 0.18, 0.06), 'trim');
      }
      M.add(WEST.box(a + 0.18, b - 0.18, v0 + 3.6, v1 - 0.25, -0.24, -0.22), 'glass');
      M.add(WEST.box(a, b, v1 - 0.25, v1 - 0.1, -0.18, -0.12), 'trim');
    }
  }
  M.el = null;
  // pilasters and corner boards, first floor
  pilaster(WEST, -0.2, 0.75, FL, T1 + 0.1); pilaster(WEST, L - 0.75, L + 0.2, FL, T1 + 0.1);
  pilaster(WEST, 14.25, 15.2, FL, T1 + 0.1); pilaster(WEST, 24.95, 25.5, FL, T1 + 0.1);
  pilaster(EAST, -0.2, 0.55, FL, T1 + 0.1); pilaster(EAST, 9.8, 10.55, FL, T1 + 0.1); pilaster(EAST, L - 0.75, L + 0.2, FL, T1 + 0.1);
  pilaster(SOUTH, -0.2, 0.85, FL, T1 + 0.1); pilaster(SOUTH, W - 0.85, W + 0.2, FL, T1 + 0.1);
  pilaster(NORTH, -0.2, 0.75, FL, T1 + 0.1); pilaster(NORTH, W - 0.75, W + 0.2, FL, T1 + 0.1);
  M.el = 'trim';
  M.add(SOUTH.box(0.85, W - 0.85, d2[3] + 0.4, T1 + 0.1, -0.05, 0.12), 'trim');   // header panel over the bifold
  M.el = null;
  // second floor frame: 9 1/2" TJI on a rim, white oak above
  M.el = 'floor2'; M.add(P.abox(0.6, T1 - 0.05, -26.1, W - 0.6, F2 - 0.15, -0.6), 'lumber'); M.add(P.abox(3.9, T1 - 0.05, -30.9, 11.7, F2 - 0.15, -26.1), 'lumber'); M.el = null;   // open at the stair

  // ---------------------------------------------------------------- second floor walls, windows and the gables
  M.phase = 'second';
  const B = [F2 + 0.2, FL + 17.3], TR = FL + 11.9;        // 3'-0" x 7'-3" casements with a lower transom
  const sW = [[2.67, 5.67, FL + 11.6, FL + 16.95], [9.79, 12.79, FL + 11.6, FL + 16.95]];   // 219, 218
  M.el = 'cutwall'; lap(WEST, [[0, F2 + 0.05], [L, F2 + 0.05], [L, T2 - 0.4], [0, T2 - 0.4]], [...sW, [15.83, 24.83, B[0], B[1]], [25.85, 34.85, B[0], B[1]]]); M.el = null;
  for (const r of sW) casement(WEST, r);
  gang(WEST, 15.83, 3, 3, B[0], B[1], TR); gang(WEST, 25.85, 3, 3, B[0], B[1], TR);
  const sE = [[2.67, 5.67, FL + 11.6, FL + 16.95], [9.79, 12.79, FL + 11.6, FL + 16.95]].map(([a, b, c, d]) => [L - b, L - a, c, d]);   // 201, 202
  lap(EAST, [[0, F2 + 0.05], [L, F2 + 0.05], [L, T2 - 0.4], [0, T2 - 0.4]], [...sE, [0.65, 9.65, B[0], B[1]], [10.67, 19.67, B[0], B[1]]]);
  for (const r of sE) casement(EAST, r);
  gang(EAST, 0.65, 3, 3, B[0], B[1], TR); gang(EAST, 10.67, 3, 3, B[0], B[1], TR);
  // south gable: 211, 210, 209 across the end with 223, 222, 221 above, all glass between the corner boards
  const g = (u) => gTop(u);
  unit(SOUTH, [0.95, 3.9, B[0], B[1]], TR); unit(SOUTH, [12.1, 15.05, B[0], B[1]], TR); unit(SOUTH, [4.1, 11.9, B[0], B[1]], TR);
  cas(SOUTH, [0.95, 15.05, B[0], B[1]]); mullion(SOUTH, 4.0, B[0], B[1]); mullion(SOUTH, 12.0, B[0], B[1]);
  M.el = 'trim'; M.add(SOUTH.box(0.85, W - 0.85, B[1] + 0.05, B[1] + 0.42, 0, 0.14), 'trim'); M.el = null;   // transom bar under the gable units
  const yS = B[1] + 0.5, rk = (u) => g(u) - 0.75;
  const sG = [[[0.95, yS], [3.9, yS], [3.9, rk(3.9)], [0.95, rk(0.95)]], [[4.1, yS], [11.9, yS], [11.9, rk(11.9) - 0.4], [8, rk(8) - 0.4], [4.1, rk(4.1) - 0.4]],
              [[12.1, yS], [15.05, yS], [15.05, rk(15.05)], [12.1, rk(12.1)]]];
  lap(SOUTH, [[0, F2 + 0.05], [W, F2 + 0.05], [W, T2 - 0.2], [W / 2, g(W / 2)], [0, T2 - 0.2]], [[0.95, 3.9, B[0], B[1]], [4.1, 11.9, B[0], B[1]], [12.1, 15.05, B[0], B[1]], ...sG], { cl: 0.85, cr: 0.85 });
  for (const p of sG) shaped(SOUTH, p);
  // north gable: siding, the copper roof canopy over door 1 on brackets, unit 220 in the gable
  const nG = [[4.15, T2 + 0.3], [11.85, T2 + 0.3], [11.85, T2 + 2.9], [8, T2 + 5.3], [4.15, T2 + 2.9]];
  lap(NORTH, [[0, F2 + 0.05], [6.44, F2 + 0.05], [6.44, d1[3]], [9.56, d1[3]], [9.56, F2 + 0.05], [W, F2 + 0.05], [W, T2 - 0.2], [W / 2, g(W / 2)], [0, T2 - 0.2]], [nG], { cl: 0.85, cr: 0.85 });
  shaped(NORTH, nG);
  // door 1: Marvin Ultimate swing door, full height glass, at the landing
  cas(NORTH, d1, { sill: false }); glz(NORTH, d1, { el: 'win', panes: [[d1[0] + 0.3, d1[1] - 0.3, d1[2] + 1.2, d1[3] - 0.3, 1, 1]] });
  M.add(NORTH.box(d1[0] + 0.1, d1[1] - 0.1, d1[2], d1[2] + 1.1, -0.3, -0.2), 'frame');
  // pilasters and corner boards, second floor, the belt between floors and the frieze under the eaves
  pilaster(WEST, -0.2, 0.75, F2 + 0.03, T2 - 0.6); pilaster(WEST, L - 0.75, L + 0.2, F2 + 0.03, T2 - 0.6); pilaster(WEST, 25.0, 25.7, F2 + 0.03, T2 - 0.6);
  pilaster(EAST, -0.2, 0.55, F2 + 0.03, T2 - 0.6); pilaster(EAST, 9.8, 10.55, F2 + 0.03, T2 - 0.6); pilaster(EAST, L - 0.75, L + 0.2, F2 + 0.03, T2 - 0.6);
  pilaster(SOUTH, -0.2, 0.85, F2 + 0.03, T2 - 0.6); pilaster(SOUTH, W - 0.85, W + 0.2, F2 + 0.03, T2 - 0.6);
  pilaster(NORTH, -0.2, 0.75, F2 + 0.03, T2 - 0.6); pilaster(NORTH, W - 0.75, W + 0.2, F2 + 0.03, T2 - 0.6);
  belt(WEST, -0.2, L + 0.2); belt(EAST, -0.2, L + 0.2); belt(SOUTH, -0.2, W + 0.2); belt(NORTH, -0.2, 6.05); belt(NORTH, 9.95, W + 0.2);
  M.el = 'trim';
  for (const w of [WEST, EAST]) { M.el = 'trim' + W_(w); M.add(w.box(-0.25, L + 0.25, T2 - 1.3, T2 - 0.6, 0, 0.16), 'trim'); }
  M.el = 'trim';
  M.el = null;

  // ---------------------------------------------------------------- roof: cedar shingles, copper drip edge, gutters and leaders, mitered rakes
  M.phase = 'roof';
  M.el = 'roof';
  const eav = 1.17, rkz = 0.75, yE = yRoof(-eav), yR = RIDGE;
  const pW = P.roofPlane(M, V(-eav, yE, -L - rkz), V(-eav, yE, rkz), V(W / 2, yR, rkz), V(W / 2, yR, -L - rkz), { seams: false, mat: 'shingle', soffit: 'soffit', fasciaH: 0.6 });
  const pE = P.roofPlane(M, V(W + eav, yE, rkz), V(W + eav, yE, -L - rkz), V(W / 2, yR, -L - rkz), V(W / 2, yR, rkz), { seams: false, mat: 'shingle', soffit: 'soffit', fasciaH: 0.6 });
  for (const [eL, eR, pl] of [[V(-eav, yE, -L - rkz), V(-eav, yE, rkz), pW], [V(W + eav, yE, rkz), V(W + eav, yE, -L - rkz), pE]]) {   // shingle courses, 5" exposure
    for (let s = 0.42; s < pl.H - 0.3; s += 0.42) {
      const c = eL.clone().addScaledVector(eR.clone().sub(eL), 0.5).addScaledVector(pl.ay, s).addScaledVector(pl.nz, 0.02);
      M.add(P.obox(c, pl.ax, pl.ay, pl.nz, pl.L, 0.05, 0.06), 'shingleDk');
    }
  }
  M.add(P.obox(V(W / 2, yR + 0.1, -L / 2), V(0, 0, 1), V(0, 1, 0), V(1, 0, 0), L + 2 * rkz + 0.1, 0.24, 0.9), 'shingleDk');   // ridge cap
  for (const z of [rkz, -L - rkz]) {   // mitered rake boards with a copper drip edge
    const out = V(0, 0, z > 0 ? 1 : -1);
    P.rake(M, V(-eav, yE, z), V(W / 2, yR, z), { out, h: 0.75 }); P.rake(M, V(W + eav, yE, z), V(W / 2, yR, z), { out, h: 0.75 });
    P.rake(M, V(-eav, yE + 0.06, z + (z > 0 ? 0.08 : -0.08)), V(W / 2, yR + 0.06, z + (z > 0 ? 0.08 : -0.08)), { out, h: 0.1, mat: 'flashing', lift: 0.02 });
    P.rake(M, V(W + eav, yE + 0.06, z + (z > 0 ? 0.08 : -0.08)), V(W / 2, yR + 0.06, z + (z > 0 ? 0.08 : -0.08)), { out, h: 0.1, mat: 'flashing', lift: 0.02 });
  }
  for (const z of [rkz + 0.02, -L - rkz - 0.02]) { const o = z > 0 ? 1 : -1; M.add(P.abox(W / 2 - 0.32, yR - 0.95, Math.min(z, z + o * 0.24), W / 2 + 0.32, yR - 0.02, Math.max(z, z + o * 0.28)), 'trim'); }   // peak block where the rakes meet
  // 6" half-round copper gutters on both eaves, 4" copper leaders at the four corners
  P.gutter(M, V(-eav - 0.05, yE - 0.55, -L - rkz), V(-eav - 0.05, yE - 0.55, rkz), V(-1, 0, 0), { r: 0.25 });
  P.gutter(M, V(W + eav + 0.05, yE - 0.55, rkz), V(W + eav + 0.05, yE - 0.55, -L - rkz), V(1, 0, 0), { r: 0.25 });
  const pipe = (a, b, r) => { const d = b.clone().sub(a), g = new THREE.CylinderGeometry(r, r, d.length(), 12); g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), d.clone().normalize())); g.translate(...a.clone().addScaledVector(d, 0.5).toArray()); M.add(g, 'flashing'); };
  for (const [xs, z] of [[-1, 0.62], [-1, -L - 0.62], [1, 0.62], [1, -L - 0.62]]) {   // on the corner diagonal, clear of the belt and the bifolds
    const xw = xs < 0 ? -0.8 : W + 0.8, xg = xs < 0 ? -eav - 0.3 : W + eav + 0.3, yT = yE - 1.8;
    P.downspout(M, xw, z, yT, { r: 0.17 });
    pipe(V(xg, yE - 0.6, z), V(xg, yE - 1.0, z), 0.17); pipe(V(xg, yE - 1.0, z), V(xw, yT, z), 0.17);
  }
  // copper canopy over door 1 on two brackets
  P.roofPlane(M, V(10.6, d1[3] + 0.9, -L - 2.6), V(5.4, d1[3] + 0.9, -L - 2.6), V(5.4, d1[3] + 1.5, -L), V(10.6, d1[3] + 1.5, -L), { seam: 0.85, mat: 'flashing', fasciaH: 0.45 });
  M.el = 'trim';
  M.add(P.abox(5.4, d1[3] + 0.2, -L - 2.55, 10.6, d1[3] + 0.85, -L - 2.1), 'trim');
  for (const x of [5.9, 10.1]) {
    M.add(P.abox(x - 0.25, d1[3] - 1.9, -L - 0.5, x + 0.25, d1[3] + 0.85, -L), 'trim');
    const a = V(x, d1[3] - 1.5, -L - 0.4), b = V(x, d1[3] + 0.25, -L - 2.3), dd = b.clone().sub(a);
    M.add(P.obox(a.clone().addScaledVector(dd, 0.5), dd.clone().normalize(), new THREE.Vector3().crossVectors(V(1, 0, 0), dd).normalize(), V(1, 0, 0), dd.length(), 0.45, 0.4), 'trim');
  }
  // cornice returns at the four gable corners
  for (const [x0, x1, z0, z1] of [[-eav, 1.0, -0.2, rkz], [W - 1.0, W + eav, -0.2, rkz], [-eav, 1.0, -L - rkz, -L + 0.2], [W - 1.0, W + eav, -L - rkz, -L + 0.2]]) {
    M.add(P.abox(x0, yE - 1.25, z0, x1, yE - 0.62, z1), 'trim');
    M.add(P.abox(x0 - 0.1, yE - 0.62, z0 - 0.05, x1 + 0.1, yE - 0.42, z1 + 0.05), 'trim');
  }
  M.el = null;

  // ---------------------------------------------------------------- interior, seen through the glass
  M.phase = 'interior';
  M.add(P.abox(0.65, FL - 0.02, -L + 0.65, W - 0.65, FL + 0.02, -0.65), 'stone');                 // stone floor to match the terrace
  M.el = 'floor2'; M.add(P.abox(0.65, F2 - 0.15, -26.1, W - 0.65, F2, -0.65), 'oak');                             // 6" white oak, second floor
  M.add(P.abox(3.9, F2 - 0.15, -30.9, 11.7, F2, -26.1), 'oak'); M.el = null;
  // vaulted ceiling under the rafters
  for (const sx of [-1, 1]) {
    const a = V(sx < 0 ? 0.65 : W - 0.65, T2 - 0.3, -L / 2), b = V(W / 2, RIDGE - 1.4, -L / 2), d = b.clone().sub(a);
    const ay = d.clone().normalize(), az = new THREE.Vector3().crossVectors(V(0, 0, 1), ay).normalize();
    M.add(P.obox(a.clone().addScaledVector(d, 0.5), V(0, 0, 1), ay, az, L - 1.3, d.length(), 0.05), 'gypIn');
  }
  // bath and storage walls
  // tagged with the west wall so the stair and bar cutaways see past them
  const wallBox = (x0, z0, x1, z1, y1 = T1) => { M.el = 'cutwall'; M.add(P.abox(x0, FL, z0, x1, y1, z1), 'gyp'); M.el = null; };
  wallBox(4.0, -25.4, 12.0, -25.1); wallBox(4.0, -31.0, 4.3, -25.1); wallBox(11.7, -31.0, 12.0, -25.1); wallBox(0.65, -26.6, 4.0, -26.3, LD - 0.3 + 3.0);   // closet wall stops under the up run
  wallBox(4.0, -20.2, 12.0, -19.9, FL + 9.0);
  // the bar: island with seating, back counter with the sink, inner counter at window 108, 3" stone counter outside
  M.el = 'bar';
  M.add(P.abox(3.4, FL, -15.2, 9.4, FL + 3.0, -11.0), 'cab'); M.add(P.abox(3.2, FL + 3.0, -15.4, 9.8, FL + 3.12, -10.4), 'stone');
  M.add(P.abox(2.6, FL, -19.9, 11.8, FL + 3.0, -17.9), 'cab'); M.add(P.abox(2.6, FL + 3.0, -19.9, 11.8, FL + 3.12, -17.7), 'stone');
  for (const y of [FL + 5.2, FL + 6.5]) M.add(P.abox(3.4, y, -19.9, 11.0, y + 0.15, -19.0), 'oak');
  M.add(P.abox(0.65, FL, -19.5, 2.4, FL + 3.0, -11.0), 'cab'); M.add(P.abox(0.65, FL + 3.0, -19.6, 2.5, FL + 3.12, -10.9), 'stone');
  M.add(P.abox(-1.6, FL + 2.95, -19.7, -0.05, FL + 3.2, -10.8), 'stone'); M.add(P.abox(-0.45, FL, -19.4, -0.05, FL + 2.95, -11.1), 'siding');   // 3" stone counter outside window 108 on a sided knee wall
  M.el = null;
  for (const z of [-18.3, -16.2, -14.1, -12.0]) { M.add(P.cyl(-2.6, FL, z, 0.07, FL + 2.5, 8), 'steel'); M.add(P.cyl(-2.6, FL - 0.05, z, 0.42, FL + 0.04, 16), 'steel'); M.add(P.cyl(-2.6, FL + 2.5, z, 0.62, FL + 2.7, 14), 'timber'); }
  for (const z of [-14.6, -12.9, -11.4]) { M.add(P.cyl(10.4, FL, z, 0.07, FL + 2.5, 8), 'steel'); M.add(P.cyl(10.4, FL + 2.5, z, 0.62, FL + 2.7, 14), 'timber'); }
  for (const x of [4.6, 6.4, 8.2]) { M.add(P.cyl(x, FL + 6.4, -13.1, 0.02, T1, 6), 'steel'); M.add(new THREE.SphereGeometry(0.55, 16, 10).translate(x, FL + 6.2, -13.1), 'lamp'); }
  // the white oak stair: entry landing at door 1, one run down along the east wall, one run up along the west wall
  M.el = 'stair';
  const rs = 9.95 / 16;
  M.add(P.abox(0.65, LD - 0.3, -L + 0.65, W - 0.65, LD, -30.9), 'oak');
  for (let i = 1; i <= 7; i++) {   // down: from the landing to the first floor, along the east wall
    const y = LD - i * rs, z0 = -30.9 + (i - 1) * 0.68;
    M.add(P.abox(12.1, y - 0.12, z0, 15.35, y + 0.0, z0 + 0.75), 'oak');
    M.add(P.abox(12.1, FL, z0, 15.35, y - 0.12, z0 + 0.06), 'trim');
  }
  for (let i = 1; i <= 7; i++) {   // up: from the landing to the second floor, along the west wall
    const y = LD + i * rs, z0 = -30.9 + (i - 1) * 0.68;
    M.add(P.abox(0.65, y - 0.12, z0, 3.9, y, z0 + 0.75), 'oak');
    M.add(P.abox(0.65, y - 0.12 - rs, z0, 3.9, y - 0.12, z0 + 0.06), 'trim');
  }
  for (let i = 1; i <= 7; i++) { const y = LD + i * rs, z0 = -30.9 + (i - 1) * 0.68; M.add(P.abox(3.9, FL, z0, 4.05, y + 0.02, z0 + 0.75), 'trim'); }   // closed stringer wall, up run
  M.add(P.abox(0.65, FL, -30.98, 12.1, LD - 0.3, -30.9), 'trim');   // the wall under the landing
  const guard = (a, b, y0) => {   // painted rail, square balusters, oak cap
    const d = b.clone().sub(a), Ln = d.length(), u = d.clone().normalize(), n = V(-u.z, 0, u.x);
    for (let s = 0; s <= Ln; s += 0.33) { const p = a.clone().addScaledVector(u, s); M.add(P.abox(p.x - 0.05, y0, p.z - 0.05, p.x + 0.05, y0 + 3.0, p.z + 0.05), 'trim'); }
    for (const s of [0, Ln]) { const p = a.clone().addScaledVector(u, s); M.add(P.abox(p.x - 0.18, y0, p.z - 0.18, p.x + 0.18, y0 + 3.3, p.z + 0.18), 'trim'); }
    const c = a.clone().addScaledVector(d, 0.5);
    M.add(P.obox(V(c.x, y0 + 3.1, c.z), u, V(0, 1, 0), n, Ln + 0.2, 0.18, 0.3), 'oak');
  };
  guard(V(3.9, 0, -30.9), V(11.7, 0, -30.9), F2); guard(V(3.9, 0, -30.9), V(3.9, 0, -26.1), F2); guard(V(11.7, 0, -30.9), V(11.7, 0, -26.1), F2);
  guard(V(12.1, 0, -30.9), V(12.1, 0, -26.1), LD - 2.0);
  M.el = null;
  // gym and yoga room: mats and a bench, so the glass reads as a room
  M.el = 'floor2';
  for (const x of [5.0, 8.0, 11.0]) { M.add(P.abox(x - 1.0, F2, -4.6, x + 1.0, F2 + 1.45, -2.0), 'linen'); M.add(P.abox(x - 1.0, F2 + 1.45, -4.6, x + 1.0, F2 + 2.7, -4.0), 'linen'); }   // lounge chairs facing the gable
  M.add(P.abox(1.2, F2, -16.0, 3.0, F2 + 1.4, -11.0), 'linen'); M.add(P.abox(1.2, F2 + 1.4, -16.0, 1.75, F2 + 2.6, -11.0), 'linen'); M.el = null;
  for (const z of [-6, -13, -20]) M.add(new THREE.SphereGeometry(0.8, 16, 10).translate(W / 2, RIDGE - 3.4, z), 'lamp');

  // ---------------------------------------------------------------- north entry: 2" bluestone treads and stone veneer up to door 1
  M.phase = 'details';
  for (let i = 0; i < 4; i++) {   // four risers from the north grade up to the landing at door 1
    const y = 2.4 + (i + 1) * ((LD - 2.4) / 4), z1 = -L - 4.4 + i * 1.1;
    M.add(P.abox(4.2, 2.4, z1, 11.8, y - 0.17, -L - 0.03), 'stone');
    M.add(P.abox(4.0, y - 0.17, z1 - 0.06, 12.0, y, -L - 0.03), 'slab');
  }
  return M.group();
}
