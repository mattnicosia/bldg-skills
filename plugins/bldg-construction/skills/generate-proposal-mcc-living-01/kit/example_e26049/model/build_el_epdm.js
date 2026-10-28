// 1004 Old Albany Post Rd, Garrison NY. Blejer Architecture + Design, SD Presentation 02 (09.04.2026), Scheme 2.
// Plan dimensions from the SD-04 / SD-05 wall geometry as measured for the Montana estimate (E26049):
//   first floor 54.0' x 32.17' plus a 21.26' x 4.58' stair bay on the south, screened deck 17.04' x 21.17' to the west,
//   first-level roof 71' over the house and deck, second floor box 21.99' x 44.59' running north-south and
//   cantilevering 6.66' north of the glass wall. Heights from SD-06 / SD-07: 9'-6" floor to ceiling, 1.5' roof,
//   box walls 10.8' above the green roof. Materials and openings from the Blejer renderings (SD-08 to SD-14).
// Plan coordinates: X east, N north, y up. three.js world: x = X, y = y, z = -N.
// Element tags (M.el): windows, cantilever, greenroof, siding + boxsiding, stair, porch. Cutaway tags: roof1 (first floor roof over the house),
//   roof1u (the first roof under the box), boxshell (box floor, ceiling, roof, stair guard), lamps, partitions.
// Phases: foundation, floor1, porch, upper, upperwalls, roof, interior, stair, site.
import * as THREE from 'three';
import * as P from '../../kit/tools/glb/parts.js';

