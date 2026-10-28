// Montana bid presentation kit: the 3D world.
// One scene, one camera, driven by the scroll. The model comes from one of three sources:
//   glb      the architect's model (SketchUp, Revit, Rhino exported to .glb)
//   massing  volumes built from the drawings (plans for footprints, elevations for heights and skins)
//   images   no 3D at all: renders or drawings crossfade behind the copy
// Every camera view is computed from the model's bounding box, so a new project needs no camera work.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { EXRLoader } from 'three/addons/loaders/EXRLoader.js';

const D = window.PROPOSAL, CFG = D.model || { mode: 'images' };
const ROOT = document.documentElement;
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
const NARROW = () => innerWidth < 760;
const TOUCH = matchMedia('(pointer: coarse)').matches;
const clamp01 = (v) => Math.min(1, Math.max(0, v));
const ease = (t) => t * t * (3 - 2 * t);
const STOPS = window.STOPS;           // built by page.js: { id, type, s0, s1, a, b, len, side, view, ... }
const PAGE = window.PAGE;             // page.js hooks: renderStops(p), schedU(p), schedTime(u)

let pTarget = 0, pNow = 0;
function readScroll() { const max = document.documentElement.scrollHeight - innerHeight; pTarget = max > 0 ? clamp01(scrollY / max) : 0; }
addEventListener('scroll', readScroll, { passive: true });
readScroll(); pNow = pTarget;
window.__jump = (p) => { pTarget = pNow = p; };

// ============================================================ renderer, light, sky
const canvas = document.getElementById('world');
let renderer;
try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' }); }
catch (e) { ROOT.classList.add('no-webgl'); throw e; }
const DPR = () => Math.min(devicePixelRatio || 1, NARROW() ? 1.25 : 1.6);
renderer.setPixelRatio(DPR());
renderer.setSize(innerWidth, innerHeight, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = CFG.setting === 'landscape' ? 1.08 : 0.95;
renderer.shadowMap.enabled = true;
const LAND = CFG.setting === 'landscape';   // a lawn, a sky and a tree line instead of the paper table
renderer.shadowMap.type = LAND ? THREE.PCFSoftShadowMap : THREE.PCFShadowMap;
renderer.localClippingEnabled = true;

const scene = new THREE.Scene();
const BONE = new THREE.Color('#f2efe9'), DUSKC = new THREE.Color('#2a3350');
scene.background = BONE.clone();
const pmrem = new THREE.PMREMGenerator(renderer);
// ---- the landscape setting: a gradient sky dome, used for the background and the reflections
const SKY = { top: new THREE.Color('#4d84c4'), hor: new THREE.Color('#dbe5ec'), low: new THREE.Color('#8d957c') };
const SKYD = { top: new THREE.Color('#1c2440'), hor: new THREE.Color('#5a5f78'), low: new THREE.Color('#20242c') };
function skyMat() {
  return new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false, toneMapped: false,
    uniforms: { top: { value: SKY.top.clone() }, hor: { value: SKY.hor.clone() }, low: { value: SKY.low.clone() } },
    vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: `uniform vec3 top; uniform vec3 hor; uniform vec3 low; varying vec3 vP;
      float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float n2(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f); return mix(mix(h2(i), h2(i+vec2(1,0)), f.x), mix(h2(i+vec2(0,1)), h2(i+vec2(1,1)), f.x), f.y); }
      float fbm(vec2 p){ float v = 0.0, a = 0.5; for (int i = 0; i < 5; i++) { v += a * n2(p); p *= 2.03; a *= 0.5; } return v; }
      void main(){ float h = vP.y; vec3 c = h > 0.0 ? mix(hor, top, pow(clamp(h,0.0,1.0), 0.55)) : mix(hor, low, pow(clamp(-h,0.0,1.0), 0.35));
        if (h > 0.02) { vec2 q = vP.xz / (h + 0.25) * 1.6; float cl = smoothstep(0.46, 0.8, fbm(q + vec2(3.1, 1.7))) * smoothstep(0.02, 0.25, h); c = mix(c, mix(hor, vec3(1.0), 0.75), cl * 0.75); }
        gl_FragColor = vec4(c, 1.0); }` });
}
let DOME = null, COMP = null, AOP = null, PARTIAL = false;
function setupAO() {
  if (!LAND || NARROW() || CFG.ao === false) return;
  COMP = new EffectComposer(renderer); COMP.setPixelRatio(DPR()); COMP.setSize(innerWidth, innerHeight);
  COMP.addPass(new RenderPass(scene, camera));
  AOP = new GTAOPass(scene, camera, innerWidth, innerHeight);
  AOP.updateGtaoMaterial({ radius: CFG.aoRadius ?? 2.2, distanceExponent: 1.2, thickness: 2.0, scale: 1.0, samples: 16 });
  AOP.blendIntensity = CFG.aoIntensity ?? 0.95;
  COMP.addPass(AOP); COMP.addPass(new OutputPass());
}
if (LAND) {
  const env = new THREE.Scene();
  env.add(new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), skyMat()));
  const sunBall = new THREE.Mesh(new THREE.SphereGeometry(3, 16, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(14, 12, 10) }));
  sunBall.position.set(-24, 30, 30); env.add(sunBall);
  scene.environment = pmrem.fromScene(env, 0.02).texture;
  scene.environmentIntensity = 0.85;
  DOME = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 24), skyMat()); DOME.renderOrder = -1; DOME.frustumCulled = false; scene.add(DOME);
} else {
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.45;
}
const hemi = LAND ? new THREE.HemisphereLight(0xe2e6ea, 0x7a8458, 0.55) : new THREE.HemisphereLight(0xeef2f7, 0xb9ae9b, 0.7);
const sun = new THREE.DirectionalLight(LAND ? 0xffe3bf : 0xfff0e0, LAND ? 4.6 : 3.0);
const SUN0 = sun.intensity, HEMI0 = hemi.intensity;
sun.castShadow = true;
sun.shadow.mapSize.set(NARROW() ? 2048 : LAND ? 4096 : 2048, NARROW() ? 2048 : LAND ? 4096 : 2048);
if (LAND) { sun.shadow.radius = 3; sun.shadow.normalBias = 0.09; sun.shadow.bias = -0.0003; }
sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.05;
scene.add(hemi, sun, sun.target);
const camera = new THREE.PerspectiveCamera(32, innerWidth / innerHeight, 1, 20000);

