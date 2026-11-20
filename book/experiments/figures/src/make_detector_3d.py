"""Write the interactive 3D model of SLD (sld-detector-3d.html) from ``sld_geometry.py``.

The page is self-contained apart from three.js, which it loads from jsDelivr at a pinned
version. Each volume is a solid of revolution of its r–z outline (a polygonal prism for the
octagonal WIC and the 48-sided LAC barrel), mirrored to both sides of the interaction
point. The page reads the book's colour tokens from the page that embeds it, when it can,
and follows the book's light and dark schemes.
"""

from __future__ import annotations

import json
from pathlib import Path

from sld_geometry import (
    BEAM_PIPE_RADIUS,
    GROUPS,
    VOLUMES,
    VXD3_HALF_LENGTH,
    VXD3_LAYERS,
)
from svgkit import TOKENS

FIGURES_DIR = Path(__file__).resolve().parent.parent
OUT_PATH = FIGURES_DIR / "sld-detector-3d.html"

# three.js release used by the page, https://www.npmjs.com/package/three (r160, Dec 2023).
THREE_VERSION = "0.160.0"
# Dark-scheme values of the theme tokens, bookspine 0.3.0 book.css :root[data-theme="dark"].
DARK_TOKENS = {
    "paper": "#161513",
    "ink": "#e9e5dc",
    "ink-2": "#c3bdb1",
    "ink-3": "#8f8980",
    "rule": "#332f2a",
    "accent": "#d79184",
    "box-definition": "#7fb0d0",
    "box-example": "#8ebb86",
    "box-remark": "#c9b26a",
    "box-recipe": "#a899d6",
    "box-warning": "#e2905e",
}
# Face opacity per group: the outer shells faint, so that the inner detectors show through.
OPACITY = {
    "tracking": 0.5,
    "pid": 0.32,
    "calorimetry": 0.26,
    "magnet": 0.14,
    "muon": 0.1,
    "lum": 0.7,
    "beam": 0.5,
}
LADDER_WIDTH_CM = 1.6  # NIM A400 (1997) 287: CCDs of 80 x 16 mm^2
LADDER_CANT_DEG = {12: 10.0, 16: 9.0, 20: 9.0}  # NIM A400, Table 2

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SLD detector, 3D model</title>
<style>
  :root { --paper: #fbfaf7; --ink: #1d1b17; --ink-2: #4a463f; --ink-3: #7a756b; --rule: #ddd8cc; }
  html, body { margin: 0; height: 100%; background: var(--paper); color: var(--ink);
    font: 13px/1.4 "Source Sans 3", "Helvetica Neue", Arial, sans-serif; overflow: hidden; }
  #view { position: absolute; inset: 0; }
  #view canvas { display: block; width: 100%; height: 100%; }
  #panel { position: absolute; top: 8px; left: 8px; padding: 8px 10px; border: 1px solid var(--rule);
    border-radius: 4px; background: color-mix(in srgb, var(--paper) 88%, transparent); max-width: 52%; }
  #panel label { display: flex; align-items: center; gap: 6px; margin: 2px 0; cursor: pointer; }
  #panel .sw { width: 11px; height: 11px; border-radius: 2px; flex: none; }
  #panel button { margin-top: 6px; font: inherit; color: var(--ink); background: none;
    border: 1px solid var(--rule); border-radius: 3px; padding: 2px 8px; cursor: pointer; }
  #hint { position: absolute; bottom: 6px; right: 10px; color: var(--ink-3); font-size: 12px; }
  #fail { display: none; padding: 2em; color: var(--ink-2); }
</style>
<script type="importmap">
{"imports": {"three": "https://cdn.jsdelivr.net/npm/three@__THREE__/build/three.module.js",
             "three/addons/": "https://cdn.jsdelivr.net/npm/three@__THREE__/examples/jsm/"}}
</script>
</head>
<body>
<div id="view" role="img" aria-label="Interactive 3D model of the SLD detector"></div>
<div id="panel"></div>
<div id="hint">drag to rotate, right-drag to pan, scroll to zoom</div>
<div id="fail">This model needs WebGL, which this browser does not provide.</div>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const MODEL = __MODEL__;

