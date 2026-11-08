#!/usr/bin/env python3
"""One-time OpenStreetMap -> city-memory static street GeoJSON.
Derived data © OpenStreetMap contributors, ODbL 1.0.
"""
import collections
import json
import re
import sys
from pathlib import Path
import osmium
from shapely.geometry import LineString, Point

ROOT = Path(__file__).resolve().parents[1]
STREET_DATA = ROOT / "data" / "novosibirsk_streets.json"
TARGET = ROOT / "data" / "novosibirsk_geometry.geojson"

def normalize(s):
    s = str(s or "").casefold().replace("ё", "е").strip()
    s = re.sub(r"\bул\.(?=\s|$)", "улица", s)
    s = re.sub(r"\bпр[-.]?кт\b|\bпр-т\b", "проспект", s)
    s = re.sub(r"\bпер\.(?=\s|$)", "переулок", s)
    s = re.sub(r"\bпл\.(?=\s|$)", "площадь", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-zа-я0-9]+", " ", s).strip()
    words = s.split()
    kinds = {"улица","переулок","проезд","проспект","площадь","бульвар",
             "шоссе","набережная","аллея","тупик","тракт","мост","линия"}
    if len(words) > 1 and words[-1] in kinds:
        words = [words[-1]] + words[:-1]
    return " ".join(words)

def key(rec):
    return f"{rec['street']}|{float(rec['lat']):.6f}|{float(rec['lon']):.6f}"

def projected_line(coords):
    return LineString([(p[0] * 63700, p[1] * 111000) for p in coords])

class Collector(osmium.SimpleHandler):
    def __init__(self, needed):
        super().__init__()
        self.needed = needed
        self.by_name = collections.defaultdict(list)
        self.count = 0
    def way(self, w):
        if "highway" not in w.tags: return
        name = None
        for tag in ("name","name:ru","official_name","alt_name","loc_name","short_name"):
            if tag in w.tags and normalize(w.tags[tag]) in self.needed:
                name = normalize(w.tags[tag])
                break
        if not name: return
        try:
            coords = [[round(n.lon, 6), round(n.lat, 6)] for n in w.nodes if n.location.valid()]
            if len(coords) < 2 or len(coords) != len(w.nodes): return
            line = projected_line(coords)
            if line.length < .1: return
            self.by_name[name].append((int(w.id), coords, line))
            self.count += 1
        except (ValueError, RuntimeError):
            pass

def get_component(ways, point, max_dist=750):
    distances = [line.distance(point) for _, _, line in ways]
    seed = min(range(len(ways)), key=distances.__getitem__)
    if distances[seed] > max_dist:
        return [], round(distances[seed])
    chosen, current = {seed}, [seed]
    while current:
        i = current.pop()
        for j, (_, _, geom) in enumerate(ways):
            if j in chosen: continue
            if ways[i][2].distance(geom) <= 32:
                chosen.add(j)
                current.append(j)
    return [ways[i] for i in sorted(chosen)], round(distances[seed])

def main(source):
    records = json.loads(STREET_DATA.read_text(encoding="utf-8"))
    eligible = [r for r in records if r.get("street") and r.get("lat") is not None and r.get("lon") is not None]
    wanted = {normalize(r["street"]) for r in eligible}
    collector = Collector(wanted)
    collector.apply_file(str(source), locations=True)
    print(f"OSM matched-name segments: {collector.count}; names: {len(collector.by_name)}", flush=True)
    features, missed = [], collections.Counter()
    for rec in eligible:
        ways = collector.by_name.get(normalize(rec["street"]), [])
        if not ways:
            missed["name_not_in_osm"] += 1
            continue
        point = Point(float(rec["lon"]) * 63700, float(rec["lat"]) * 111000)
        component, distance = get_component(ways, point, max_dist=6000 if rec.get('named_after_person') else 750)
        if not component:
            missed["geometry_far_from_point"] += 1
            continue
        features.append({
            "type":"Feature",
            "properties":{"key":key(rec),"street":rec["street"],"osm_ways":len(component),"distance_m":distance},
            "geometry":{"type":"MultiLineString","coordinates":[coords for _, coords, _ in component]}
        })
    data = {
        "type":"FeatureCollection",
        "name":"Novosibirsk street centerlines",
        "attribution":"© OpenStreetMap contributors",
        "license":"ODbL 1.0",
        "note":"OSM road centerlines, not legal street boundaries",
        "features":features
    }
    TARGET.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    matched_keys = {f["properties"]["key"] for f in features}
    named = [r for r in eligible if r.get("named_after_person")]
    matched_named = sum(key(r) in matched_keys for r in named)
    print(f"Matched {len(features)}/{len(eligible)} overall and {matched_named}/{len(named)} memorial streets. Missed: {dict(missed)}. GeoJSON size: {TARGET.stat().st_size}", flush=True)
    if matched_named < 130 or len(features) < 500:
        raise RuntimeError("Matched geometry coverage too low; refusing to deploy")

if __name__ == "__main__":
    main(Path(sys.argv[1]))