// ============================================================ materials
const MAT = {
  dark_siding: { color: '#2b2c2e', roughness: 0.85 }, light_siding: { color: '#d9d4ca', roughness: 0.85 },
  wood: { color: '#b0875c', roughness: 0.8 }, cedar: { color: '#9a7350', roughness: 0.8 },
  concrete: { color: '#c9c4bb', roughness: 0.95 }, stucco: { color: '#ece8e0', roughness: 0.95 },
  white: { color: '#f4f2ee', roughness: 0.9 }, paper: { color: '#efebe4', roughness: 0.95 },
  roof: { color: '#3a3c3f', roughness: 0.8 }, steel: { color: '#303236', roughness: 0.5, metalness: 0.6 },
  stone: { color: '#a59b8c', roughness: 0.95 }, brick: { color: '#8e5a46', roughness: 0.95 },
  glass: { color: '#26303a', roughness: 0.08, metalness: 0.4 }, green: { color: '#8a9a6c', roughness: 1 },
  lawn: { color: '#c9c8ae', roughness: 1 }, paving: { color: '#d8d2c6', roughness: 1 }, asphalt: { color: '#8f8c86', roughness: 1 },
  water: { color: '#8ea3ad', roughness: 0.1, metalness: 0.2 },
};
const matCache = new Map();
function mat(name, extra = {}) {
  const key = name + JSON.stringify(extra);
  if (!matCache.has(key)) {
    const m = MAT[name] || (/^#/.test(name) ? { color: name, roughness: 0.85 } : MAT.paper);
    matCache.set(key, new THREE.MeshStandardMaterial({ ...m, ...extra }));
  }
  return matCache.get(key);
}

// ============================================================ the model
// Every mesh carries userData.phase (for the build reveal) and userData.alt (shown only when that
// alternate is switched on). Phases reveal with a rising clip plane, so any geometry works.
const model = new THREE.Group(); scene.add(model);
const PHASES = (D.phases || []).map((p) => p.id);
const textures = new THREE.TextureLoader();

function polyShape(pts) { const s = new THREE.Shape(); pts.forEach(([x, y], i) => (i ? s.lineTo(x, y) : s.moveTo(x, y))); s.closePath(); return s; }
// plan coordinates: x east, y north, feet. Scene: x east, z south, y up.
function extrude(pts, base, top) {
  const g = new THREE.ExtrudeGeometry(polyShape(pts), { depth: top - base, bevelEnabled: false });
  g.rotateX(-Math.PI / 2); g.translate(0, base, 0);   // shape y (north) becomes -z
  return g;
}
function roofGeom(v) {
  const r = v.roof || { type: 'flat' };
  const xs = v.footprint.map((p) => p[0]), ys = v.footprint.map((p) => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys), top = v.top;
  if (r.type === 'flat' || !r.type) return null;
  const rise = (r.ridge ?? top + 6) - top;
  const g = new THREE.BufferGeometry(); let P;
  const A = (x, y, h) => [x, top + h, -y];
  if (r.type === 'gable') {
    if ((r.axis || 'x') === 'x') { const ym = (y0 + y1) / 2; P = [A(x0, y0, 0), A(x1, y0, 0), A(x1, ym, rise), A(x0, ym, rise), A(x0, y1, 0), A(x1, y1, 0)];
      g.setIndex([0, 1, 2, 0, 2, 3, 3, 2, 5, 3, 5, 4, 0, 3, 4, 1, 5, 2]); }
    else { const xm = (x0 + x1) / 2; P = [A(x0, y0, 0), A(x0, y1, 0), A(xm, y1, rise), A(xm, y0, rise), A(x1, y0, 0), A(x1, y1, 0)];
      g.setIndex([0, 2, 1, 0, 3, 2, 3, 5, 2, 3, 4, 5, 0, 4, 3, 1, 2, 5]); }
  } else if (r.type === 'shed') {
    const hi = r.high || 'N';
    const h = (x, y) => ({ N: (y - y0) / (y1 - y0), S: (y1 - y) / (y1 - y0), E: (x - x0) / (x1 - x0), W: (x1 - x) / (x1 - x0) }[hi]) * rise;
    P = [A(x0, y0, h(x0, y0)), A(x1, y0, h(x1, y0)), A(x1, y1, h(x1, y1)), A(x0, y1, h(x0, y1)), A(x0, y0, 0), A(x1, y0, 0), A(x1, y1, 0), A(x0, y1, 0)];
    g.setIndex([0, 1, 2, 0, 2, 3, 4, 5, 1, 4, 1, 0, 5, 6, 2, 5, 2, 1, 6, 7, 3, 6, 3, 2, 7, 4, 0, 7, 0, 3]);
  } else if (r.type === 'hip') {
    const ym = (y0 + y1) / 2, inset = Math.min(x1 - x0, y1 - y0) / 2;
    P = [A(x0, y0, 0), A(x1, y0, 0), A(x1, y1, 0), A(x0, y1, 0), A(x0 + inset, ym, rise), A(x1 - inset, ym, rise)];
    g.setIndex([0, 1, 5, 0, 5, 4, 1, 2, 5, 2, 3, 4, 2, 4, 5, 3, 0, 4]);
  } else return null;
  g.setAttribute('position', new THREE.Float32BufferAttribute(P.flat(), 3));
  const ng = g.toNonIndexed(); ng.computeVertexNormals(); return ng;
}
// Elevation skins: each elevation drawing is projected onto the walls that face it. Crop the
// elevation from grade to the highest point and edge to edge of the building, and it lands in place.
const DIRS = { S: new THREE.Vector3(0, 0, 1), N: new THREE.Vector3(0, 0, -1), E: new THREE.Vector3(1, 0, 0), W: new THREE.Vector3(-1, 0, 0) };
function skinFaces(geom, elev, bb, matFor) {
  // split triangles by facing: S, N, E, W walls, and everything else (roofs, soffits)
  const g = geom.index ? geom.toNonIndexed() : geom; g.computeVertexNormals();
  const pos = g.attributes.position, nrm = g.attributes.normal, n = pos.count;
  const uv = new Float32Array(n * 2), groups = [];
  const _n = new THREE.Vector3();
  let cur = null;
  for (let t = 0; t < n; t += 3) {
    _n.set(nrm.getX(t), nrm.getY(t), nrm.getZ(t));
    let k = 'top';
    if (Math.abs(_n.y) < 0.5) { let best = -1; for (const d in DIRS) { const dt = _n.dot(DIRS[d]); if (dt > best) { best = dt; k = d; } } }
    for (let j = 0; j < 3; j++) {
      const x = pos.getX(t + j), y = pos.getY(t + j), z = pos.getZ(t + j);
      const e = elev[k];
      let u = 0, v = 0;
      if (k === 'S') u = (x - (e?.x0 ?? bb.min.x)) / ((e?.x1 ?? bb.max.x) - (e?.x0 ?? bb.min.x));
      if (k === 'N') u = ((e?.x1 ?? bb.max.x) - x) / ((e?.x1 ?? bb.max.x) - (e?.x0 ?? bb.min.x));
      if (k === 'E') u = ((e?.z1 ?? bb.max.z) - z) / ((e?.z1 ?? bb.max.z) - (e?.z0 ?? bb.min.z));
      if (k === 'W') u = (z - (e?.z0 ?? bb.min.z)) / ((e?.z1 ?? bb.max.z) - (e?.z0 ?? bb.min.z));
      if (k === 'top') { u = x / 40; v = z / 40; } else v = (y - (e?.y0 ?? 0)) / ((e?.y1 ?? bb.max.y) - (e?.y0 ?? 0));
      uv[(t + j) * 2] = u; uv[(t + j) * 2 + 1] = v;
    }
    if (!cur || cur.k !== k) { cur = { k, start: t, count: 0 }; groups.push(cur); }
    cur.count += 3;
  }
  g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  const keys = ['S', 'N', 'E', 'W', 'top'];
  g.clearGroups(); for (const gr of groups) g.addGroup(gr.start, gr.count, keys.indexOf(gr.k));
  return [g, keys.map(matFor)];
}
function tag(o, phase, alt, extra = {}) { o.traverse((m) => { if (m.isMesh) { m.userData.phase = phase || null; m.userData.alt = alt || null; Object.assign(m.userData, extra); m.castShadow = m.receiveShadow = true; } }); return o; }

async function buildMassing(M) {
  // first pass for the bounding box the skins project against
  const bb = new THREE.Box3();
  for (const v of M.volumes) for (const [x, y] of v.footprint) { bb.expandByPoint(new THREE.Vector3(x, v.base || 0, -y)); bb.expandByPoint(new THREE.Vector3(x, v.roof?.ridge ?? v.top, -y)); }
  const elevTex = {};
  for (const [k, e] of Object.entries(M.elevations || {})) {
    const t = await textures.loadAsync(e.src); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; elevTex[k] = { ...e, tex: t };
  }
  for (const v of M.volumes) {
    const g = new THREE.Group(); g.name = v.name || '';
    const wallMat = (k) => {
      const e = elevTex[k];
      if (k === 'top') return mat(v.roofMaterial || 'roof');
      if (e && v.skin !== false) return mat(v.material || 'paper', { map: e.tex, color: e.tint || '#ffffff' });
      return mat(v.material || 'paper');
    };
    const [wg, mats] = skinFaces(extrude(v.footprint, v.base || 0, v.top), elevTex, bb, wallMat);
    g.add(new THREE.Mesh(wg, mats));
    const rg = roofGeom(v);
    if (rg) { const [rg2, rm] = skinFaces(rg, elevTex, bb, wallMat); g.add(new THREE.Mesh(rg2, rm.map((m) => { const c = m.clone(); c.side = THREE.DoubleSide; return c; }))); }
    // flat roof edge: a thin coping so the box reads as built, not extruded
    if (!rg && v.coping !== false) {
      const cg = extrude(v.footprint, v.top, v.top + 0.35); g.add(new THREE.Mesh(cg, mat(v.copingMaterial || 'steel')));
    }
    model.add(tag(g, v.phase, v.alt, { label: v.name }));
  }
  // windows when there is no elevation skin: dark glass set just proud of the wall
  for (const w of M.windows || []) {
    const v = M.volumes.find((x) => x.name === w.volume); if (!v) continue;
    const xs = v.footprint.map((p) => p[0]), ys = v.footprint.map((p) => p[1]);
    const box = new THREE.Box3(new THREE.Vector3(Math.min(...xs), 0, -Math.max(...ys)), new THREE.Vector3(Math.max(...xs), 0, -Math.min(...ys)));
    const [a, b] = w.along, [c, d] = w.height, t = 0.4;
    let geo, p;
    if (w.face === 'S' || w.face === 'N') { geo = new THREE.BoxGeometry(b - a, d - c, t); p = [(a + b) / 2, (c + d) / 2, w.face === 'S' ? box.max.z + t / 2 : box.min.z - t / 2]; }
    else { geo = new THREE.BoxGeometry(t, d - c, b - a); p = [w.face === 'E' ? box.max.x + t / 2 : box.min.x - t / 2, (c + d) / 2, -(a + b) / 2]; }
    const m = new THREE.Mesh(geo, mat('glass')); m.position.set(...p); model.add(tag(m, v.phase, v.alt));
  }
  // paving, lawn, water: flat shapes on the ground
  for (const f of M.flats || []) {
    const g = new THREE.ShapeGeometry(polyShape(f.polygon)); g.rotateX(-Math.PI / 2); g.translate(0, f.y ?? 0.05, 0);
    const m = new THREE.Mesh(g, mat(f.material || 'paving')); m.receiveShadow = true; m.userData.phase = f.phase || null; m.userData.alt = f.alt || null; m.userData.context = true; model.add(m);
  }
  // trees: faceted, so they sit with the paper model instead of pretending to be real
  for (const [x, y, r = 12, h = r * 2.6] of M.trees || []) {
    const t = new THREE.Group();
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(r * 0.06, r * 0.08, h * 0.35, 6), mat('#8b7d6b')); trunk.position.y = h * 0.175;
    const crown = new THREE.Mesh(new THREE.IcosahedronGeometry(r, 0), mat('#b9b9a1', { flatShading: true })); crown.position.y = h * 0.62; crown.scale.y = 1.15;
    t.add(trunk, crown); t.position.set(x, 0, -y); model.add(tag(t, M.treePhase || null, null, { context: true }));
  }
}

