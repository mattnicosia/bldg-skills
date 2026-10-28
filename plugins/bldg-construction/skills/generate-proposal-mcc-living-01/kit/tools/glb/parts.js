// Montana bid presentation kit: parts for building a render-quality model from drawings.
// A project script (model/build.js in the project folder) calls these to assemble the building,
// then tools/make_glb.mjs exports it as model.glb for model.mode "glb".
//
// Units are feet. World axes: x east, y up, z south (plan north is -z).
// A wall frame places local (u, v, w) points: u runs along the wall (left to right seen from
// outside), v is height above grade, w is outward from the outer face of the sheathing.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

// ------------------------------------------------------------------ materials
export function materials(over = {}) {
  const M = (o) => new THREE.MeshStandardMaterial(o);
  const base = {
    siding: { color: '#605a53', roughness: 0.82 },
    trim: { color: '#5a534b', roughness: 0.75 },
    frame: { color: '#3a3129', roughness: 0.5 },
    glass: { color: '#1d252b', roughness: 0.03, metalness: 0.15 },
    roof: { color: '#a29d95', roughness: 0.5, metalness: 0.5 },
    flashing: { color: '#8f8f8d', roughness: 0.4, metalness: 0.75 },
    concrete: { color: '#8f8c86', roughness: 0.95 },
    deck: { color: '#6e4630', roughness: 0.7 },
    footing: { color: '#7f7c76', roughness: 0.95 },
    slab: { color: '#a19e97', roughness: 0.9 },
    gravel: { color: '#8a857c', roughness: 1 },
    lumber: { color: '#b89a72', roughness: 0.85 },
    membrane: { color: '#2a2a2a', roughness: 0.9 },
    steel: { color: '#1e1e1e', roughness: 0.5, metalness: 0.5 },
    stainless: { color: '#cfd1d3', roughness: 0.22, metalness: 1.0 },
    soffit: { color: '#4a423b', roughness: 0.85 },
    // interior
    gyp: { color: '#e9e6df', roughness: 0.92 },
    timber: { color: '#7a5a3e', roughness: 0.72 },
    walnut: { color: '#4a3326', roughness: 0.55 },
    plank: { color: '#9c7652', roughness: 0.62 },
    machine: { color: '#5c6066', roughness: 0.45, metalness: 0.3 },
    copper: { color: '#b87333', roughness: 0.3, metalness: 1.0 },
    fabric: { color: '#3d4249', roughness: 0.95 },
    lamp: { color: '#fff4e0', emissive: '#ffd59a', emissiveIntensity: 1.0, roughness: 0.5 },
  };
  const out = {};
  for (const [k, v] of Object.entries({ ...base, ...over })) { out[k] = M(v); out[k].name = k; }
  return out;
}

// ------------------------------------------------------------------ collector
// Parts are collected per phase and material, then merged, so a whole building is a few dozen draw calls.
export class Model {
  constructor(mats) { this.mats = mats; this.bins = new Map(); this.phase = 'main'; this.el = null; }
  add(geom, mat) {
    const key = this.phase + '|' + mat + (this.el ? '|' + this.el : '');
    if (!this.bins.has(key)) this.bins.set(key, []);
    const g = geom.index ? geom.toNonIndexed() : geom;
    for (const a of Object.keys(g.attributes)) if (!['position', 'normal', 'uv'].includes(a)) g.deleteAttribute(a);
    if (!g.attributes.uv) g.setAttribute('uv', new THREE.Float32BufferAttribute(new Float32Array(g.attributes.position.count * 2), 2));
    if (!g.attributes.normal) g.computeVertexNormals();
    this.bins.get(key).push(g);
  }
  group() {
    const root = new THREE.Group(); root.name = 'Building';
    const phases = new Map();
    for (const [key, list] of this.bins) {
      const [ph, mat, el] = key.split('|');
      if (!phases.has(ph)) { const g = new THREE.Group(); g.name = `${ph} [phase:${ph}]`; phases.set(ph, g); root.add(g); }
      const m = new THREE.Mesh(mergeGeometries(list, false), this.mats[mat]); m.name = `${ph} ${mat}` + (el ? ` [el:${el}]` : '');   // M.el tags a part (priced element) as its own mesh
      phases.get(ph).add(m);
    }
    return root;
  }
}