const view = document.getElementById("view");
let gl;
try {
  gl = new THREE.WebGLRenderer({ antialias: true, alpha: true });
} catch (e) {
  document.getElementById("fail").style.display = "block";
  throw e;
}
gl.setPixelRatio(Math.min(window.devicePixelRatio, 2));
view.appendChild(gl.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 1, 10000);
const controls = new OrbitControls(camera, gl.domElement);
controls.enableDamping = true;
scene.add(new THREE.AmbientLight(0xffffff, 1.1));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(600, 900, 400);
scene.add(sun);

function resetView() {
  camera.position.set(-1900, 1150, 1650);
  controls.target.set(0, 0, 0);
  controls.update();
}

// Theme: the embedding page's tokens if it shares our origin, else the scheme preference.
function themeTokens() {
  let dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  try {
    const root = window.parent.document.documentElement;
    const attr = root.getAttribute("data-theme");
    if (attr === "dark" || attr === "light") dark = attr === "dark";
  } catch (e) { /* cross-origin parent: keep the media query */ }
  return dark ? MODEL.dark : MODEL.light;
}

const groups = {};
const materials = {};
let cutaway = true;

function lathePoints(outline, sides) {
  // outline: (z, r) polygon in cm, r an apothem for a polygonal volume; LatheGeometry wants
  // (vertex radius, y) with y along the axis.
  const toVertex = sides ? 1 / Math.cos(Math.PI / sides) : 1;
  const pts = outline.map(([z, r]) => new THREE.Vector2(Math.max(r * toVertex, 0.01), z));
  pts.push(pts[0].clone());
  return pts;
}

function addVolume(vol) {
  const fraction = cutaway ? 0.75 : 1;
  const segments = Math.round((vol.sides || 96) * fraction);
  const phiStart = (vol.sides ? Math.PI / vol.sides : 0) + Math.PI / 2;
  const phiLength = 2 * Math.PI * fraction;
  const outlines = [];
  if (vol.outline.some(([z]) => z <= 0.001)) {
    // A barrel volume from z = 0: reflect it to span both sides of the IP.
    outlines.push(vol.outline.concat(vol.outline.map(([z, r]) => [-z, r]).reverse()));
  } else {
    // An endcap volume: one copy on each side.
    outlines.push(vol.outline, vol.outline.map(([z, r]) => [-z, r]).reverse());
  }
  for (const outline of outlines) {
    const geo = new THREE.LatheGeometry(lathePoints(outline, vol.sides), segments, phiStart, phiLength);
    geo.rotateX(Math.PI / 2);  // lathe axis (y) onto the beam axis (z)
    const mesh = new THREE.Mesh(geo, materials[vol.group]);
    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 30), materials[vol.group + ":edge"]);
    groups[vol.group].add(mesh, edges);
  }
}

function addVxd3() {
  const g = groups["tracking"];
  for (const layer of MODEL.vxd3.layers) {
    const cant = THREE.MathUtils.degToRad(layer.cant);
    for (let k = 0; k < layer.ladders; k++) {
      const phi = 2 * Math.PI * k / layer.ladders;
      const box = new THREE.BoxGeometry(MODEL.vxd3.width, 0.2, 2 * MODEL.vxd3.half_length);
      const mesh = new THREE.Mesh(box, materials["tracking:solid"]);
      mesh.position.set(layer.radius * Math.cos(phi), layer.radius * Math.sin(phi), 0);
      mesh.rotation.z = phi + Math.PI / 2 + cant;
      g.add(mesh);
    }
  }
  const pipe = new THREE.CylinderGeometry(MODEL.vxd3.pipe, MODEL.vxd3.pipe, 700, 48, 1, true);
  pipe.rotateX(Math.PI / 2);
  groups["beam"].add(new THREE.Mesh(pipe, materials["beam"]));
}