async function buildGLB(src) {
  const gltf = await new GLTFLoader().loadAsync(src);
  const root = gltf.scene;
  if (CFG.scale) root.scale.setScalar(CFG.scale);
  if (CFG.rotateY) root.rotation.y = THREE.MathUtils.degToRad(CFG.rotateY);
  // phase and alternate tags come from node names: 'Roof Deck [phase:house] [alt:5]', or from
  // the name patterns in project.json (model.phaseNodes / model.altNodes)
  const pat = (obj, map) => { if (!map) return null; for (const [k, list] of Object.entries(map)) for (const s of list) { const re = new RegExp('^' + s.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*') + '$', 'i'); for (let o = obj; o; o = o.parent) if (re.test(o.name)) return k; } return null; };
  root.traverse((m) => {
    if (!m.isMesh) return;
    let ph = null, alt = null;
    for (let o = m; o; o = o.parent) { const a = /\[phase:([^\]]+)\]/i.exec(o.name); const b = /\[alt:([^\]]+)\]/i.exec(o.name); ph = ph || a?.[1]; alt = alt || b?.[1]; }
    m.userData.phase = ph || pat(m, CFG.phaseNodes); m.userData.alt = alt || pat(m, CFG.altNodes);
    if (pat(m, CFG.contextNodes ? { c: CFG.contextNodes } : null) || /\[context\]/i.test(m.name)) m.userData.context = true;
    m.castShadow = m.receiveShadow = true;
    if (m.material) { const ms = Array.isArray(m.material) ? m.material : [m.material]; ms.forEach((x) => { if (x.map) x.map.anisotropy = 8; }); }
    // baked lighting (tools/render/bake.py): show the baked texture unlit; the mesh still casts its live shadow on the lawn
    if (CFG.baked && m.material && m.material.map) {
      const k = 1 / (CFG.bakeScale || 0.5), mm = new THREE.MeshBasicMaterial({ map: m.material.map, color: new THREE.Color(k, k, k), name: m.material.name });
      mm.userData.baked = true; m.material = mm; m.receiveShadow = false;
    }
  });
  // sit it on the ground, centered
  const bb = new THREE.Box3().setFromObject(root), c = bb.getCenter(new THREE.Vector3());
  root.position.x -= c.x; root.position.z -= c.z; root.position.y -= bb.min.y;
  model.add(root); model.updateMatrixWorld(true);   // so the views are computed from where the model now sits
}

// ============================================================ landscape: lawn and tree line
function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
function lawnMat(S) {
  const c = document.createElement('canvas'); c.width = c.height = 512; const x = c.getContext('2d'), R = rng(7);
  x.fillStyle = '#6f7d4a'; x.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 26000; i++) { const g = 90 + R() * 70, r = g * (0.62 + R() * 0.14), b = g * (0.38 + R() * 0.1); x.fillStyle = `rgba(${r|0},${g|0},${b|0},${0.25 + R() * 0.35})`; x.fillRect(R() * 512, R() * 512, 1 + R() * 2, 2 + R() * 5); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(S * 12 / 9, S * 12 / 9); t.anisotropy = 8;
  return new THREE.MeshStandardMaterial({ map: t, color: '#c9ccb0', roughness: 1 });
}
// a painted tree line on a ring: mixed conifers and hardwoods in silhouette, softened by the fog
function treeRing(C, radius, height, seed, haze, dabs = true) {
  // painted crown by crown: a dark mass, then hundreds of leaf dabs lit from the sun side
  const W = 4096, H = 768, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const x = cv.getContext('2d'), R = rng(seed);
  const hsl = (h, s, l) => `hsl(${h.toFixed(0)}, ${s.toFixed(0)}%, ${l.toFixed(1)}%)`;
  const hz = (l) => l + haze * 22, hs = (sat) => sat * (1 - haze * 0.55);
  const crown = (cx, hgt, conifer, depth) => {
    const base = H, hue = conifer ? 112 + R() * 22 : 80 + R() * 28, sat = conifer ? 22 + R() * 10 : 26 + R() * 14;
    const dark = (conifer ? 8 : 10) + depth * 3.5, lit = (conifer ? 17 : 23) + depth * 3.5;
    const pts = [];   // dab centres inside the crown outline
    if (conifer) {
      const w = hgt * (0.17 + R() * 0.08), top = base - hgt;
      x.fillStyle = hsl(hue, hs(sat), hz(dark)); x.beginPath(); x.moveTo(cx, top);
      for (let t = 0; t <= 1.0001; t += 0.06) x.lineTo(cx + w * t * (0.8 + R() * 0.45), top + hgt * t);
      for (let t = 1; t >= 0; t -= 0.06) x.lineTo(cx - w * t * (0.8 + R() * 0.45), top + hgt * t);
      x.closePath(); x.fill();
      for (let i = 0; i < 220; i++) { const t = Math.pow(R(), 0.8), side = R() * 2 - 1; pts.push([cx + side * w * t * 0.95, top + hgt * t, side, t]); }
    } else {
      const w = hgt * (0.32 + R() * 0.18), cy = base - hgt * 0.62;
      x.fillStyle = hsl(hue, hs(sat), hz(dark));
      for (let j = 0; j < 12; j++) { const r = w * (0.3 + R() * 0.28), px = cx + (R() - 0.5) * w * 1.3, py = cy + (R() - 0.6) * hgt * 0.55; x.beginPath(); x.arc(px, py, r, 0, 6.283); x.fill(); pts.push([px, py, (px - cx) / w, 0.5, r]); }
      x.fillRect(cx - w * 0.55, cy, w * 1.1, base - cy);
      for (let i = 0; i < 420; i++) { const a = R() * 6.283, d = Math.sqrt(R()) * w * 0.62; pts.push([cx + Math.cos(a) * d, cy + Math.sin(a) * d * 0.85 - hgt * 0.05, Math.cos(a), (Math.sin(a) + 1) / 2]); }
    }
    if (dabs) for (const [px, py, side, t] of pts) {
      const light = -side * 0.5 + (1 - t) * 0.6 + R() * 0.4;   // sun from the left and above
      const l = dark + (lit - dark) * Math.max(0, Math.min(1, light));
      x.fillStyle = hsl(hue + (R() - 0.5) * 10, hs(sat + R() * 8), hz(l)); x.globalAlpha = 0.55 + R() * 0.4;
      const r = hgt * (conifer ? 0.008 + R() * 0.012 : 0.01 + R() * 0.016);
      x.beginPath(); x.ellipse(px, py, r * (conifer ? 1.8 : 1.2), r, (R() - 0.5) * 0.6, 0, 6.283); x.fill();
    }
    x.globalAlpha = 1;
    if (!conifer && R() < 0.6) { x.strokeStyle = hsl(30, 12, hz(14)); x.lineWidth = hgt * 0.012; x.beginPath(); x.moveTo(cx, base); x.lineTo(cx + (R() - 0.5) * 8, base - hgt * 0.42); x.stroke(); }
  };
  for (let layer = 0; layer < 3; layer++) {
    const n = 150 + layer * 40;
    for (let i = 0; i < n; i++) { const conifer = R() < 0.4; crown(R() * W, H * (0.42 + R() * 0.5) * (1 - layer * 0.1), conifer, layer); }
  }
  // understory: the bottom of the tree line falls into shade
  x.globalCompositeOperation = 'source-atop';
  const ug = x.createLinearGradient(0, H * 0.7, 0, H); ug.addColorStop(0, 'rgba(8,14,6,0)'); ug.addColorStop(1, 'rgba(8,14,6,0.55)'); x.fillStyle = ug; x.fillRect(0, 0, W, H);
  x.globalCompositeOperation = 'source-over';
  // soften like a background out of focus
  const cv2 = document.createElement('canvas'); cv2.width = W; cv2.height = H; const x2 = cv2.getContext('2d');
  x2.filter = `blur(${(1.6 + haze * 2).toFixed(1)}px)`; x2.drawImage(cv, 0, 0);
  const t = new THREE.CanvasTexture(cv2); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = THREE.RepeatWrapping; t.repeat.x = 3; t.anisotropy = 8;
  const m = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, 128, 1, true), new THREE.MeshBasicMaterial({ map: t, transparent: true, side: THREE.DoubleSide, depthWrite: false }));
  m.renderOrder = -0.5;
  m.position.set(C.x, BB.min.y + height / 2 - 0.5, C.z); m.userData.context = true;
  return m;
}
// trees rendered in Cycles (tools/render/trees.py), standing as billboards that turn to the camera
const BILL = [];
function impostors(C, S, list) {
  const R = rng(1984), g = new THREE.Group(); g.userData.context = true;
  const mats = list.map((t) => { const tx = textures.load(t.src); tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = 8; return new THREE.MeshBasicMaterial({ map: tx, alphaTest: 0.5, side: THREE.DoubleSide, color: new THREE.Color(0.92, 0.92, 0.92) }); });
  const R0 = Math.max(BB.max.x - BB.min.x, BB.max.z - BB.min.z) * 0.5, n = CFG.treeCount ?? 90;
  for (let i = 0; i < n; i++) {
    const ang = R() * Math.PI * 2, dir = new THREE.Vector3(Math.sin(ang), 0, Math.cos(ang)), facing = dir.dot(FRONT);
    const dist = R0 + S * (facing > 0.3 ? 3.4 + R() * 1.6 : 2.9 + R() * 1.8);
    const k = (R() * list.length) | 0, t = list[k], h = 48 + R() * 34, w = h * t.w / t.h;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h).translate(0, h / 2 - 0.5, 0), mats[k]);
    m.position.set(C.x + dir.x * dist, BB.min.y, C.z + dir.z * dist); m.userData.context = true;
    g.add(m); BILL.push(m);
  }
  return g;
}
function faceBillboards() { for (const m of BILL) m.rotation.y = Math.atan2(camera.position.x - m.position.x, camera.position.z - m.position.z); }
function treeLine(C, S, BB) {
  // trees are kept out of a wedge in front of the building and out of the camera paths
  const R = rng(1984), fol = [], trk = [], col = [];
  const jitter = (g, a) => { const p = g.attributes.position; for (let i = 0; i < p.count; i++) p.setXYZ(i, p.getX(i) * (1 + (R() - 0.5) * a), p.getY(i) * (1 + (R() - 0.5) * a * 0.6), p.getZ(i) * (1 + (R() - 0.5) * a)); return g; };
  const tint = (g, c) => { const n = g.attributes.position.count, a = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const k = 0.85 + R() * 0.25; a[i * 3] = c.r * k; a[i * 3 + 1] = c.g * k; a[i * 3 + 2] = c.b * k; } g.setAttribute('color', new THREE.BufferAttribute(a, 3)); return g; };
  const R0 = Math.max(BB.max.x - BB.min.x, BB.max.z - BB.min.z) * 0.5;
  const front = FRONT.clone();
  for (let i = 0; i < 150; i++) {
    const ang = R() * Math.PI * 2, dir = new THREE.Vector3(Math.sin(ang), 0, Math.cos(ang));
    const facing = dir.dot(front), dist = R0 + S * (facing > 0.2 ? 1.6 + R() * 1.6 : 0.55 + R() * 1.4);
    const x = C.x + dir.x * dist, z = C.z + dir.z * dist;
    const conifer = R() < 0.45, h = (conifer ? 38 : 34) + R() * 26, lean = (R() - 0.5) * 0.06;
    const m = new THREE.Matrix4().makeRotationY(R() * 6.28).premultiply(new THREE.Matrix4().makeRotationZ(lean)).setPosition(x, BB.min.y, z);
    trk.push(new THREE.CylinderGeometry(h * 0.012, h * 0.022, h * (conifer ? 0.5 : 0.55), 6).translate(0, h * 0.25, 0).applyMatrix4(m));
    const base = conifer ? new THREE.Color().setHSL(0.31 + R() * 0.05, 0.32 + R() * 0.1, 0.16 + R() * 0.06) : new THREE.Color().setHSL(0.2 + R() * 0.07, 0.38 + R() * 0.15, 0.26 + R() * 0.1);
    if (conifer) {
      for (let k = 0; k < 6; k++) { const y = h * (0.2 + k * 0.13), r = h * (0.2 - k * 0.028); fol.push(tint(jitter(new THREE.ConeGeometry(r, h * 0.3, 9, 2), 0.35).translate(0, y + h * 0.15, 0), base).applyMatrix4(m)); }
    } else {
      const n = 9 + (R() * 6) | 0, cw = h * 0.3;
      for (let k = 0; k < n; k++) { const r = cw * (0.45 + R() * 0.35), y = h * (0.5 + R() * 0.38), a = R() * 6.28, d = cw * 0.65 * R(); fol.push(tint(jitter(new THREE.IcosahedronGeometry(r, 1), 0.4).translate(Math.cos(a) * d, y, Math.sin(a) * d), base).applyMatrix4(m)); }
    }
  }
  const g = new THREE.Group();
  const merge = (list) => { let n = 0; list.forEach((x) => (n += x.toNonIndexed().attributes.position.count)); const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), co = new Float32Array(n * 3); let o = 0; for (const x0 of list) { const x = x0.toNonIndexed(); x.computeVertexNormals(); pos.set(x.attributes.position.array, o * 3); nor.set(x.attributes.normal.array, o * 3); if (x.attributes.color) co.set(x.attributes.color.array, o * 3); else co.fill(1, o * 3, (o + x.attributes.position.count) * 3); o += x.attributes.position.count; } const b = new THREE.BufferGeometry(); b.setAttribute('position', new THREE.BufferAttribute(pos, 3)); b.setAttribute('normal', new THREE.BufferAttribute(nor, 3)); b.setAttribute('color', new THREE.BufferAttribute(co, 3)); return b; };
  const f = new THREE.Mesh(merge(fol), new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, flatShading: false }));
  const t = new THREE.Mesh(merge(trk), new THREE.MeshStandardMaterial({ color: '#4a3d33', roughness: 1 }));
  f.castShadow = t.castShadow = true; f.receiveShadow = true; g.add(f, t); g.userData.context = true;
  return g;
}