// ------------------------------------------------------------------ primitives
const V = (x, y, z) => new THREE.Vector3(x, y, z);
// an oriented box from a local frame: center c, axes ax/ay/az (unit), half sizes
export function obox(c, ax, ay, az, sx, sy, sz) {
  if (new THREE.Vector3().crossVectors(ax, ay).dot(az) < 0) az = az.clone().negate();   // keep the basis right handed, or the faces turn inside out
  const g = new THREE.BoxGeometry(sx, sy, sz);
  const m = new THREE.Matrix4().makeBasis(ax, ay, az); m.setPosition(c);
  return g.applyMatrix4(m);
}
// axis-aligned box from min/max corners
export function abox(x0, y0, z0, x1, y1, z1) {
  const g = new THREE.BoxGeometry(Math.abs(x1 - x0), Math.abs(y1 - y0), Math.abs(z1 - z0));
  return g.translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
}
export function cyl(x, y0, z, r, y1, seg = 16) { return new THREE.CylinderGeometry(r, r, y1 - y0, seg).translate(x, (y0 + y1) / 2, z); }

export class Wall {
  // o: world point at u=0, v=0 on the outer face. U: along-wall unit vector. N: outward normal.
  constructor(o, U, N) { this.o = o.clone(); this.U = U.clone().normalize(); this.N = N.clone().normalize(); this.Y = V(0, 1, 0); }
  p(u, v, w = 0) { return this.o.clone().addScaledVector(this.U, u).addScaledVector(this.Y, v).addScaledVector(this.N, w); }
  // a box in wall coordinates: u0..u1, v0..v1, w0..w1
  box(u0, u1, v0, v1, w0, w1) { const c = this.p((u0 + u1) / 2, (v0 + v1) / 2, (w0 + w1) / 2); return obox(c, this.U, this.Y, this.N, Math.abs(u1 - u0), Math.abs(v1 - v0), Math.abs(w1 - w0)); }
  // a flat slab whose outline is a polygon in (u, v), with rectangular holes, from w0 to w1
  slab(poly, holes, w0, w1) {
    const s = new THREE.Shape(poly.map(([u, v]) => new THREE.Vector2(u, v)));
    for (const h of holes) s.holes.push(new THREE.Path([new THREE.Vector2(h[0], h[2]), new THREE.Vector2(h[1], h[2]), new THREE.Vector2(h[1], h[3]), new THREE.Vector2(h[0], h[3])]));
    const g = new THREE.ExtrudeGeometry(s, { depth: w1 - w0, bevelEnabled: false, curveSegments: 1 });
    g.translate(0, 0, w0);
    const m = new THREE.Matrix4().makeBasis(this.U, this.Y, this.N); m.setPosition(this.o);
    g.applyMatrix4(m);
    if (m.determinant() < 0) {   // a mirrored frame flips the winding: put it back
      const idx = g.index; if (idx) { for (let i = 0; i < idx.count; i += 3) { const a = idx.getX(i + 1); idx.setX(i + 1, idx.getX(i + 2)); idx.setX(i + 2, a); } }
      else { const p = g.attributes.position; for (let i = 0; i < p.count; i += 3) for (let k = 0; k < 3; k++) { const a = p.getComponent(i + 1, k); p.setComponent(i + 1, k, p.getComponent(i + 2, k)); p.setComponent(i + 2, k, a); } }
      g.computeVertexNormals();
    }
    return g;
  }
}

// top of a polygon outline at u (polygons are listed counterclockwise from the bottom left)
function spanAt(poly, u) {
  const ys = [];
  for (let i = 0; i < poly.length; i++) {
    const [a, b] = [poly[i], poly[(i + 1) % poly.length]];
    if ((a[0] <= u && b[0] > u) || (b[0] <= u && a[0] > u)) ys.push(a[1] + (b[1] - a[1]) * (u - a[0]) / (b[0] - a[0]));
  }
  ys.sort((p, q) => p - q); return ys.length >= 2 ? [ys[0], ys[ys.length - 1]] : null;
}