export default function build() {
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const M = new P.Model(P.materials({
    siding: { color: '#d8bd96', roughness: 0.8 }, trim: { color: '#d8bd96', roughness: 0.8 }, soffit: { color: '#b8986c', roughness: 0.8 },
    frame: { color: '#2e3138', roughness: 0.45 }, flashing: { color: '#3b3d42', roughness: 0.4, metalness: 0.6 },
    sedum: { color: '#6f7f43', roughness: 1.0 }, subfloor: { color: '#c9b593', roughness: 0.9 }, stone: { color: '#9b968c', roughness: 0.9 }, gyp: { color: '#ece9e2', roughness: 0.92 },
  }));
  const B = (X0, N0, y0, X1, N1, y1) => P.abox(X0, y0, -N1, X1, y1, -N0);   // a box from plan corners
  const FT = 1.0, FL = 2.07, CEIL = 11.6, RT = 13.2, RW = RT - 0.12;   // RW: wall tops, under the membrane                     // top of foundation, first floor, ceiling, top of first roof
  const HN = 32.17, HW = 54.0;                                            // house depth (N) and length (X)
  const BAY = [13.4, 34.66, 4.58];                                        // stair bay X0, X1, depth south of the house
  const BX0 = 13.34, BX1 = 35.33, BN0 = -5.58, BN1 = 39.0, BB = 12.4, BT = 24.0;   // the box
  const DX0 = -17.04, DN0 = 11.0;                                         // screened deck west edge, south edge

  // ---------------------------------------------------------------- foundation
  // 10" crawl space walls on 24" x 12" footings at frost depth, 2" rat slab, piers under the screened deck.
  M.phase = 'foundation';
  const WT = 0.83, FB = -4.5;
  const wall = (x0, n0, x1, n1) => {   // a run of foundation wall along x or n, with its footing
    M.add(B(Math.min(x0, x1), Math.min(n0, n1), FB, Math.max(x0, x1), Math.max(n0, n1), FT), 'concrete');
    const along = Math.abs(x1 - x0) > Math.abs(n1 - n0);
    const cx = (x0 + x1) / 2, cn = (n0 + n1) / 2;
    M.add(along ? B(Math.min(x0, x1) - 0.6, cn - 1, FB - 1, Math.max(x0, x1) + 0.6, cn + 1, FB) : B(cx - 1, Math.min(n0, n1) - 0.6, FB - 1.02, cx + 1, Math.max(n0, n1) + 0.6, FB - 0.02), 'footing');
  };
  wall(0, HN - WT, HW, HN);                     // north
  wall(0, 0, BAY[0], WT); wall(BAY[1], 0, HW, WT);   // south, either side of the bay
  wall(0, WT, WT, HN - WT); wall(HW - WT, WT, HW, HN - WT);   // west, east
  wall(BAY[0], -BAY[2], BAY[1], -BAY[2] + WT);  // bay south
  wall(BAY[0], -BAY[2] + WT, BAY[0] + WT, WT); wall(BAY[1] - WT, -BAY[2] + WT, BAY[1], WT);
  M.add(B(WT, WT, -3.17, HW - WT, HN - WT, -3.0), 'slab');      // rat slab
  M.add(B(WT, WT, -3.5, HW - WT, HN - WT, -3.17), 'gravel');
  for (const X of [DX0 + 1, -8.5, -2.4]) for (const N of [DN0 + 1, 21.5, HN - 1]) {   // porch piers
    M.add(P.cyl(X, FB, -N, 0.6, FT - 0.4, 16), 'concrete');
    M.add(B(X - 1.2, N - 1.2, FB - 1, X + 1.2, N + 1.2, FB), 'footing');
  }
  M.add(B(0.4, 0.4, FT, HW - 0.4, HN - 0.4, FL - 0.05), 'subfloor');   // floor framing and subfloor over the crawl space
  M.add(B(BAY[0] + 0.4, -BAY[2] + 0.4, FT, BAY[1] - 0.4, 0.4, FL - 0.05), 'subfloor');

  // ---------------------------------------------------------------- first floor shell
  M.phase = 'floor1';
  const S = new P.Wall(V(0, 0, 0), V(1, 0, 0), V(0, 0, 1));
  const N = new P.Wall(V(HW, 0, -HN), V(-1, 0, 0), V(0, 0, -1));
  const W = new P.Wall(V(0, 0, -HN), V(0, 0, 1), V(-1, 0, 0));
  const E = new P.Wall(V(HW, 0, 0), V(0, 0, -1), V(1, 0, 0));
  const VB = { batten: 0.1, battenDepth: 0.035, spacing: 0.42, corners: true, cornerWidth: 0.7, inner: 'gyp', casing: 0.0 };   // vertical wood boards
  const panes = (u0, u1, v0, v1, n) => {   // a glazed wall of n equal panels, thin dark frames
    const st = []; for (let i = 1; i < n; i++) st.push(u0 + (u1 - u0) * i / n);
    const ps = []; for (let i = 0; i < n; i++) ps.push([u0 + (u1 - u0) * i / n + 0.12, u0 + (u1 - u0) * (i + 1) / n - 0.12, v0 + 0.2, v1 - 0.15, 1, 1]);
    return { panes: ps, stiles: st, stileW: 0.16, frame: 0.18, inset: -0.35 };
  };
  const glaze = (w, r, n) => { M.el = 'windows'; P.glazedUnit(M, w, r, panes(r[0], r[1], r[2], r[3], n)); M.el = null; };
  const band = (w, u0, u1, v0, v1, d = 0.07, mat = 'flashing') => M.add(w.box(u0, u1, v0, v1, -0.02, d), mat);   // base flashing and caps that close the board ends

  // north: the glass wall, 51.9' of Unilux units floor to ceiling (8 panels, the lift-slide among them)
  const nG = [1.0, 52.9, FL, CEIL];
  M.el = 'siding'; P.boardBatten(M, N, [[0, FT], [HW, FT], [HW, RW], [0, RW]], [nG], VB); M.el = null;
  glaze(N, nG, 8);
  band(N, 0, HW, FT, FL - 0.12, 0.07, 'concrete'); band(N, 0, HW, FL - 0.12, FL + 0.02, 0.09);   // exposed concrete, thin dark sill
  // south: entry door and bedroom and bath windows either side of the stair bay
  const sE = [3.0, 6.2, FL, 9.6], sW1 = [8.0, 11.5, 5.0, 9.6], sW2 = [38.5, 44.5, 5.0, 9.6], sW3 = [48.0, 50.5, 7.0, 9.6];
  M.el = 'siding';
  P.boardBatten(M, S, [[0, FT], [BAY[0], FT], [BAY[0], RW], [0, RW]], [sE, sW1], VB);
  P.boardBatten(M, S, [[BAY[1], FT], [HW, FT], [HW, RW], [BAY[1], RW]], [sW2, sW3], VB);
  M.el = null;
  band(S, 0, BAY[0], FT, FT + 0.35); band(S, BAY[1], HW, FT, FT + 0.35);
  M.add(S.box(sE[0], sE[1], sE[2], sE[3], -0.4, -0.3), 'timber');   // wood entry door
  M.el = 'windows'; P.glazedUnit(M, S, [6.3, 7.6, FL, 9.6], panes(6.3, 7.6, FL, 9.6, 1)); M.el = null;   // side lite
  glaze(S, sW1, 1); glaze(S, sW2, 2); glaze(S, sW3, 1);
  // west, inside the screened deck: the 10' lift-slide from the kitchen
  const wD = [3.0, 13.0, FL - 0.45, 10.0];
  M.el = 'siding'; P.boardBatten(M, W, [[0, FT], [HN, FT], [HN, RW - 0.01], [0, RW - 0.01]], [wD], VB); M.el = null;
  band(W, 0, HN, FT, FT + 0.35);
  glaze(W, wD, 2);
  // east: bedroom and bath
  const eW1 = [20.0, 27.0, 4.5, CEIL - 0.6], eW2 = [9.0, 11.5, 7.0, 10.0];
  M.el = 'siding'; P.boardBatten(M, E, [[0, FT], [HN, FT], [HN, RW - 0.01], [0, RW - 0.01]], [eW1, eW2], VB); M.el = null;
  glaze(E, eW1, 2); glaze(E, eW2, 1);
  band(E, 0, HN, FT, FT + 0.35);
  // stair bay, glazed on three sides under the box
  const BS = new P.Wall(V(BAY[0], 0, BAY[2]), V(1, 0, 0), V(0, 0, 1));
  const BWw = new P.Wall(V(BAY[0], 0, 0), V(0, 0, 1), V(-1, 0, 0));
  const BEw = new P.Wall(V(BAY[1], 0, BAY[2]), V(0, 0, -1), V(1, 0, 0));
  const bl = BAY[1] - BAY[0];
  M.el = 'siding';
  P.boardBatten(M, BS, [[0, FT], [bl, FT], [bl, BB], [0, BB]], [[0.4, bl - 0.4, FL, CEIL]], VB);
  P.boardBatten(M, BWw, [[0, FT], [BAY[2], FT], [BAY[2], BB - 0.01], [0, BB - 0.01]], [[0.4, BAY[2] - 0.2, FL, CEIL]], VB);
  P.boardBatten(M, BEw, [[0, FT], [BAY[2], FT], [BAY[2], BB - 0.01], [0, BB - 0.01]], [[0.2, BAY[2] - 0.4, FL, CEIL]], VB);
  M.el = null;
  glaze(BS, [0.4, bl - 0.4, FL, CEIL], 4); glaze(BWw, [0.4, BAY[2] - 0.2, FL, CEIL], 1); glaze(BEw, [0.2, BAY[2] - 0.4, FL, CEIL], 1);
  for (const [w, len] of [[BS, bl], [BWw, BAY[2]], [BEw, BAY[2]]]) { band(w, 0, len, FT, FL - 0.12, 0.07, 'concrete'); band(w, 0, len, FL - 0.12, FL + 0.02, 0.09); }
  // steel header over the north glass wall (part of the structural steel), inside the wall
  M.el = 'cantilever'; M.add(B(1.0, HN - 0.75, CEIL + 0.1, 53.0, HN - 0.25, CEIL + 1.1), 'steel'); M.el = null;

  // first-level roof over the house, the deck and the entry: 1.5' slab, wood fascia, dark coping
  M.el = 'roof1';
  const roofRects = [[0, 0, BX0, HN + 0.19], [BX1, 0, HW, HN + 0.19], [BX0, 0, BX1, HN + 0.19], [BX0 + 0.05, -BAY[2], BX1 - 0.05, 0]];   // bay piece held inside the box walls so the faces never meet   // over the house and the bay; the box sits on the middle
  for (const [i, [x0, n0, x1, n1]] of roofRects.entries()) {
    M.el = i >= 2 ? 'roof1u' : 'roof1';
    M.add(B(x0, n0, CEIL + 0.05, x1, n1, RT - 0.1), 'lumber');
    M.add(B(x0, n0, RT - 0.1, x1, n1, RT), 'membrane');
    M.add(B(x0 + 0.1, n0 + 0.1, CEIL, x1 - 0.1, n1 - 0.1, CEIL + 0.05), 'gyp');
  }
  M.el = null;
  // over the deck and the entry (stays in every cutaway)
  const deckRoof = [[DX0, DN0, 0, HN + 0.19], [-4.0, 0, 0, DN0]];
  for (const [x0, n0, x1, n1] of deckRoof) {
    M.add(B(x0, n0, CEIL + 0.05, x1, n1, RT - 0.1), 'lumber');
    M.add(B(x0, n0, RT - 0.1, x1, n1, RT), 'membrane');
    M.add(B(x0, n0, CEIL - 0.02, x1, n1, CEIL + 0.05), 'soffit');   // wood ceiling over the deck
  }
  // fascia band and coping around the free roof edges
  M.el = 'siding';
  const fas = (x0, n0, x1, n1) => (x1 - x0 > n1 - n0) ? M.add(B(x0 + 0.01, n0, CEIL - 0.1, x1 - 0.01, n1, RT), 'siding') : M.add(B(x0, n0, CEIL - 0.1, x1, n1, RT), 'siding');
  fas(DX0 - 0.12, HN + 0.19, HW + 0.12, HN + 0.31);                                                // north, under the box too
  fas(DX0 - 0.12, DN0, DX0, HN + 0.31);                                                             // west, over the deck
  fas(DX0 - 0.12, DN0 - 0.12, -4.0, DN0); fas(-4.12, -0.12, -4.0, DN0);                              // deck south, entry west
  fas(-4.12, -0.12, BAY[0], 0.0); fas(BAY[1], -0.12, HW + 0.12, 0.0);                               // south
  fas(HW, -0.12, HW + 0.12, HN + 0.31);                                                             // east
  M.el = null;
  const cop = (x0, n0, x1, n1) => (x1 - x0 > n1 - n0) ? M.add(B(x0 + 0.01, n0, RT, x1 - 0.01, n1, RT + 0.12), 'flashing') : M.add(B(x0, n0, RT, x1, n1, RT + 0.13), 'flashing');
  cop(DX0 - 0.2, HN + 0.12, HW + 0.2, HN + 0.39); cop(DX0 - 0.2, DN0 - 0.2, DX0 + 0.15, HN + 0.39);
  cop(DX0 - 0.2, DN0 - 0.2, -4.0, DN0 + 0.15); cop(-4.2, -0.2, -3.85, DN0); cop(-4.2, -0.2, BX0, 0.15); cop(BX1, -0.2, HW + 0.2, 0.15); cop(HW - 0.15, -0.2, HW + 0.2, HN + 0.39);

  // ---------------------------------------------------------------- screened deck
  M.phase = 'porch';
  // corner pier at the northwest and a solid wall panel at the southwest, clad like the house
  M.el = 'siding';
  const pier = (x0, n0, x1, n1) => {
    for (const [w, len] of [[new P.Wall(V(x0, 0, -n0), V(1, 0, 0), V(0, 0, 1)), x1 - x0], [new P.Wall(V(x1, 0, -n1), V(-1, 0, 0), V(0, 0, -1)), x1 - x0],
      [new P.Wall(V(x0, 0, -n1), V(0, 0, 1), V(-1, 0, 0)), n1 - n0], [new P.Wall(V(x1, 0, -n0), V(0, 0, -1), V(1, 0, 0)), n1 - n0]])
      P.boardBatten(M, w, [[0, 0], [len, 0], [len, CEIL], [0, CEIL]], [], { ...VB, inner: null, wallDepth: 0.05, cornerWidth: 0.3 });   // narrow corner boards: two 0.7' boards would overlap on a 1' face
    M.add(B(x0 + 0.05, n0 + 0.05, 0, x1 - 0.05, n1 - 0.05, CEIL), 'trim');
    M.add(B(x0 - 0.06, n0 - 0.06, 0, x1 + 0.06, n1 + 0.06, 0.35), 'flashing');   // base flashing
  };
  const PW = 1.04, PN = HN + 0.19 - 4.77, PS = DN0 + 6.35;   // wall thickness, NW pier south end, SW wall north end
  pier(DX0, PN, DX0 + PW, HN + 0.19);
  pier(DX0, DN0, DX0 + PW, PS);
  M.el = 'porch';
  M.add(B(DX0 + 0.3, DN0 + 0.3, FT - 0.2, -0.2, HN, FL - 0.6), 'lumber');                       // deck framing on the piers
  for (let x = DX0 + 0.2; x < -0.1; x += 0.47) M.add(B(x, DN0 + 0.1, FL - 0.6, Math.min(x + 0.43, -0.05), HN + 0.1, FL - 0.48), 'deck');   // Cumaru boards
  for (const [x0, n0, x1, n1] of [[DX0 + 0.15, DN0 + 0.15, DX0 + 0.27, HN - 0.05], [DX0 + 0.27, DN0 + 0.15, -0.2, DN0 + 0.27], [DX0 + 0.27, HN - 0.17, -0.2, HN - 0.05]]) M.add(B(x0, n0, 0, x1, n1, FL - 0.48), 'deck');   // skirt boards, set back from the pier faces
  // Centor retractable screen housings at the open sides (screens shown retracted)
  M.add(B(DX0 + PW, HN - 0.25, CEIL - 0.45, -0.1, HN + 0.05, CEIL - 0.05), 'frame');        // north head
  M.add(B(DX0 + 0.1, PS, CEIL - 0.45, DX0 + 0.4, PN, CEIL - 0.05), 'frame');                  // west head
  M.add(B(DX0 + PW, DN0 + 0.05, CEIL - 0.45, -0.1, DN0 + 0.35, CEIL - 0.05), 'frame');        // south head
  M.el = null;

  // ---------------------------------------------------------------- the upper box
  M.phase = 'upper';
  M.el = 'cantilever';   // the steel floor frame that carries the box past the glass wall: two edge girders and cross beams, inside the floor
  M.add(B(BX0 + 0.5, BN0 + 0.4, BB + 0.3, BX0 + 1.3, BN1 - 0.4, BB + 1.3), 'steel');
  M.add(B(BX1 - 1.3, BN0 + 0.4, BB + 0.3, BX1 - 0.5, BN1 - 0.4, BB + 1.3), 'steel');
  for (let n = BN0 + 1.0; n < BN1 - 0.5; n += 5.5) M.add(B(BX0 + 1.3, n, BB + 0.4, BX1 - 1.3, n + 0.5, BB + 1.2), 'steel');
  M.el = null;
  for (const [x0, n0, x1, n1] of [[BX0 - 0.06, BN0 - 0.06, BX1 + 0.06, BN0 + 0.6], [BX0 - 0.06, BN1 - 0.6, BX1 + 0.06, BN1 + 0.06],
    [BX0 - 0.06, BN0 + 0.6, BX0 + 0.6, BN1 - 0.6], [BX1 - 0.6, BN0 + 0.6, BX1 + 0.06, BN1 - 0.6]]) M.add(B(x0, n0, BB, x1, n1, BB + 0.3), 'flashing');   // thin dark edge at the base of the box
  M.add(B(BX0 + 0.1, HN + 0.4, BB - 0.04, BX1 - 0.1, BN1 - 0.1, BB), 'soffit');   // wood soffit under the cantilever, north
  M.add(B(BX0 + 0.1, BN0 + 0.1, BB - 0.04, BX1 - 0.1, -BAY[2], BB), 'soffit');    // south
  M.phase = 'upperwalls';   // the box walls and glass, kept apart so the steel frame can be shown on its own
  const bS = new P.Wall(V(BX0, 0, -BN0), V(1, 0, 0), V(0, 0, 1));
  const bN = new P.Wall(V(BX1, 0, -BN1), V(-1, 0, 0), V(0, 0, -1));
  const bW = new P.Wall(V(BX0, 0, -BN1), V(0, 0, 1), V(-1, 0, 0));
  const bE = new P.Wall(V(BX1, 0, -BN0), V(0, 0, -1), V(1, 0, 0));
  const bw = BX1 - BX0, bl2 = BN1 - BN0, F2 = 13.7, C2 = 22.6;
  const nGl = [1.2, bw - 1.2, F2, C2];
  const wW1 = [17.0, 19.6, F2 + 0.6, C2 - 0.4], wW2 = [40.0, 43.0, 17.5, C2 - 0.6];
  const eW1b = [3.0, 9.0, 16.5, C2 - 0.4], eW2b = [22.0, 24.6, F2 + 0.6, C2 - 0.4];
  const sWb = [8.5, 13.5, 16.0, C2 - 0.6];
  M.el = 'boxsiding';
  const BB1 = BB + 0.3, BW = BT - 0.12;
  P.boardBatten(M, bN, [[0, BB1], [bw, BB1], [bw, BW], [0, BW]], [nGl], VB);
  P.boardBatten(M, bW, [[0, BB1], [bl2, BB1], [bl2, BW - 0.01], [0, BW - 0.01]], [wW1, wW2], VB);
  P.boardBatten(M, bE, [[0, BB1], [bl2, BB1], [bl2, BW - 0.01], [0, BW - 0.01]], [eW1b, eW2b], VB);
  P.boardBatten(M, bS, [[0, BB1], [bw, BB1], [bw, BW], [0, BW]], [sWb], VB);
  M.el = null;
  glaze(bN, nGl, 4); glaze(bW, wW1, 1); glaze(bW, wW2, 1); glaze(bE, eW1b, 2); glaze(bE, eW2b, 1); glaze(bS, sWb, 2);
  band(bN, 0, bw, BT - 0.4, BT, 0.1); band(bS, 0, bw, BT - 0.4, BT, 0.1); band(bW, 0, bl2, BT - 0.4, BT, 0.1); band(bE, 0, bl2, BT - 0.4, BT, 0.1);   // cap that closes the board tops
  // dark picture frame around the north glazing, as rendered
  for (const r of [[0.6, 1.2, F2 - 0.3, C2 + 0.6], [bw - 1.2, bw - 0.6, F2 - 0.3, C2 + 0.6], [1.2, bw - 1.2, C2, C2 + 0.6], [1.2, bw - 1.2, F2 - 0.3, F2]]) M.add(bN.box(r[0], r[1], r[2], r[3], 0, 0.28), 'flashing');
  // x-ray shell: plain box walls with no battens, only for the all-elements frame (ghosted there; hero.py drops the phase)
  M.phase = 'xray'; M.el = 'boxghost';
  for (const [w, len, holes, e] of [[bN, bw, [nGl], 0], [bS, bw, [sWb], 0], [bW, bl2, [wW1, wW2], 0.3], [bE, bl2, [eW1b, eW2b], 0.3]])
    M.add(w.slab([[e, BB1], [len - e, BB1], [len - e, BW], [e, BW]], holes.map((h) => [h[0], h[1], h[2], h[3]]), -0.3, 0), 'trim');
  M.el = null;
  M.phase = 'upper';
  M.el = 'boxshell';
  M.add(B(BX0 + 0.6, BN0 + 0.6, BB + 1.3, BX1 - 0.6, BN1 - 0.6, BB + 1.35), 'plank');    // box floor
  M.add(B(BX0 + 0.6, BN0 + 0.6, C2, BX1 - 0.6, BN1 - 0.6, C2 + 0.05), 'gyp');            // box ceiling
  // box roof
  M.add(B(BX0 + 0.7, BN0 + 0.7, BT - 0.9, BX1 - 0.7, BN1 - 0.7, BT - 0.1), 'lumber');
  M.add(B(BX0 - 0.12, BN0 - 0.12, BT - 0.1, BX1 + 0.12, BN1 + 0.12, BT), 'membrane');
  M.el = null;
  M.phase = 'upperwalls';
  for (const [x0, n0, x1, n1] of [[BX0 - 0.19, BN0 - 0.2, BX1 + 0.19, BN0 + 0.15], [BX0 - 0.19, BN1 - 0.15, BX1 + 0.19, BN1 + 0.2]]) M.add(B(x0, n0, BT, x1, n1, BT + 0.14), 'flashing');
  for (const [x0, n0, x1, n1] of [[BX0 - 0.2, BN0 - 0.2, BX0 + 0.15, BN1 + 0.2], [BX1 - 0.15, BN0 - 0.2, BX1 + 0.2, BN1 + 0.2]]) M.add(B(x0, n0, BT, x1, n1, BT + 0.15), 'flashing');

  // ---------------------------------------------------------------- green roofs and skylights
  M.phase = 'roof';
  M.el = 'greenroof';
  const gr = (x0, n0, x1, n1) => {   // sedum trays inside a 1' gravel strip
    // EPDM variant: membrane only, no gravel strip or sedum trays
  };
  gr(DX0 + 0.2, DN0 + 0.2, BX0 - 0.1, HN); gr(BX1 + 0.1, 0.2, HW - 0.2, HN);
  // EPDM variant: no entry tray
  for (const [x, n, s] of [[2.0, 18.0, 4.0], [38.0, 6.0, 3.0], [38.0, 11.5, 3.0], [38.0, 17.0, 3.0]]) {   // Velux flat-roof skylights on raised curbs
    M.add(B(x - 0.2, n - 0.2, RT, x + s + 0.2, n + s + 0.2, RT + 1.1), 'flashing');
    M.el = 'skyglass'; M.add(B(x, n, RT + 1.1, x + s, n + s, RT + 1.2), 'glass'); M.el = 'greenroof';
  }
  M.el = null;

  // ---------------------------------------------------------------- interior, seen through the glass
  M.phase = 'interior';
  M.add(B(0.6, 0.6, FL - 0.05, HW - 0.6, HN - 0.6, FL), 'plank');                       // white oak floor
  M.add(B(BAY[0] + 0.5, -BAY[2] + 0.5, FL - 0.05, BAY[1] - 0.5, 0.6, FL), 'plank');
  // partitions (bedroom wing to the east, mech, entry, kitchen run) and the kitchen island
  M.el = 'partitions';
  for (const [x0, n0, x1, n1] of [[40.0, 0.6, 40.4, 30.0], [40.4, 12.0, 53.4, 12.4], [8.0, 0.6, 8.4, 12.0], [8.4, 11.6, 19.0, 12.0], [14.0, 0.6, 14.4, 11.6]])
    M.add(B(x0, n0, FL, x1, n1, CEIL), 'gyp');
  M.el = null;
  M.add(B(8.6, 13.0, FL, 26.0, 15.2, FL + 3.0), 'walnut');                             // kitchen run
  M.add(B(15.0, 19.5, FL, 23.0, 22.5, FL + 3.0), 'walnut');                            // island
  M.add(B(15.0, 19.5, FL + 3.0, 23.0, 22.5, FL + 3.15), 'stone');
  for (const [x, n] of [[29.0, 22.0], [33.0, 22.0]]) M.add(B(x, n, FL, x + 3.2, n + 6.0, FL + 1.4), 'gyp');   // sofas, light upholstery
  M.add(B(28.0, 8.0, FL, 37.0, 11.0, FL + 2.5), 'timber');                              // dining table
  M.el = 'lamps'; for (const [x, n] of [[19.0, 21.0], [30.0, 9.5], [45.0, 20.0]]) M.add(P.cyl(x, CEIL - 1.4, -n, 0.5, CEIL - 0.9, 16), 'lamp'); M.el = null;

  // ---------------------------------------------------------------- floating stair to the box
  // per SD-04: UP from the great room, two steps south onto a landing at the east end of the bay, then a flight climbing west to the box.
  // 18 risers, white oak treads on a steel center stringer, frameless glass guard at the opening in the box floor.
  M.phase = 'stair'; M.el = 'stair';
  const R = 18, rise = (BB + 1.3 - FL) / R, run = 0.8, n0s = -3.85, sw = 3.5, xL = 29.3, xE = 33.9, nT = 14;
  for (const [k, n0, n1] of [[1, 0.75, 1.75], [2, -0.25, 0.75]]) M.add(B(xL + 0.6, n0, FL + k * rise - 0.17, xE, n1, FL + k * rise), 'plank');   // two steps
  M.add(B(xL, n0s, FL + 3 * rise - 0.17, xE, -0.25, FL + 3 * rise), 'plank');                              // landing
  M.add(B(xL + 0.3, n0s + 0.3, FL + 3 * rise - 0.45, xE - 0.3, -0.55, FL + 3 * rise - 0.17), 'steel');     // landing plate
  for (let j = 0; j < nT; j++) {
    const x1 = xL - j * run, y = FL + (4 + j) * rise;
    M.add(B(x1 - run - 0.1, n0s, y - 0.17, x1, n0s + sw, y), 'plank');
  }
  const L = nT * run, H = BB + 1.3 - (FL + 3 * rise), mid = n0s + sw / 2;
  M.add(P.obox(V(xL - L / 2, FL + 3 * rise + H / 2 - 0.3, -mid), V(-L, H, 0).normalize(), V(-H, -L, 0).normalize(), V(0, 0, 1), Math.hypot(L, H), 0.6, 0.5), 'steel');
  M.phase = 'upper'; M.el = 'boxshell';
  M.add(B(xL - L, n0s + sw + 0.3, BB + 1.3, xE, n0s + sw + 0.35, BB + 4.8), 'glass');   // frameless glass guard along the opening, in the box
  M.phase = 'interior';
  M.el = null;

  // ---------------------------------------------------------------- site: stone patio at the glass wall, concrete walk to the entry
  M.phase = 'site';
  M.add(B(BX0, HN + 0.25, 0.0, BX1, HN + 8.25, FL - 0.25), 'stone');            // stone patio 8' x 22' under the cantilever (SD-04), stone-faced base
  M.add(B(BX0 - 0.08, HN + 0.25, FL - 0.25, BX1 + 0.08, HN + 8.33, FL - 0.12), 'concrete');   // cap
  M.add(B(-3.6, -6.5, 0.0, 6.0, -0.2, 0.2), 'stone');

  return M.group();
}