// ============================================================ views, from the bounding box
let BB, C, S, FRONT, RIGHT, GROUND;
function frame3() {
  BB = new THREE.Box3();
  model.traverse((m) => { if (m.isMesh && !m.userData.alt && !m.userData.ground && !m.userData.context) BB.expandByObject(m); });
  if (BB.isEmpty()) BB.setFromObject(model);
  C = BB.getCenter(new THREE.Vector3()); C.y = BB.min.y + (BB.max.y - BB.min.y) * 0.42;
  const sz = BB.getSize(new THREE.Vector3()); S = Math.max(sz.x, sz.z, sz.y * 1.6);
  const fd = THREE.MathUtils.degToRad(CFG.front_deg ?? 0);   // 0 = the front faces south (+z)
  FRONT = new THREE.Vector3(Math.sin(fd), 0, Math.cos(fd)); RIGHT = new THREE.Vector3().crossVectors(new THREE.Vector3(0, 1, 0), FRONT).negate();
  // ground and shadow camera sized to the project
  const ground = GROUND = new THREE.Mesh(new THREE.CircleGeometry(S * (LAND ? 12 : 6), 64), LAND ? lawnMat(S) : new THREE.MeshStandardMaterial({ color: '#ece8e1', roughness: 1 }));
  ground.rotation.x = -Math.PI / 2; ground.position.y = BB.min.y - 0.02; ground.receiveShadow = true; ground.userData.ground = true; scene.add(ground);
  const sc = sun.shadow.camera, r = S * (LAND ? 1.6 : 1.1); sc.left = -r; sc.right = r; sc.top = r; sc.bottom = -r; sc.near = 1; sc.far = S * 8; sc.updateProjectionMatrix();
  sun.position.copy(C).add((LAND ? new THREE.Vector3(-0.62, 0.52, 0.6) : new THREE.Vector3(-0.5, 0.62, 0.66)).normalize().multiplyScalar(S * 3)); sun.target.position.copy(C);
  if (LAND) {
    DOME.scale.setScalar(S * 30); DOME.position.copy(C);
    scene.fog = new THREE.Fog(SKY.hor.clone(), S * 3.5, S * 13);
    if (CFG.treeImpostors && CFG.treeImpostors.length) scene.add(impostors(C, S, CFG.treeImpostors));
    else if (CFG.trees === true) { scene.add(treeRing(C, S * 4.6, S * 0.5, 11, 0.15, false)); scene.add(treeRing(C, S * 6.5, S * 0.55, 23, 0.45, false)); }
  } else scene.fog = new THREE.Fog(BONE.clone(), S * 4, S * 9);
}
// a view: [distance in model sizes, azimuth from the front (deg, + to the right), elevation (deg), fov, look height]
const PRESET = {
  hero: [1.55, 28, 9, 34, 0.35], front: [1.7, 0, 6, 32, 0.4], rear: [1.7, 180, 10, 32, 0.4],
  left: [1.7, -90, 8, 32, 0.4], right: [1.7, 90, 8, 32, 0.4], aerial: [1.85, 38, 34, 32, 0.2],
  'aerial-rear': [1.85, 215, 34, 32, 0.2], top: [2.3, 10, 78, 32, 0], low: [1.25, -24, 4, 38, 0.5],
  'corner-left': [1.55, -42, 16, 32, 0.35], 'corner-right': [1.55, 48, 16, 32, 0.35], detail: [0.9, 30, 12, 36, 0.45],
};
function pose(v, drift) {
  if (v && typeof v === 'object' && v.pos) return [new THREE.Vector3(...v.pos), new THREE.Vector3(...v.look), v.fov || 32];
  const [d, az, el, fov, lh] = PRESET[v] || PRESET.hero;
  const a = THREE.MathUtils.degToRad(az + drift * 7), e = THREE.MathUtils.degToRad(el);
  const dir = FRONT.clone().multiplyScalar(Math.cos(a)).addScaledVector(RIGHT, Math.sin(a)).multiplyScalar(Math.cos(e)).add(new THREE.Vector3(0, Math.sin(e), 0));
  const dist = d * S * (1 - drift * 0.06) / Math.tan(THREE.MathUtils.degToRad(fov) / 2) * (CFG.zoom ? 0.42 / CFG.zoom : 0.36);
  const look = C.clone(); look.y = BB.min.y + (BB.max.y - BB.min.y) * lh;
  return [look.clone().addScaledVector(dir, dist), look, fov];
}
let CAM = [];
function buildCams() {
  CAM = [];
  STOPS.forEach((s, i) => {
    const t0 = i === 0 ? 0 : s.s0 + 0.2 * s.len, t1 = i === STOPS.length - 1 ? 1 : s.s1 - 0.2 * s.len;
    const sx = s.type === 'schedule' ? 0.175 : s.side === 'r' ? -0.13 : s.type === 'hero' ? 0.12 : 0.13;
    const sy = s.type === 'schedule' ? -0.27 : s.type === 'hero' ? 0.3 : 0;
    const [p0, l0, f0] = pose(s.view, 0), [p1, l1, f1] = pose(s.view, 1);
    CAM.push([t0, p0, l0, sx, sy, f0], [t1, p1, l1, sx, sy, f1]);
  });
}
const _m = new THREE.Vector3(), _c = new THREE.Vector3();
function camAt(p) {
  let i = 0; while (i < CAM.length - 2 && p > CAM[i + 1][0]) i++;
  const k0 = CAM[i], k1 = CAM[i + 1], t = ease(clamp01((p - k0[0]) / (k1[0] - k0[0] || 1)));
  const pos = new THREE.Vector3();
  if (i % 2 === 1) {   // between stops the camera arcs around the model instead of cutting through it
    _m.copy(k0[1]).add(k1[1]).multiplyScalar(0.5);
    const want = Math.max(k0[1].distanceTo(C), k1[1].distanceTo(C));
    const dir = _m.clone().sub(C); if (dir.lengthSq() < 1) dir.set(0, 1, 0);
    _c.copy(C).add(dir.setLength(Math.max(want, _m.distanceTo(C)))).multiplyScalar(2).sub(_m);
    const u = 1 - t; pos.copy(k0[1]).multiplyScalar(u * u).addScaledVector(_c, 2 * u * t).addScaledVector(k1[1], t * t);
  } else pos.copy(k0[1]).lerp(k1[1], t);
  const L = (j) => k0[j] + (k1[j] - k0[j]) * t;
  return [pos, k0[2].clone().lerp(k1[2], t), L(3), L(4), L(5)];
}
function applyLens(sx, sy) {
  const w = innerWidth, h = innerHeight;
  if (NARROW()) camera.setViewOffset(w, h, 0, h * 0.2, w, h);
  else camera.setViewOffset(w, h, -sx * w, -sy * h, w, h);
}