// Board and batten cladding on a wall: the board slab with openings cut, battens at a spacing that
// stop at openings, corner boards at the ends.
export function boardBatten(M, wall, poly, openings, o = {}) {
  const t = o.thick ?? 0.06, bw = o.batten ?? 0.22, bd = o.battenDepth ?? 0.14, sp = o.spacing ?? 1.25;
  const holes = openings.map((h) => [h[0], h[1], h[2], h[3]]);
  M.add(wall.slab(poly, holes, -t, 0), o.mat || 'siding');
  // sheathing and framing depth behind, so the openings have returns
  M.add(wall.slab(poly, holes, -(o.wallDepth ?? 0.6), -t), o.backMat || 'trim');
  // o.inner: a finish face on the room side (painted drywall), so views through the glass see a lit room
  if (o.inner) M.add(wall.slab(poly, holes, -(o.wallDepth ?? 0.6) - 0.04, -(o.wallDepth ?? 0.6)), o.inner);
  const us = poly.map((p) => p[0]), u0 = Math.min(...us), u1 = Math.max(...us);
  for (let u = u0 + (o.offset ?? sp / 2); u < u1 - bw / 2; u += sp) {
    const span = spanAt(poly, u); if (!span) continue;
    let segs = [[span[0], span[1] - 0.05]];
    for (const h of openings) {
      const pad = (o.casing ?? 0.35) + 0.02;
      if (u + bw / 2 > h[0] - pad && u - bw / 2 < h[1] + pad) {
        const out = [];
        for (const [a, b] of segs) { if (h[3] + pad < a || h[2] - pad > b) { out.push([a, b]); continue; } if (h[2] - pad > a) out.push([a, h[2] - pad]); if (h[3] + pad < b) out.push([h[3] + pad, b]); }
        segs = out;
      }
    }
    for (const [a, b] of segs) if (b - a > 0.2) M.add(wall.box(u - bw / 2, u + bw / 2, a, b, 0, bd), o.mat || 'siding');
  }
  if (o.corners !== false) {
    const cw = o.cornerWidth ?? 0.45, top = (u) => (spanAt(poly, u) || [0, 0])[1];
    const v0 = Math.min(...poly.map((p) => p[1]));
    const ext = bd + 0.04;   // corner boards lap past the corner so the two walls close
    if (o.cornerLeft !== false) M.add(wall.box(u0 - ext, u0 + cw, v0, top(u0 + 0.01), 0, bd + 0.02), 'trim');
    if (o.cornerRight !== false) M.add(wall.box(u1 - cw, u1 + ext, v0, top(u1 - 0.01), 0, bd + 0.02), 'trim');
  }
}

// casing around an opening, proud of the battens
export function casing(M, wall, [u0, u1, v0, v1], o = {}) {
  const c = o.width ?? 0.35, d = o.depth ?? 0.1, mat = o.mat || 'trim';
  M.add(wall.box(u0 - c, u0, v0 - (o.sill ? 0 : 0), v1 + c, 0, d), mat);
  M.add(wall.box(u1, u1 + c, v0, v1 + c, 0, d), mat);
  M.add(wall.box(u0 - c - 0.06, u1 + c + 0.06, v1, v1 + c + 0.06, 0, d + 0.03), mat);   // head
  if (o.sill !== false) M.add(wall.box(u0 - c - 0.08, u1 + c + 0.08, v0 - 0.16, v0, 0, d + 0.12), mat);   // no sill: the jambs run to v0 (a second jamb here sat on the first and rendered black)
}

// a glazed unit set into an opening: frame, sash rails, muntin grid, glass recessed in the wall
export function glazedUnit(M, wall, [u0, u1, v0, v1], o = {}) {
  const inset = o.inset ?? -0.28, f = o.frame ?? 0.22, md = 0.07, mw = o.muntin ?? 0.065;
  const fm = o.frameMat || 'frame';
  M.add(wall.box(u0, u1, v0, v1, inset - 0.12, inset - 0.08), 'glass');
  // frame
  M.add(wall.box(u0, u0 + f, v0, v1, inset - 0.1, inset + 0.06), fm);
  M.add(wall.box(u1 - f, u1, v0, v1, inset - 0.1, inset + 0.06), fm);
  M.add(wall.box(u0 + f, u1 - f, v1 - f, v1, inset - 0.1, inset + 0.06), fm);          // head and sill between the jambs, so no faces overlap at the corners
  M.add(wall.box(u0 + f, u1 - f, v0, v0 + f * 1.2, inset - 0.1, inset + 0.06), fm);
  // panes: o.panes = [[uA,uB,vA,vB, cols, rows], ...] in absolute wall coordinates; default one pane
  const panes = o.panes || [[u0 + f, u1 - f, v0 + f * 1.2, v1 - f, o.cols ?? 2, o.rows ?? 2]];
  for (const [a, b, c, d, cols, rows] of panes) {
    for (let i = 1; i < cols; i++) { const u = a + (b - a) * i / cols; M.add(wall.box(u - mw / 2, u + mw / 2, c, d, inset - 0.09, inset - 0.09 + md), fm); }
    for (let j = 1; j < rows; j++) { const v = c + (d - c) * j / rows; M.add(wall.box(a, b, v - mw / 2, v + mw / 2, inset - 0.09, inset - 0.09 + md), fm); }
  }
  for (const r of o.rails || []) M.add(wall.box(u0, u1, r - (o.railH ?? 0.18) / 2, r + (o.railH ?? 0.18) / 2, inset - 0.1, inset + 0.04), fm);
  for (const s of o.stiles || []) M.add(wall.box(s - (o.stileW ?? 0.2) / 2, s + (o.stileW ?? 0.2) / 2, v0, v1, inset - 0.1, inset + 0.04), fm);
}

