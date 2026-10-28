// The Cooper Barn, Crisp Architects SK-5 (22 September 2026), modeled for the presentation.
// Plan dimensions from SK-5. Heights from the SK-5 front elevation and the Crisp rendering on the
// same sheet, with the 15 ft plate and 9:12 roof carried in the Montana estimate.
// x east, y up, z south. Barn x 0..40, z 0 (south face) .. -30. Wing x 40..56, z -2..-28.
import * as THREE from 'three';
import * as P from '../../kit/tools/glb/parts.js';   // path from <project>/model/build.js

export default function build() {
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const M = new P.Model(P.materials());
  const FL = 0.67;                     // top of exposed foundation, bottom of siding
  const PLATE = 15, K = 0.75, RIDGE = 26.25, RT = 0.44;   // roof underside at the wall, 9:12, ridge underside, top offset
  const yTopS = (z) => PLATE + RT + K * (-z);              // barn roof top surface, south slope (z from +1.25 to -15)
  const WIN = (a, b) => [a, b, 3.05, 8.4];
  const DOOR_H = 12.2;

  // ---------------------------------------------------------------- foundation
  M.phase = 'foundation';
  M.add(P.abox(-0.06, 0, -30.06, 40.06, FL, 0.06), 'concrete');
  M.add(P.abox(40, 0, -28.06, 56.06, FL, -1.94), 'concrete');

  // ---------------------------------------------------------------- the workshop barn
  M.phase = 'barn';
  const gable = [[0, FL], [30, FL], [30, PLATE], [15, RIDGE], [0, PLATE]];
  // south
  const S = new P.Wall(V(0, 0, 0), V(1, 0, 0), V(0, 0, 1));
  const sB1 = [8.6, 18.6, FL, DOOR_H], sB2 = [21.3, 31.3, FL, DOOR_H], sW1 = WIN(3.3, 5.45), sW2 = WIN(34.5, 36.6);
  P.boardBatten(M, S, [[0, FL], [40, FL], [40, PLATE], [0, PLATE]], [sB1, sB2, sW1, sW2]);
  P.bifold(M, S, sB1); P.bifold(M, S, sB2); P.window(M, S, sW1); P.window(M, S, sW2);
  M.add(S.box(18.6 + 0.5, 21.3 - 0.5, 9.2, 12.4, 0, 0.12), 'trim');   // pier between the bifolds
  // north
  const N = new P.Wall(V(40, 0, -30), V(-1, 0, 0), V(0, 0, -1));
  const nB = [8.5, 18.6, FL, DOOR_H];
  P.boardBatten(M, N, [[0, FL], [40, FL], [40, PLATE], [0, PLATE]], [nB]);
  P.bifold(M, N, nB);
  // west, with the 12 ft bifold
  const W = new P.Wall(V(0, 0, -30), V(0, 0, 1), V(-1, 0, 0));
  const wB = [9, 21, FL, DOOR_H];
  P.boardBatten(M, W, gable, [wB]); P.bifold(M, W, wB);
  // east, above and behind the lounge wing, with the door from the mezzanine to the roof deck
  const E = new P.Wall(V(40, 0, 0), V(0, 0, -1), V(1, 0, 0));
  const eD = [10, 13, 11.0, 18.0];
  P.boardBatten(M, E, gable, [eD]);
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
  const DECK = 11.0, GUARD = 14.15;
  const WS = new P.Wall(V(40, 0, -2), V(1, 0, 0), V(0, 0, 1));
  const wW1 = WIN(1.9, 3.7), wW2 = WIN(12.7, 14.5);
  P.boardBatten(M, WS, [[0, FL], [16, FL], [16, yW(56) - 0.35], [0, yW(40) - 0.35]], [wW1, wW2], { cornerLeft: false });
  P.window(M, WS, wW1); P.window(M, WS, wW2);
  const WE = new P.Wall(V(56, 0, -2), V(0, 0, -1), V(1, 0, 0));
  const eW1 = WIN(7.25, 9.35), eW2 = WIN(19.85, 21.95);
  P.boardBatten(M, WE, [[0, FL], [26, FL], [26, GUARD], [1.6, GUARD], [1.6, yW(56) - 0.35], [0, yW(56) - 0.35]], [eW1, eW2]);
  P.window(M, WE, eW1); P.window(M, WE, eW2);
  const WN = new P.Wall(V(56, 0, -28), V(-1, 0, 0), V(0, 0, -1));
  P.boardBatten(M, WN, [[0, FL], [16, FL], [16, GUARD], [0, GUARD]], [], { cornerRight: false });
  // the sloped eyebrow roof along the south face, with a galvalume edge, and the guard wall behind it
  P.roofPlane(M, V(40, yW(40), -1.4), V(57.3, yW(57.3), -1.4), V(57.3, yW(57.3) + 0.25, -3.6), V(40, yW(40) + 0.25, -3.6), { seam: 1.0, fascia: false });
  P.rake(M, V(40, yW(40), -1.4), V(57.3, yW(57.3), -1.4), { out: V(0, 0, 1), h: 0.6, mat: 'flashing', lift: 0.1 });
  P.rake(M, V(57.3, yW(57.3), -1.4), V(57.3, yW(57.3) + 0.25, -3.6), { out: V(1, 0, 0), h: 0.6, mat: 'flashing', lift: 0.1 });
  const GS = new P.Wall(V(40, 0, -3.6), V(1, 0, 0), V(0, 0, 1));
  P.boardBatten(M, GS, [[0, yW(40) + 0.1], [16, yW(56) + 0.1], [16, GUARD], [0, GUARD]], [], { cornerLeft: false, cornerRight: false, wallDepth: 0.5 });
  // copings on the guard walls
  M.add(P.abox(40, GUARD, -4.15, 56.1, GUARD + 0.14, -3.5), 'flashing');
  M.add(P.abox(55.4, GUARD, -28.1, 56.1, GUARD + 0.14, -3.5), 'flashing');
  M.add(P.abox(40, GUARD, -28.1, 56.1, GUARD + 0.14, -27.4), 'flashing');
  // Cumaru roof deck, boards running north south over the pitched membrane
  M.add(P.abox(40, DECK - 0.6, -27.4, 55.4, DECK - 0.35, -4.1), 'membrane');
  for (let x = 40.1; x < 55.35; x += 0.47) M.add(P.abox(x, DECK - 0.1, -27.4, Math.min(x + 0.44, 55.4), DECK, -4.1), 'deck');
  // stainless flue from the Hearthstone stove
  M.add(P.cyl(54.4, DECK - 0.2, -15, 0.45, 19.0, 20), 'stainless');
  M.add(P.cyl(54.4, DECK, -15, 0.62, DECK + 0.35, 20), 'stainless');
  M.add(P.cyl(54.4, 19.0, -15, 0.7, 19.15, 20), 'stainless');
  M.add(new THREE.ConeGeometry(0.75, 0.5, 20).translate(54.4, 19.55, -15), 'stainless');
  M.add(P.cyl(54.4, 19.15, -15, 0.12, 19.35, 8), 'stainless');

  // ---------------------------------------------------------------- canopies, cupola, gutters
  M.phase = 'details';
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
  // gutters on both barn eaves and downspouts at the north corners
  P.gutter(M, V(-rk, yE - 0.35, eaveZ + 0.05), V(40 + rk, yE - 0.35, eaveZ + 0.05), V(0, 0, 1));
  P.gutter(M, V(-rk, yE - 0.35, -30 - eaveZ - 0.05), V(40 + rk, yE - 0.35, -30 - eaveZ - 0.05), V(0, 0, -1));
  for (const x of [0.8, 39.2]) {
    P.downspout(M, x, -30.35, yE - 0.9);
    M.add(P.abox(x - 0.15, yE - 1.05, -31.75, x + 0.15, yE - 0.75, -30.35), 'flashing');
  }
  return M.group();
}