// ============================================================ build state: phases, alternates, tint
// Each mesh gets its own clip plane per phase so a phase rises out of the ground as it is built.
const PH = {};
function prepPhases() {
  const box = {};
  model.traverse((m) => { if (!m.isMesh) return; const k = m.userData.phase || '_'; (box[k] ||= new THREE.Box3()).expandByObject(m); });
  for (const k in box) {
    const plane = new THREE.Plane(new THREE.Vector3(0, -1, 0), box[k].max.y + 1);
    PH[k] = { plane, y0: box[k].min.y - 0.5, y1: box[k].max.y + 0.5, f: 1, tint: 0, mats: [] };
  }
  const seen = new Map();
  model.traverse((m) => {
    if (!m.isMesh) return;
    const k = m.userData.phase || '_';
    const swap = (x) => { const key = x.uuid + k; if (!seen.has(key)) { const c = x.clone(); c.clippingPlanes = [PH[k].plane]; c.userData.base = c.color ? c.color.clone() : null; seen.set(key, c); PH[k].mats.push(c); } return seen.get(key); };
    m.material = Array.isArray(m.material) ? m.material.map(swap) : swap(m.material);
  });
}
const BLUE = new THREE.Color('#0028cc');
function phaseState(p) {
  // the stops say what the model looks like; between stops the state blends
  const st = (s, u) => {
    const out = {};
    for (const k in PH) out[k] = 1;
    if (s.type === 'schedule' && PAGE.schedTime) {
      const t = PAGE.schedTime(PAGE.schedU(p));
      for (const ph of D.phases || []) if (ph.sched && PH[ph.id]) out[ph.id] = PAGE.schedFrac(ph.sched, t);
    } else if (s.reveal) {
      const list = s.reveal, n = list.length, seq = PHASES.indexOf(list[0]);
      for (const k in PH) { const i = PHASES.indexOf(k); if (i >= 0 && seq >= 0 && i > PHASES.indexOf(list[n - 1])) out[k] = 0; }
      list.forEach((k, i) => { out[k] = clamp01(u * n * 1.12 - i); });
    } else if (s.show) {
      for (const k in PH) { const i = PHASES.indexOf(k); if (i >= 0 && i > PHASES.indexOf(s.show)) out[k] = 0; }
    }
    return out;
  };
  let i = 0; STOPS.forEach((s, k) => { if (p >= s.s0 - 1e-6) i = k; });
  const s = STOPS[i], u = clamp01((p - (s.a - 0.012)) / (s.b - s.a + 0.012));
  const here = st(s, u);
  // blend into the next stop's opening state across the gap
  const nx = STOPS[i + 1];
  if (nx && p > s.b) { const w = ease(clamp01((p - s.b) / (nx.a - s.b || 1))); const there = st(nx, 0); for (const k in here) here[k] += (there[k] - here[k]) * w; }
  const tint = {}; for (const k in PH) tint[k] = (s.tint || []).includes(k) ? clamp01(Math.min((p - s.a + 0.02) / 0.03, (s.b + 0.02 - p) / 0.03)) : 0;
  return [here, tint];
}
let lastState = '';
function applyPhases(p) {
  const [f, tint] = phaseState(p);
  const key = JSON.stringify([f, tint, [...(window.ALT_ON || [])]]);
  if (key === lastState) return; lastState = key;
  PARTIAL = false;
  for (const k in PH) {
    const P = PH[k], v = ease(clamp01(f[k]));
    if (v > 0.002 && v < 0.998) PARTIAL = true;   // the AO pass ignores clip planes, so it sits out a reveal
    P.plane.constant = v >= 0.999 ? P.y1 + 1000 : P.y0 + (P.y1 - P.y0) * v;
    if (Math.abs(P.tint - tint[k]) > 0.001) { P.tint = tint[k]; for (const m of P.mats) if (m.userData.base) m.color.copy(m.userData.base).lerp(BLUE, 0.55 * P.tint); }
  }
  const on = window.ALT_ON || new Set();
  model.traverse((m) => { if (m.isMesh && m.userData.alt) m.visible = on.has(String(m.userData.alt)); });
}
document.addEventListener('alts', () => { lastState = ''; wake(); });