function build() {
  for (const g of Object.values(groups)) scene.remove(g);
  for (const key of Object.keys(MODEL.groups)) {
    const visible = groups[key] ? groups[key].visible : true;
    groups[key] = new THREE.Group();
    groups[key].visible = visible;
    scene.add(groups[key]);
  }
  for (const vol of MODEL.volumes) addVolume(vol);
  addVxd3();
  const axis = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, -700), new THREE.Vector3(0, 0, 700)]);
  groups["beam"].add(new THREE.Line(axis, materials["axis"]));
}

function makeMaterials() {
  const t = themeTokens();
  for (const [key, g] of Object.entries(MODEL.groups)) {
    const c = new THREE.Color(t[g.token]);
    materials[key] = new THREE.MeshLambertMaterial({ color: c, transparent: true, opacity: MODEL.opacity[key],
      side: THREE.DoubleSide, depthWrite: false });
    materials[key + ":edge"] = new THREE.LineBasicMaterial({ color: c, transparent: true, opacity: 0.55 });
    materials[key + ":solid"] = new THREE.MeshLambertMaterial({ color: c });
  }
  materials["axis"] = new THREE.LineBasicMaterial({ color: new THREE.Color(t["ink-3"]) });
  document.documentElement.style.setProperty("--paper", t.paper);
  document.documentElement.style.setProperty("--ink", t.ink);
  document.documentElement.style.setProperty("--ink-2", t["ink-2"]);
  document.documentElement.style.setProperty("--ink-3", t["ink-3"]);
  document.documentElement.style.setProperty("--rule", t.rule);
}

function buildPanel() {
  const t = themeTokens();
  const panel = document.getElementById("panel");
  panel.innerHTML = "";
  for (const [key, g] of Object.entries(MODEL.groups)) {
    const label = document.createElement("label");
    const box = document.createElement("input");
    box.type = "checkbox";
    box.checked = groups[key] ? groups[key].visible : true;
    box.addEventListener("change", () => { groups[key].visible = box.checked; });
    const sw = document.createElement("span");
    sw.className = "sw";
    sw.style.background = t[g.token];
    label.append(box, sw, document.createTextNode(g.label));
    panel.appendChild(label);
  }
  const cut = document.createElement("label");
  const cutBox = document.createElement("input");
  cutBox.type = "checkbox";
  cutBox.checked = cutaway;
  cutBox.addEventListener("change", () => { cutaway = cutBox.checked; build(); });
  cut.append(cutBox, document.createTextNode("cut away one quarter"));
  panel.appendChild(cut);
  const reset = document.createElement("button");
  reset.textContent = "reset view";
  reset.addEventListener("click", resetView);
  panel.appendChild(reset);
}

function refreshTheme() {
  makeMaterials();
  build();
  buildPanel();
}

function resize() {
  const w = view.clientWidth, h = view.clientHeight;
  gl.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}

refreshTheme();
resetView();
resize();
window.addEventListener("resize", resize);
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", refreshTheme);
try {
  new MutationObserver(refreshTheme).observe(window.parent.document.documentElement,
    { attributes: true, attributeFilter: ["data-theme"] });
} catch (e) { /* cross-origin parent */ }
gl.setAnimationLoop(() => { controls.update(); gl.render(scene, camera); });
</script>
</body>
</html>
"""


def model() -> dict:
    return {
        "groups": {
            key: {"label": label, "token": token}
            for key, (label, token) in GROUPS.items()
        },
        "volumes": [
            {
                "key": v.key,
                "group": v.group,
                "outline": [list(p) for p in v.outline],
                "sides": v.sides,
            }
            for v in VOLUMES
        ],
        "vxd3": {
            "layers": [
                {"radius": r, "ladders": n, "cant": LADDER_CANT_DEG[n]}
                for r, n in VXD3_LAYERS
            ],
            "half_length": VXD3_HALF_LENGTH,
            "width": LADDER_WIDTH_CM,
            "pipe": BEAM_PIPE_RADIUS,
        },
        "opacity": OPACITY,
        "light": TOKENS,
        "dark": {**TOKENS, **DARK_TOKENS},
    }


def main() -> None:
    page = TEMPLATE.replace("__THREE__", THREE_VERSION).replace(
        "__MODEL__", json.dumps(model(), separators=(",", ":"), sort_keys=True)
    )
    OUT_PATH.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
