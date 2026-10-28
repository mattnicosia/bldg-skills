// The Cooper Barn, Crisp Architects SK-5 (22 September 2026), modeled for the presentation.
// Plan dimensions from SK-5. Heights from the SK-5 front elevation and the Crisp rendering on the
// same sheet, with the 15 ft plate and 9:12 roof carried in the Montana estimate.
// x east, y up, z south. Barn x 0..40, z 0 (south face) .. -30. Wing x 40..56, z -2..-28.
import * as THREE from 'three';
import * as P from '../../kit/tools/glb/parts.js';

export default function build() {
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const M = new P.Model(P.materials());
  const FL = 0.5;                     // top of exposed foundation, bottom of siding
  const PLATE = 15, K = 0.75, RIDGE = 26.25, RT = 0.44;   // roof underside at the wall, 9:12, ridge underside, top offset
  const yTopS = (z) => PLATE + RT + K * (-z);              // barn roof top surface, south slope (z from +1.25 to -15)
  const WIN = (a, b) => [a, b, 3.05, 8.4];
  const DOOR_H = 11.7;                                     // SK-5: transom head 11'-8", leaves 9'-7"
  const LITES = { rowsTop: 2, rowsBottom: 2 };             // 4 over 4 double hungs, as drawn

  // ---------------------------------------------------------------- foundation
  // As carried in the estimate: 12x24 footings, parged 10" walls, the workshop on 4 ft frost walls,
  // a full-height mechanical space under the lounge wing (16 x 26, 9 ft walls), 4" slabs on 6" gravel.
  M.phase = 'foundation';
  const WT = 0.83, FW = 2.0, FD = 1.0;                       // wall 10", footing 24" x 12"
  const ring = (x0, z0, x1, z1, top, bot, skip = []) => {    // four walls with footings under them
    const sides = [['S', x0, z0 - WT, x1, z0], ['N', x0, z1, x1, z1 + WT], ['W', x0, z1 + WT, x0 + WT, z0 - WT], ['E', x1 - WT, z1 + WT, x1, z0 - WT]];   // end walls run between the long walls, so nothing overlaps
    for (const [k, a, b, c, d] of sides) {
      if (skip.includes(k)) continue;
      M.add(P.abox(a, bot, Math.min(b, d), c, top, Math.max(b, d)), 'concrete');
      const cx = (a + c) / 2, cz = (b + d) / 2, along = (k === 'S' || k === 'N');
      M.add(along ? P.abox(a - 0.6, bot - FD, cz - FW / 2, c + 0.6, bot, cz + FW / 2) : P.abox(cx - FW / 2, bot - FD, Math.min(b, d) + 0.6, cx + FW / 2, bot, Math.max(b, d) - 0.6), 'footing');
    }
  };
  ring(-0.06, 0.06, 40.06, -30.06, FL, -3.5);                // workshop frost walls
  ring(40.06, -1.94, 56.06, -28.06, FL, -8.5, ['W']);         // mechanical space walls (the west side is the barn's wall below)
  M.add(P.abox(40.06 - WT, -8.5, -28.06 + WT, 40.06, -3.5, -1.94 - WT), 'concrete');   // barn east wall carried down to the mech floor
  M.add(P.abox(40.06 - WT - 0.4, -9.5, -28.6, 40.06 + 0.4, -8.5, -1.4), 'footing');
  M.add(P.abox(0.8, FL - 0.33, -29.2, 39.2, FL, -0.8), 'slab');           // 4" workshop slab
  M.add(P.abox(0.8, FL - 0.83, -29.2, 39.2, FL - 0.33, -0.8), 'gravel');  // 6" gravel
  M.add(P.abox(40.9, -8.5, -27.2, 55.2, -8.17, -2.8), 'slab');            // mech space slab
  M.add(P.abox(40.9, -9.0, -27.2, 55.2, -8.5, -2.8), 'gravel');
  M.add(P.abox(40.06, FL - 1.0, -28.06 + WT, 56.06 - WT, FL - 0.01, -1.94 - WT), 'lumber');      // lounge floor framing over the mech space

  // ---------------------------------------------------------------- the workshop barn
  M.phase = 'barn';
  const gable = [[0, FL], [30, FL], [30, PLATE], [15, RIDGE], [0, PLATE]];
  // south
  const S = new P.Wall(V(0, 0, 0), V(1, 0, 0), V(0, 0, 1));
  const sB1 = [8.6, 18.6, FL, DOOR_H], sB2 = [21.3, 31.3, FL, DOOR_H], sW1 = WIN(3.3, 5.45), sW2 = WIN(34.5, 36.6);
  P.boardBatten(M, S, [[0, FL], [40, FL], [40, PLATE], [0, PLATE]], [sB1, sB2, sW1, sW2], { inner: 'gyp' });
  M.el = 'bifolds'; P.bifold(M, S, sB1, { transom: 2.1 }); P.bifold(M, S, sB2, { transom: 2.1 }); M.el = null; P.window(M, S, sW1, LITES); P.window(M, S, sW2, LITES);
  M.add(S.box(18.6 + 0.5, 21.3 - 0.5, 9.2, 12.4, 0, 0.12), 'trim');   // pier between the bifolds
  // north
  const N = new P.Wall(V(40, 0, -30), V(-1, 0, 0), V(0, 0, -1));
  const nB = [8.5, 18.6, FL, DOOR_H];
  P.boardBatten(M, N, [[0, FL], [40, FL], [40, PLATE], [0, PLATE]], [nB], { inner: 'gyp' });
  M.el = 'bifolds'; P.bifold(M, N, nB, { transom: 2.1 }); M.el = null;
  // west, with the 12 ft bifold
  const W = new P.Wall(V(0, 0, -30), V(0, 0, 1), V(-1, 0, 0));
  const wB = [9, 21, FL, DOOR_H];
  P.boardBatten(M, W, gable, [wB], { inner: 'gyp' }); M.el = 'bifolds'; P.bifold(M, W, wB, { transom: 2.1 }); M.el = null;
  // east, above and behind the lounge wing, with the door from the mezzanine to the roof deck
  const E = new P.Wall(V(40, 0, 0), V(0, 0, -1), V(1, 0, 0));
  const eD = [10, 13, 11.0, 18.0];
  P.boardBatten(M, E, gable, [eD], { inner: 'gyp' });
  P.casing(M, E, eD, { sill: false });
  P.glazedUnit(M, E, eD, { panes: [[10.25, 12.75, 13.6, 17.75, 2, 4]], rails: [13.4], inset: -0.3 });
  // frieze under the eaves
  M.add(S.box(0, 40, PLATE - 0.7, PLATE, 0, 0.1), 'trim');
  M.add(N.box(0, 40, PLATE - 0.7, PLATE, 0, 0.1), 'trim');

  // roof: standing seam galvalume, 1.25 ft eaves, 1 ft rakes
  const eaveZ = 1.25, rk = 1.0;
  const yE = yTopS(eaveZ), yR = yTopS(-15);
  P.roofPlane(M, V(-rk, yE, eaveZ), V(40 + rk, yE, eaveZ), V(40 + rk, yR, -15), V(-rk, yR, -15));
  P.roofPlane(M, V(40 + rk, yE, -30 - eaveZ), V(-rk, yE, -30 - eaveZ), V(-rk, yR, -15), V(40 + rk, yR, -15));
  M.add(P.obox(V(20, yR + 0.08, -15), V(1, 0, 0), V(0, 1, 0), V(0, 0, 1), 40 + 2 * rk + 0.1, 0.22, 1.1), 'flashing');   // ridge cap
  for (const x of [-rk, 40 + rk]) {
    const out = V(x < 20 ? -1 : 1, 0, 0);
    P.rake(M, V(x, yE, eaveZ), V(x, yR, -15), { out, h: 0.55 });
    P.rake(M, V(x, yE, -30 - eaveZ), V(x, yR, -15), { out, h: 0.55 });
  }
  // gable soffit returns at the corners
  for (const [x0, x1] of [[-rk, 0], [40, 40 + rk]]) {
    M.add(P.abox(x0, PLATE - 0.7, -30 - eaveZ, x1, PLATE, -30), 'trim');
    M.add(P.abox(x0, PLATE - 0.7, 0, x1, PLATE, eaveZ), 'trim');
  }

  // ---------------------------------------------------------------- the lounge wing
  M.phase = 'wing';
  const yW = (x) => 13.4 - 0.131 * (x - 40);   // sloped roof edge along the south face
  const DECK = 11.0, GUARD = 13.75;
  const WS = new P.Wall(V(40, 0, -2), V(1, 0, 0), V(0, 0, 1));
  const wW1 = WIN(1.9, 3.7), wW2 = WIN(12.7, 14.5);
  M.el = 'cutwall';
  P.boardBatten(M, WS, [[0, FL], [16, FL], [16, yW(56) - 0.35], [0, yW(40) - 0.35]], [wW1, wW2], { cornerLeft: false, inner: 'gyp' });
  P.window(M, WS, wW1, LITES); P.window(M, WS, wW2, LITES);
  const WE = new P.Wall(V(56, 0, -2), V(0, 0, -1), V(1, 0, 0));
  const eW1 = WIN(7.25, 9.35), eW2 = WIN(19.85, 21.95);
  P.boardBatten(M, WE, [[0, FL], [26, FL], [26, GUARD], [1.6, GUARD], [1.6, yW(56) - 0.35], [0, yW(56) - 0.35]], [eW1, eW2], { inner: 'gyp' });
  P.window(M, WE, eW1, LITES); P.window(M, WE, eW2, LITES);
  M.el = null;
  const WN = new P.Wall(V(56, 0, -28), V(-1, 0, 0), V(0, 0, -1));
  P.boardBatten(M, WN, [[0, FL], [16, FL], [16, GUARD], [0, GUARD]], [], { cornerRight: false, inner: 'gyp' });
  // the sloped eyebrow roof along the south face, with a galvalume edge, and the guard wall behind it
  M.el = 'wingroof';
  P.roofPlane(M, V(40, yW(40), -1.4), V(57.3, yW(57.3), -1.4), V(57.3, yW(57.3) + 0.25, -3.6), V(40, yW(40) + 0.25, -3.6), { seam: 1.0, fascia: false });
  P.rake(M, V(40, yW(40), -1.4), V(57.3, yW(57.3), -1.4), { out: V(0, 0, 1), h: 0.6, mat: 'flashing', lift: 0.1 });
  P.rake(M, V(57.3, yW(57.3), -1.4), V(57.3, yW(57.3) + 0.25, -3.6), { out: V(1, 0, 0), h: 0.6, mat: 'flashing', lift: 0.1 });
  const GS = new P.Wall(V(40, 0, -3.6), V(1, 0, 0), V(0, 0, 1));
  M.el = 'cutwall';
  P.boardBatten(M, GS, [[0, yW(40) + 0.1], [16, yW(56) + 0.1], [16, GUARD], [0, GUARD]], [], { cornerLeft: false, cornerRight: false, wallDepth: 0.5 });
  M.el = 'deck';
  // copings on the guard walls
  M.add(P.abox(40, GUARD, -4.15, 56.1, GUARD + 0.14, -3.5), 'flashing');
  M.add(P.abox(55.4, GUARD, -28.1, 56.1, GUARD + 0.14, -3.5), 'flashing');
  M.add(P.abox(40, GUARD, -28.1, 56.1, GUARD + 0.14, -27.4), 'flashing');
  // Cumaru roof deck, boards running north south over the pitched membrane
  M.add(P.abox(40, DECK - 0.6, -27.4, 55.4, DECK - 0.35, -4.1), 'membrane');
  for (let x = 40.1; x < 55.35; x += 0.47) M.add(P.abox(x, DECK - 0.1, -27.4, Math.min(x + 0.44, 55.4), DECK, -4.1), 'deck');
  M.el = 'stove';
  // Class A flue from the Hearthstone stove, outside the east wall as drawn on SK-5, with a plain cap
  const FX = 56.75;
  M.add(P.cyl(FX, 7.6, -15, 0.45, 18.3, 20), 'stainless');
  M.add(P.abox(56.05, 7.3, -15.35, FX, 7.9, -14.65), 'stainless');   // wall thimble
  for (const y of [10.5, 13.5]) M.add(P.abox(56.05, y - 0.06, -15.08, FX - 0.4, y + 0.06, -14.92), 'steel');   // wall bands
  M.add(P.cyl(FX, 18.3, -15, 0.62, 18.42, 20), 'steel');
  M.add(new THREE.ConeGeometry(0.66, 0.42, 20).translate(FX, 18.85, -15), 'steel');
  M.add(P.cyl(FX, 18.42, -15, 0.1, 18.64, 8), 'steel');
  M.el = null;

  // ---------------------------------------------------------------- interior, seen through the glass
  // Fit-out as SK-5 lays it out: double height workshop under a painted cathedral ceiling with the
  // exposed beams carried in the estimate, the mezzanine at the east end at roof deck level, and the
  // whiskey bar and lounge in the wing. Owner equipment is shown as plain blocks.
  M.phase = 'interior';
  const yc = (z) => 14.14 + K * Math.min(-z, 30 + z);         // cathedral ceiling under the rafters
  const slope = (x0, x1, za, zb, mat, t = 0.05) => {          // a sloped plane between two z lines
    const a = V((x0 + x1) / 2, yc(za), za), b = V((x0 + x1) / 2, yc(zb), zb), d = b.clone().sub(a);
    const ay = d.clone().normalize(), az = new THREE.Vector3().crossVectors(V(1, 0, 0), ay).normalize();
    M.add(P.obox(a.clone().addScaledVector(d, 0.5), V(1, 0, 0), ay, az, x1 - x0, d.length(), t), mat);
  };
  slope(0.6, 39.4, -0.6, -15, 'gyp'); slope(0.6, 39.4, -15, -29.4, 'gyp');
  // beams: the 40 ft ridge beam and two 30 ft ties
  M.add(P.abox(0.6, yc(-15) - 1.25, -15.38, 39.4, yc(-15), -14.62), 'timber');
  for (const x of [13.3, 26.7]) M.add(P.abox(x - 0.3, 13.4, -29.4, x + 0.3, 14.4, -0.6), 'timber');
  // purlins between the beams, so the ceiling reads as framed
  for (const z of [-5.2, -9.8, -20.2, -24.8]) {
    const y = yc(z) - 0.55;
    M.add(P.abox(0.6, y, z - 0.25, 39.4, y + 0.55, z + 0.25), 'timber');
  }
  // workshop floor: sealed concrete (the slab is already in the foundation phase)
  // mezzanine at the east end, floor at the roof deck door sill
  const MZ = DECK, mx0 = 32.8, mz0 = -9.6, mz1 = -29.4;
  M.add(P.abox(mx0, MZ - 0.25, mz1, 39.4, MZ, mz0), 'plank');
  for (let x = mx0 + 0.6; x < 39.3; x += 1.33) M.add(P.abox(x - 0.12, MZ - 1.05, mz1, x + 0.12, MZ - 0.25, mz0), 'timber');
  M.add(P.abox(mx0 - 0.1, MZ - 1.45, mz1, mx0 + 0.45, MZ - 0.25, mz0), 'timber');               // carrying beam
  M.add(P.abox(mx0, MZ - 1.45, mz0 - 0.45, 39.4, MZ - 0.25, mz0 + 0.1), 'timber');               // rim at the south edge
  for (const z of [-10.0, -19.5, -29.0]) M.add(P.abox(mx0, FL, z - 0.25, mx0 + 0.5, MZ - 1.45, z + 0.25), 'timber');
  const guard = (a, b) => {                                   // timber posts and cap, steel pickets
    const d = b.clone().sub(a), L = d.length(), u = d.clone().normalize();
    for (let s = 0; s <= L + 0.01; s += L / Math.max(1, Math.round(L / 4.5))) { const p = a.clone().addScaledVector(u, s); M.add(P.abox(p.x - 0.18, MZ, p.z - 0.18, p.x + 0.18, MZ + 3.5, p.z + 0.18), 'timber'); }
    const c = a.clone().addScaledVector(d, 0.5);
    M.add(P.obox(V(c.x, MZ + 3.55, c.z), u, V(0, 1, 0), V(-u.z, 0, u.x), L + 0.3, 0.2, 0.42), 'timber');
    M.add(P.obox(V(c.x, MZ + 0.35, c.z), u, V(0, 1, 0), V(-u.z, 0, u.x), L, 0.12, 0.12), 'steel');
    for (let s = 0.35; s < L - 0.1; s += 0.36) { const p = a.clone().addScaledVector(u, s); M.add(P.abox(p.x - 0.03, MZ + 0.35, p.z - 0.03, p.x + 0.03, MZ + 3.45, p.z + 0.03), 'steel'); }
  };
  // stair up the west side of the mezzanine, rising north to a landing
  const sx0 = 29.8, sx1 = 32.8, sz = -13.0, n = 16, rise = (MZ - FL) / n, run = 0.83;
  for (let i = 1; i < n; i++) M.add(P.abox(sx0, FL + i * rise - 0.15, sz - i * run, sx1, FL + i * rise, sz - (i - 1) * run - 0.08), 'timber');
  M.add(P.abox(sx0, MZ - 0.25, mz1, mx0, MZ, sz - (n - 1) * run), 'plank');                      // landing
  for (const x of [sx0 - 0.05, sx1 + 0.05]) {
    const a = V(x, FL, sz + 0.4), b = V(x, MZ - 0.2, sz - (n - 1) * run), d = b.clone().sub(a);
    M.add(P.obox(a.clone().addScaledVector(d, 0.5), d.clone().normalize(), new THREE.Vector3().crossVectors(V(1, 0, 0), d).normalize(), V(1, 0, 0), d.length(), 0.9, 0.12), 'steel');
  }
  { const a = V(sx0 - 0.1, FL + 3.0, sz), b = V(sx0 - 0.1, MZ + 3.0, sz - (n - 1) * run), d = b.clone().sub(a);
    M.add(P.obox(a.clone().addScaledVector(d, 0.5), d.clone().normalize(), new THREE.Vector3().crossVectors(V(1, 0, 0), d).normalize(), V(1, 0, 0), d.length(), 0.14, 0.14), 'timber'); }
  guard(V(mx0, 0, sz - (n - 1) * run), V(mx0, 0, mz0)); guard(V(mx0, 0, mz0), V(39.4, 0, mz0));
  guard(V(sx0, 0, mz1 + 0.2), V(sx0, 0, sz - (n - 1) * run));
  // 3D printer workspace on the mezzanine: a long table and printer cabinets
  M.add(P.abox(37.2, MZ + 2.4, -27.5, 39.3, MZ + 2.55, -14), 'timber');
  for (const z of [-26.5, -24.2, -21.9, -19.6, -17.3]) M.add(P.abox(37.6, MZ + 2.55, z - 0.9, 39.1, MZ + 4.3, z + 0.9), 'machine');
  // benches along the north wall and the west ends, butcher block tops on steel bases, shelf above
  const bench = (x0, z0, x1, z1) => {
    M.add(P.abox(x0, FL + 2.75, z0, x1, FL + 2.95, z1), 'timber');
    M.add(P.abox(x0 + 0.1, FL, z0 + 0.15, x1 - 0.1, FL + 2.75, z1 - 0.15), 'machine');
    M.add(P.abox(x0 + 0.1, FL + 0.35, z0 + 0.1, x1 - 0.1, FL + 0.45, z1 - 0.1), 'steel');
  };
  bench(0.7, -29.35, 20.6, -26.9); bench(32.9, -29.35, 37.0, -26.9);
  M.add(P.abox(0.7, FL + 6.0, -29.35, 20.6, FL + 6.12, -28.2), 'timber');
  M.add(P.abox(0.7, FL + 7.6, -29.35, 20.6, FL + 7.72, -28.2), 'timber');
  bench(0.65, -29.3, 3.1, -22.6); bench(0.65, -7.9, 3.1, -0.7);
  // assembly table at the center of the floor
  M.add(P.abox(11.5, FL + 3.0, -17.2, 21.5, FL + 3.25, -12.8), 'timber');
  for (const [x, z] of [[12, -16.8], [21, -16.8], [12, -13.2], [21, -13.2]]) M.add(P.abox(x - 0.2, FL, z - 0.2, x + 0.2, FL + 3.0, z + 0.2), 'steel');
  M.add(P.abox(12, FL + 0.6, -16.9, 21, FL + 0.75, -13.1), 'timber');
  // owner equipment as plain blocks: table saw with outfeed, bandsaw, drill press, a rolling cart
  M.add(P.abox(5.0, FL, -12.5, 6.8, FL + 2.8, -10.7), 'machine'); M.add(P.abox(3.8, FL + 2.8, -13.6, 8.0, FL + 2.95, -9.6), 'steel');
  M.add(P.abox(1.4, FL, -21.5, 3.0, FL + 6.2, -19.9), 'machine');
  M.add(P.abox(34.0, FL, -15.0, 35.4, FL + 5.4, -13.6), 'machine');
  M.add(P.abox(26.0, FL + 0.4, -24.5, 28.6, FL + 3.0, -22.9), 'machine');
  // pendants over the floor: a cord, a dark shade and a warm lamp face
  const pend = (x, z, y, r = 0.75, top = null) => {
    M.add(P.cyl(x, y + 0.5, z, 0.025, top ?? yc(z), 6), 'steel');
    M.add(new THREE.ConeGeometry(r, 0.7, 24, 1, true).translate(x, y + 0.35, z), 'steel');
    M.add(new THREE.CircleGeometry(r * 0.92, 24).rotateX(Math.PI / 2).translate(x, y + 0.05, z), 'lamp');
  };
  for (const x of [7, 16, 25]) for (const z of [-9, -21]) pend(x, z, 11.6);
  // the lounge wing: plank floor, painted ceiling under the roof deck, whiskey bar, sofa, stove
  M.add(P.abox(40.2, FL, -27.4, 55.4, FL + 0.04, -2.6), 'plank');
  M.el = 'wingroof'; M.add(P.abox(40.2, 9.7, -27.4, 55.4, 9.75, -2.6), 'gyp'); M.el = null;
  // back bar against the north wall, open shelves, and the bar with its copper top
  M.el = 'bar';
  M.add(P.abox(42.6, FL, -27.4, 52.6, FL + 3.0, -25.9), 'walnut');
  M.add(P.abox(42.6, FL + 3.0, -27.4, 52.6, FL + 3.12, -25.8), 'copper');
  for (const y of [5.2, 6.4, 7.6]) M.add(P.abox(42.6, y, -27.4, 52.6, y + 0.12, -26.5), 'walnut');
  for (let x = 43.0; x < 52.3; x += 0.42) for (const y of [5.32, 6.52, 7.72]) if ((Math.round(x * 7) + y * 3) % 5 > 1) M.add(P.cyl(x, y, -26.95, 0.13, y + 0.85, 8), 'glass');
  M.add(P.abox(43.0, FL, -23.4, 52.2, FL + 3.35, -21.9), 'walnut');
  M.add(P.abox(42.8, FL + 3.35, -23.6, 52.4, FL + 3.5, -21.4), 'copper');
  M.el = null;
  for (const x of [44.2, 46.4, 48.6, 50.8]) { M.add(P.cyl(x, FL, -20.6, 0.08, FL + 2.4, 8), 'steel'); M.add(P.cyl(x, FL + 2.4, -20.6, 0.6, FL + 2.6, 16), 'fabric'); }
  for (const x of [44.6, 47.6, 50.6]) pend(x, -22.6, 6.9, 0.55, 9.7);
  // sofa and low table by the south windows, the Hearthstone stove on the east wall
  M.add(P.abox(43.4, FL, -7.4, 51.4, FL + 1.45, -4.2), 'fabric');
  M.add(P.abox(43.4, FL + 1.45, -4.9, 51.4, FL + 2.8, -4.2), 'fabric');
  for (const x of [43.4, 50.7]) M.add(P.abox(x, FL + 1.45, -7.4, x + 0.7, FL + 2.2, -4.2), 'fabric');
  M.add(P.abox(44.8, FL, -10.6, 50.0, FL + 1.35, -8.6), 'walnut');
  M.el = 'stove';
  M.add(P.abox(53.6, FL, -16.3, 55.2, FL + 0.25, -13.7), 'concrete');
  M.add(P.abox(53.9, FL + 0.25, -15.7, 55.0, FL + 2.75, -14.3), 'steel');
  M.add(P.cyl(54.45, FL + 2.75, -15, 0.3, 7.6, 16), 'steel');
  M.add(P.abox(54.15, 7.3, -15.3, 55.45, 7.9, -14.7), 'steel');
  M.el = null;

  // ---------------------------------------------------------------- canopies, cupola, gutters
  M.phase = 'details';
  M.el = 'canopy';
  // south canopy over the two bifolds, carried on paired timber brackets
  P.roofPlane(M, V(6.1, 13.1, 3.0), V(33.8, 13.1, 3.0), V(33.8, 14.1, 0), V(6.1, 14.1, 0), { seam: 1.0, fasciaH: 0.4 });
  M.add(P.abox(6.1, 12.3, 2.35, 33.8, 12.95, 2.85), 'trim');
  const bracket = (x, z0, dir) => {   // dir: +1 projects south, -1 north
    const zz = (d) => z0 + dir * d;
    M.add(P.abox(x - 0.22, 9.6, Math.min(zz(0), zz(0.55)), x + 0.22, 12.95, Math.max(zz(0), zz(0.55))), 'trim');
    M.add(P.abox(x - 0.22, 12.3, Math.min(zz(0), zz(2.8)), x + 0.22, 12.95, Math.max(zz(0), zz(2.8))), 'trim');
    const a = V(x, 10.2, zz(0.4)), b = V(x, 12.35, zz(2.3)), d = b.clone().sub(a);
    M.add(P.obox(a.clone().addScaledVector(d, 0.5), V(1, 0, 0), d.clone().normalize(), V(0, -d.z, d.y).normalize(), 0.4, d.length(), 0.35), 'trim');
  };
  for (const x of [6.75, 7.4, 19.65, 20.3, 32.55, 33.2]) bracket(x, 0, 1);
  // north canopy
  P.roofPlane(M, V(34, 13.1, -33), V(19, 13.1, -33), V(19, 14.1, -30), V(34, 14.1, -30), { seam: 1.0, fasciaH: 0.4 });
  M.add(P.abox(19, 12.3, -32.85, 34, 12.95, -32.35), 'trim');
  for (const x of [19.6, 26.5, 33.4]) bracket(x, -30, -1);
  // west canopy over the 12 ft bifold, on knee braces
  P.roofPlane(M, V(-4, 13.1, -8), V(-4, 13.1, -22), V(0, 14.1, -22), V(0, 14.1, -8), { seam: 1.0, fasciaH: 0.4 });
  M.add(P.abox(-3.85, 12.3, -22, -3.35, 12.95, -8), 'trim');
  for (const z of [-21.4, -15, -8.6]) {
    M.add(P.abox(-0.55, 9.6, z - 0.22, 0, 12.95, z + 0.22), 'trim');
    M.add(P.abox(-3.8, 12.3, z - 0.22, 0, 12.95, z + 0.22), 'trim');
    const a = V(-0.4, 10.2, z), b = V(-3.1, 12.35, z), d = b.clone().sub(a);
    M.add(P.obox(a.clone().addScaledVector(d, 0.5), d.clone().normalize(), V(0, 0, 1), new THREE.Vector3().crossVectors(d.clone().normalize(), V(0, 0, 1)), d.length(), 0.4, 0.35), 'trim');
  }

  M.el = 'cupola';
  // cupola: lap-sided base, glazed lantern on every face, cornice, standing seam hip roof, horse vane
  const cx = 20, cz = -15;
  M.add(P.abox(cx - 2.33, 22.0, cz - 2.33, cx + 2.33, 26.6, cz + 2.33), 'siding');
  for (let y = 22.2; y < 26.5; y += 0.42) {   // lap board shadow lines
    M.add(P.abox(cx - 2.38, y, cz - 2.38, cx + 2.38, y + 0.06, cz + 2.38), 'trim');
  }
  for (const [sx, sz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) M.add(P.abox(cx + sx * 2.33 - 0.25, 22, cz + sz * 2.33 - 0.25, cx + sx * 2.33 + 0.25, 26.6, cz + sz * 2.33 + 0.25), 'trim');
  M.add(P.abox(cx - 2.5, 26.6, cz - 2.5, cx + 2.5, 27.0, cz + 2.5), 'trim');
  M.add(P.abox(cx - 1.75, 27.0, cz - 1.75, cx + 1.75, 29.85, cz + 1.75), 'frame');   // dark lantern interior seen through the glass
  const faces = [[V(cx - 2.1, 0, cz + 2.1), V(1, 0, 0), V(0, 0, 1)], [V(cx + 2.1, 0, cz - 2.1), V(-1, 0, 0), V(0, 0, -1)],
                 [V(cx + 2.1, 0, cz + 2.1), V(0, 0, -1), V(1, 0, 0)], [V(cx - 2.1, 0, cz - 2.1), V(0, 0, 1), V(-1, 0, 0)]];
  for (const [o, U, Nn] of faces) {
    const F = new P.Wall(o, U, Nn), r = [1.05, 3.15, 27.45, 29.6];
    M.add(F.slab([[0, 27.0], [4.2, 27.0], [4.2, 29.85], [0, 29.85]], [r], -0.3, 0), 'siding');
    P.casing(M, F, r, { width: 0.22 });
    P.glazedUnit(M, F, r, { cols: 2, rows: 2, inset: -0.18, frame: 0.16 });
    for (const u of [0.2, 4.0]) M.add(F.box(u - 0.2, u + 0.2, 27.0, 29.85, 0, 0.08), 'trim');
  }
  M.add(P.abox(cx - 2.45, 29.85, cz - 2.45, cx + 2.45, 30.25, cz + 2.45), 'trim');
  M.add(P.abox(cx - 2.62, 30.25, cz - 2.62, cx + 2.62, 30.9, cz + 2.62), 'trim');
  const hip = new THREE.ConeGeometry(2.72 * Math.SQRT2, 1.75, 4, 1).rotateY(Math.PI / 4).translate(cx, 30.9 + 0.875, cz);
  M.add(hip, 'roof');
  for (const [dx, dz] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) {   // hip ridge rolls
    const a = V(cx + dx * 2.72, 30.95, cz + dz * 2.72), b = V(cx, 32.65, cz), d = b.clone().sub(a);
    M.add(P.obox(a.clone().addScaledVector(d, 0.5), new THREE.Vector3().crossVectors(d, V(0, 1, 0)).normalize(), d.clone().normalize(), new THREE.Vector3().crossVectors(new THREE.Vector3().crossVectors(d, V(0, 1, 0)).normalize(), d.clone().normalize()), 0.14, d.length(), 0.14), 'flashing');
  }
  P.weathervane(M, cx, 32.6, cz, 1.0);
  M.el = null;
  // gutters on both barn eaves and downspouts at the north corners
  P.gutter(M, V(-rk, yE - 0.35, eaveZ + 0.05), V(40 + rk, yE - 0.35, eaveZ + 0.05), V(0, 0, 1));
  P.gutter(M, V(-rk, yE - 0.35, -30 - eaveZ - 0.05), V(40 + rk, yE - 0.35, -30 - eaveZ - 0.05), V(0, 0, -1));
  for (let x = -rk + 1.2; x < 40 + rk - 0.5; x += 2.5) for (const [z0, z1] of [[eaveZ - 0.1, eaveZ + 0.62], [-30 - eaveZ - 0.62, -30 - eaveZ + 0.1]]) M.add(P.abox(x - 0.06, yE - 0.12, z0, x + 0.06, yE - 0.08, z1), 'flashing');
  for (const x of [0.8, 39.2]) {
    P.downspout(M, x, -30.35, yE - 0.9);
    M.add(P.abox(x - 0.15, yE - 1.05, -31.75, x + 0.15, yE - 0.75, -30.35), 'flashing');
  }
  return M.group();
}