// ============================================================ dusk: the last stops in blue hour
const DUSK_AT = STOPS.findIndex((s) => s.dusk);
function applyDusk(p) {
  const t = DUSK_AT < 0 ? 0 : ease(clamp01((p - (STOPS[DUSK_AT].s0 - STOPS[DUSK_AT].len * 0.3)) / (STOPS[DUSK_AT].len * 0.5)));
  if (LAND) {
    const u = DOME.material.uniforms; u.top.value.copy(SKY.top).lerp(SKYD.top, t); u.hor.value.copy(SKY.hor).lerp(SKYD.hor, t); u.low.value.copy(SKY.low).lerp(SKYD.low, t);
    scene.background.copy(u.hor.value); if (scene.fog) scene.fog.color.copy(u.hor.value);
    if (GROUND) GROUND.material.color.set('#c9ccb0').lerp(DUSKC, t * 0.7);
  } else {
    scene.background.copy(BONE).lerp(DUSKC, t); if (scene.fog) scene.fog.color.copy(scene.background);
    if (GROUND) GROUND.material.color.set('#ece8e1').lerp(DUSKC, t * 0.85);
  }
  for (const k in PH) for (const m of PH[k].mats) if (m.userData.baked && m.userData.base) m.color.copy(m.userData.base).multiplyScalar(1 - 0.6 * t).lerp(DUSKC, 0.25 * t);
  sun.intensity = SUN0 * (1 - 0.75 * t); hemi.intensity = HEMI0 * (1 - 0.5 * t); renderer.toneMappingExposure = (LAND ? 1.08 : 0.95) + 0.1 * t;
  ROOT.classList.toggle('dusk', t > 0.5);
}