// double hung window with casing and sill
export function window(M, wall, rect, o = {}) {
  const [u0, u1, v0, v1] = rect, f = 0.2, meet = (v0 + v1) / 2;
  casing(M, wall, rect, o.casing || {});
  glazedUnit(M, wall, rect, {
    panes: [[u0 + f, u1 - f, meet + 0.08, v1 - f, o.cols ?? 2, o.rowsTop ?? 3], [u0 + f, u1 - f, v0 + f * 1.2, meet - 0.08, o.cols ?? 2, o.rowsBottom ?? 3]],
    rails: [meet],
  });
}

// folding glass doors with a transom: leaves x lites, transom units x lites
export function bifold(M, wall, rect, o = {}) {
  const [u0, u1, v0, v1] = rect, th = o.transom ?? 2.3, leaves = o.leaves ?? 4;
  const vt = v1 - th;
  casing(M, wall, rect, { width: 0.5, depth: 0.12, sill: false });
  // leaves
  const lw = (u1 - u0) / leaves, panes = [], stiles = [];
  for (let i = 0; i < leaves; i++) {
    const a = u0 + i * lw, b = a + lw; if (i) stiles.push(a);
    panes.push([a + 0.2, b - 0.2, v0 + 0.55, vt - 0.2, o.cols ?? 2, o.rows ?? 6]);
  }
  glazedUnit(M, wall, [u0, u1, v0, vt], { panes, stiles, stileW: 0.36, frame: 0.24, inset: -0.32 });
  M.add(wall.box(u0, u1, v0, v0 + 0.55, -0.42, -0.24), 'frame');     // bottom rails
  // transom
  const tpanes = [], tst = [];
  for (let i = 0; i < leaves; i++) { const a = u0 + i * lw, b = a + lw; if (i) tst.push(a); tpanes.push([a + 0.2, b - 0.2, vt + 0.25, v1 - 0.22, o.tcols ?? 2, 1]); }
  M.add(wall.box(u0, u1, vt - 0.05, vt + 0.25, -0.34, 0.08), 'trim');   // mullion between door and transom
  glazedUnit(M, wall, [u0, u1, vt + 0.05, v1], { panes: tpanes, stiles: tst, stileW: 0.3, frame: 0.2, inset: -0.3 });
}