// ============================================================ the loop
function resize() {
  renderer.setPixelRatio(DPR()); renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); readScroll();
  if (COMP) { COMP.setPixelRatio(DPR()); COMP.setSize(innerWidth, innerHeight); }
}
let sizeW = innerWidth, sizeH = innerHeight, rzT = 0;
addEventListener('resize', () => {
  wake();
  // phones resize as the address bar slides; reallocating the canvas each time stutters the scroll
  if (TOUCH && innerWidth === sizeW && Math.abs(innerHeight - sizeH) < 160) { readScroll(); return; }
  clearTimeout(rzT); rzT = setTimeout(() => { sizeW = innerWidth; sizeH = innerHeight; resize(); }, 150);
});
let lastP = -1, idleN = 0, wakeN = 0, lastT = performance.now(), first = true;
function wake() { wakeN = 40; }
window.__wake = wake;
['pointerdown', 'click', 'change', 'input', 'keydown'].forEach((e) => addEventListener(e, wake, { passive: true }));
const perf = { n: 0, sum: 0, stage: 0 };
function adapt(dt) {
  if (perf.stage > 2 || document.hidden) return;
  perf.n++; perf.sum += dt; if (perf.n < 90) return;
  const avg = perf.sum / perf.n; perf.n = perf.sum = 0;
  const slow = avg > (NARROW() ? 0.026 : 0.034);
  if (slow && COMP) { COMP = null; return; }   // first lever on a slow machine: drop the ambient occlusion
  if (slow && perf.stage === 0 && renderer.getPixelRatio() > 1) { renderer.setPixelRatio(1); perf.stage = 1; }
  else if (slow && perf.stage <= 1 && sun.castShadow) { sun.castShadow = false; perf.stage = 3; }
  else if (!slow) perf.stage = 3;
}
function frame(t) {
  const dt = Math.min(0.1, (t - lastT) / 1000); lastT = t;
  if (document.body.classList.contains('booked')) { requestAnimationFrame(frame); return; }
  pNow += (pTarget - pNow) * (REDUCED ? 1 : Math.min(1, dt * 4.5));
  if (Math.abs(pTarget - pNow) < 1e-5) pNow = pTarget;
  const moving = Math.abs(pNow - lastP) > 1e-6; lastP = pNow;
  if (moving || wakeN > 0) idleN = 0; else idleN++;
  if (wakeN > 0) wakeN--;
  // at rest, stop redrawing an unchanged picture: phones stay cool and the scroll stays smooth
  if (!(first || idleN < 45 || idleN % 20 === 0)) { requestAnimationFrame(frame); return; }
  let [pos, look, sx, sy, fov] = camAt(pNow);
  if (window.__pose) { pos = new THREE.Vector3(...window.__pose.pos); look = new THREE.Vector3(...window.__pose.look); fov = window.__pose.fov || 30; sx = sy = 0; }   // review renders
  const asp = innerWidth / innerHeight; if (asp < 1.25) pos.sub(look).multiplyScalar(Math.min(2.6, Math.pow(1.5 / asp, 0.8))).add(look);
  camera.position.copy(pos); if (camera.fov !== fov) { camera.fov = fov; camera.updateProjectionMatrix(); }
  applyLens(sx, sy); camera.lookAt(look); if (BILL.length) faceBillboards();
  applyPhases(pNow); applyDusk(pNow);
  const sheet = PAGE.renderStops(pNow);
  if (!sheet) { if (COMP && !PARTIAL) COMP.render(); else renderer.render(scene, camera); }
  if (first) { first = false; ROOT.classList.add('ready'); window.__done = true; } else if (moving) adapt(dt);
  requestAnimationFrame(frame);
}

// ============================================================ start
try {
  if (CFG.mode === 'glb') await buildGLB(CFG.src);
  else await buildMassing(CFG.massing);
} catch (e) { console.error('model failed', e); }
if (LAND && CFG.env) {   // a measured sky for the light and the reflections (Poly Haven, CC0)
  try { const tx = await new EXRLoader().loadAsync(CFG.env); tx.mapping = THREE.EquirectangularReflectionMapping; scene.environment = pmrem.fromEquirectangular(tx).texture; scene.environmentIntensity = CFG.envIntensity ?? 0.32; scene.environmentRotation.y = THREE.MathUtils.degToRad(CFG.envRotate ?? 200); } catch (e) { console.warn('env', e); }
}
frame3(); prepPhases(); buildCams(); setupAO();
window.__stops = STOPS.map((s) => ({ id: s.id, s0: s.s0, s1: s.s1, a: s.a, b: s.b }));
window.__model = { bb: BB, size: S }; window.__three = { scene, camera, renderer, PH };
requestAnimationFrame(frame);