// A standing seam roof plane: a slab between four corners (eave left, eave right, ridge right, ridge left),
// with seams running eave to ridge at a spacing and a fascia band down the eave edge.
export function roofPlane(M, eL, eR, rR, rL, o = {}) {
  const t = o.thick ?? 0.35, sp = o.seam ?? 1.33, sh = o.seamH ?? 0.12, sw = o.seamW ?? 0.07;
  const along = eR.clone().sub(eL), up = rL.clone().sub(eL);
  const L = along.length(), H = up.length();
  const ax = along.clone().normalize(), ay = up.clone().normalize(), nz = new THREE.Vector3().crossVectors(ax, ay).normalize();
  if (nz.y < 0) nz.negate();
  const c = eL.clone().addScaledVector(along, 0.5).addScaledVector(up, 0.5).addScaledVector(nz, -t / 2);
  M.add(obox(c, ax, ay, nz, L, H, t), o.mat || 'roof');
  M.add(obox(c.clone().addScaledVector(nz, -t / 2 - 0.02), ax, ay, nz, L, H, 0.04), o.soffit || 'soffit');
  if (o.seams !== false) for (let s = sp / 2; s < L; s += sp) {
    const p = eL.clone().addScaledVector(ax, s).addScaledVector(up, 0.5).addScaledVector(nz, sh / 2);
    M.add(obox(p, ax, ay, nz, sw, H, sh), o.mat || 'roof');
  }
  if (o.fascia !== false) {
    const fh = o.fasciaH ?? 0.55, out = new THREE.Vector3().crossVectors(V(0, 1, 0), ax).normalize();
    if (out.dot(eL.clone().sub(rL)) < 0) out.negate();
    const fc = eL.clone().addScaledVector(along, 0.5).addScaledVector(V(0, -1, 0), fh / 2 - 0.05).addScaledVector(out, 0.04);
    M.add(obox(fc, ax, V(0, 1, 0), out, L, fh, 0.1), o.fasciaMat || 'trim');
    // drip edge
    M.add(obox(eL.clone().addScaledVector(along, 0.5).addScaledVector(out, 0.07), ax, V(0, 1, 0), out, L, 0.08, 0.06), 'flashing');
  }
  return { ax, ay, nz, L, H };
}
// a rake edge board along a sloped edge from a to b
export function rake(M, a, b, o = {}) {
  const d = b.clone().sub(a), L = d.length(), ax = d.clone().normalize();
  const out = o.out.clone().normalize(), ay = new THREE.Vector3().crossVectors(out, ax).normalize();
  if (ay.y > 0) ay.negate();   // ay points down the face of the board
  const c = a.clone().addScaledVector(d, 0.5).addScaledVector(ay, (o.h ?? 0.5) / 2 - (o.lift ?? 0.12)).addScaledVector(out, o.w ?? 0.05);
  M.add(obox(c, ax, ay, out, L, o.h ?? 0.5, 0.1), o.mat || 'trim');
}
// half round gutter along an eave line and round downspouts
export function gutter(M, a, b, out, o = {}) {
  const d = b.clone().sub(a), L = d.length(), r = o.r ?? 0.25;
  const g = new THREE.CylinderGeometry(r, r, L, 12, 1, true, 0, Math.PI);
  const ax = d.clone().normalize(), o2 = out.clone().normalize();
  const m = new THREE.Matrix4().makeBasis(o2, ax, new THREE.Vector3().crossVectors(o2, ax));
  // rotate so the open half faces up
  g.rotateY(Math.PI / 2); g.applyMatrix4(m);
  g.translate(...a.clone().addScaledVector(d, 0.5).addScaledVector(o2, r + 0.05).toArray());
  M.add(g, 'flashing');
}
export function downspout(M, x, z, yTop, o = {}) { M.add(cyl(x, o.bottom ?? 0.2, z, o.r ?? 0.17, yTop, 12), 'flashing'); }

// a horse weathervane on a rod: arrow, letters left out, a running horse in silhouette
export function weathervane(M, x, y, z, s = 1) {
  M.add(cyl(x, y, z, 0.05 * s, y + 2.6 * s, 8), 'steel');
  M.add(new THREE.SphereGeometry(0.2 * s, 12, 8).translate(x, y + 0.35 * s, z), 'steel');
  M.add(abox(x - 1.1 * s, y + 1.45 * s, z - 0.03, x + 1.1 * s, y + 1.52 * s, z + 0.03), 'steel');    // N S bar
  M.add(abox(x - 0.03, y + 1.45 * s, z - 1.1 * s, x + 0.03, y + 1.52 * s, z + 1.1 * s), 'steel');    // E W bar
  const h = new THREE.Shape();
  const pts = [[-1.3, 0], [-0.9, 0.35], [-0.5, 0.4], [0.35, 0.42], [0.65, 0.75], [0.95, 0.8], [1.15, 0.62], [0.85, 0.5], [0.7, 0.2], [1.1, -0.1], [0.95, -0.2], [0.45, 0.05], [-0.4, 0.05], [-0.8, -0.35], [-1.0, -0.3], [-0.75, 0.05], [-1.2, -0.05]];
  pts.forEach(([u, v], i) => (i ? h.lineTo(u * s, v * s) : h.moveTo(u * s, v * s)));
  const g = new THREE.ExtrudeGeometry(h, { depth: 0.06 * s, bevelEnabled: false }).translate(0, 0, -0.03 * s);
  g.translate(x, y + 2.2 * s, z);
  M.add(g, 'steel');
}
