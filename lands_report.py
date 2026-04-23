"""Render a 2-color land collection HTML report from mtga_export CSV rows."""
import html

LAND_CYCLES: list[dict] = [
    {
        "name": "スローランド", "en": "Slow Lands",
        "mechanic": "他の土地を2つ以上コントロールしていない限りタップイン",
        "lands": [
            {"name": "Deserted Beach",     "jp": "さびれた浜",          "pair": "WU", "rel": "ally"},
            {"name": "Shipwreck Marsh",    "jp": "難破船の湿地",        "pair": "UB", "rel": "ally"},
            {"name": "Haunted Ridge",      "jp": "憑依された峰",        "pair": "BR", "rel": "ally"},
            {"name": "Rockfall Vale",      "jp": "落石の谷間",          "pair": "RG", "rel": "ally"},
            {"name": "Overgrown Farmland", "jp": "草茂る農地",          "pair": "GW", "rel": "ally"},
            {"name": "Shattered Sanctum",  "jp": "砕かれた聖域",        "pair": "WB", "rel": "enemy"},
            {"name": "Stormcarved Coast",  "jp": "嵐削りの海岸",        "pair": "UR", "rel": "enemy"},
            {"name": "Deathcap Glade",     "jp": "死天狗茸の林間地",    "pair": "BG", "rel": "enemy"},
            {"name": "Sundown Pass",       "jp": "日没の道",            "pair": "RW", "rel": "enemy"},
            {"name": "Dreamroot Cascade",  "jp": "夢根の滝",            "pair": "GU", "rel": "enemy"},
        ],
    },
    {
        "name": "ショックランド", "en": "Shock Lands",
        "mechanic": "2点のライフを支払ってアンタップインできる",
        "lands": [
            {"name": "Hallowed Fountain", "jp": "神聖なる泉",     "pair": "WU", "rel": "ally"},
            {"name": "Watery Grave",      "jp": "湿った墓",       "pair": "UB", "rel": "ally"},
            {"name": "Blood Crypt",       "jp": "血の墓所",       "pair": "BR", "rel": "ally"},
            {"name": "Stomping Ground",   "jp": "踏み鳴らされる地", "pair": "RG", "rel": "ally"},
            {"name": "Temple Garden",     "jp": "寺院の庭",       "pair": "GW", "rel": "ally"},
            {"name": "Godless Shrine",    "jp": "神無き祭殿",     "pair": "WB", "rel": "enemy"},
            {"name": "Steam Vents",       "jp": "蒸気孔",         "pair": "UR", "rel": "enemy"},
            {"name": "Overgrown Tomb",    "jp": "草むした墓",     "pair": "BG", "rel": "enemy"},
            {"name": "Sacred Foundry",    "jp": "聖なる鋳造所",   "pair": "RW", "rel": "enemy"},
            {"name": "Breeding Pool",     "jp": "繁殖池",         "pair": "GU", "rel": "enemy"},
        ],
    },
    {
        "name": "チェックランド", "en": "Check Lands",
        "mechanic": "対応する基本土地タイプをコントロールしていないとタップイン",
        "lands": [
            {"name": "Glacial Fortress",   "jp": "氷河の城砦",         "pair": "WU", "rel": "ally"},
            {"name": "Drowned Catacomb",   "jp": "水没した地下墓地",   "pair": "UB", "rel": "ally"},
            {"name": "Dragonskull Summit", "jp": "竜髑髏の山頂",       "pair": "BR", "rel": "ally"},
            {"name": "Rootbound Crag",     "jp": "根縛りの岩山",       "pair": "RG", "rel": "ally"},
            {"name": "Sunpetal Grove",     "jp": "陽花弁の木立ち",     "pair": "GW", "rel": "ally"},
            {"name": "Isolated Chapel",    "jp": "孤立した礼拝堂",     "pair": "WB", "rel": "enemy"},
            {"name": "Sulfur Falls",       "jp": "硫黄の滝",           "pair": "UR", "rel": "enemy"},
            {"name": "Woodland Cemetery",  "jp": "森林の墓地",         "pair": "BG", "rel": "enemy"},
            {"name": "Clifftop Retreat",   "jp": "断崖の避難所",       "pair": "RW", "rel": "enemy"},
            {"name": "Hinterland Harbor",  "jp": "内陸の湾港",         "pair": "GU", "rel": "enemy"},
        ],
    },
    {
        "name": "ファストランド", "en": "Fast Lands",
        "mechanic": "他の土地を2つ以下しかコントロールしていないとアンタップイン",
        "lands": [
            {"name": "Seachrome Coast",     "jp": "金属海の沿岸",  "pair": "WU", "rel": "ally"},
            {"name": "Darkslick Shores",    "jp": "闇滑りの岸",    "pair": "UB", "rel": "ally"},
            {"name": "Blackcleave Cliffs",  "jp": "黒割れの崖",    "pair": "BR", "rel": "ally"},
            {"name": "Copperline Gorge",    "jp": "銅線の地溝",    "pair": "RG", "rel": "ally"},
            {"name": "Razorverge Thicket",  "jp": "剃刀境の茂み",  "pair": "GW", "rel": "ally"},
            {"name": "Concealed Courtyard", "jp": "秘密の中庭",    "pair": "WB", "rel": "enemy"},
            {"name": "Spirebluff Canal",    "jp": "尖塔断の運河",  "pair": "UR", "rel": "enemy"},
            {"name": "Blooming Marsh",      "jp": "花盛りの湿地",  "pair": "BG", "rel": "enemy"},
            {"name": "Inspiring Vantage",   "jp": "感動的な眺望所", "pair": "RW", "rel": "enemy"},
            {"name": "Botanical Sanctum",   "jp": "植物の聖域",    "pair": "GU", "rel": "enemy"},
        ],
    },
    {
        "name": "ペインランド", "en": "Pain Lands",
        "mechanic": "無色か、1点のライフを失って有色マナを出せる",
        "lands": [
            {"name": "Adarkar Wastes",    "jp": "アダーカー荒原",   "pair": "WU", "rel": "ally"},
            {"name": "Underground River", "jp": "地底の大河",       "pair": "UB", "rel": "ally"},
            {"name": "Sulfurous Springs", "jp": "硫黄泉",           "pair": "BR", "rel": "ally"},
            {"name": "Karplusan Forest",  "jp": "カープルーザンの森", "pair": "RG", "rel": "ally"},
            {"name": "Brushland",         "jp": "低木林地",         "pair": "GW", "rel": "ally"},
            {"name": "Caves of Koilos",   "jp": "コイロスの洞窟",   "pair": "WB", "rel": "enemy"},
            {"name": "Shivan Reef",       "jp": "シヴの浅瀬",       "pair": "UR", "rel": "enemy"},
            {"name": "Llanowar Wastes",   "jp": "ラノワールの荒原", "pair": "BG", "rel": "enemy"},
            {"name": "Battlefield Forge", "jp": "戦場の鍛冶場",     "pair": "RW", "rel": "enemy"},
            {"name": "Yavimaya Coast",    "jp": "ヤヴィマヤの沿岸", "pair": "GU", "rel": "enemy"},
        ],
    },
    {
        "name": "パスウェイ", "en": "Pathways (MDFC)",
        "mechanic": "両面土地 — 片面はどちらかの色を出す土地",
        "lands": [
            {"name": "Hengegate Pathway",   "jp": "連門の小道",     "pair": "WU", "rel": "ally"},
            {"name": "Clearwater Pathway",  "jp": "清水の小道",     "pair": "UB", "rel": "ally"},
            {"name": "Blightstep Pathway",  "jp": "荒廃踏みの小道", "pair": "BR", "rel": "ally"},
            {"name": "Cragcrown Pathway",   "jp": "岩山被りの小道", "pair": "RG", "rel": "ally"},
            {"name": "Branchloft Pathway",  "jp": "枝重なる小道",   "pair": "GW", "rel": "ally"},
            {"name": "Brightclimb Pathway", "jp": "陽光昇りの小道", "pair": "WB", "rel": "enemy"},
            {"name": "Riverglide Pathway",  "jp": "河川滑りの小道", "pair": "UR", "rel": "enemy"},
            {"name": "Darkbore Pathway",    "jp": "闇孔の小道",     "pair": "BG", "rel": "enemy"},
            {"name": "Needleverge Pathway", "jp": "針縁の小道",     "pair": "RW", "rel": "enemy"},
            {"name": "Barkchannel Pathway", "jp": "樹皮路の小道",   "pair": "GU", "rel": "enemy"},
        ],
    },
    {
        "name": "サーベイランド", "en": "Surveil Lands",
        "mechanic": "ETBタップ＋諜報1",
        "lands": [
            {"name": "Meticulous Archive",   "jp": "行き届いた書庫",      "pair": "WU", "rel": "ally"},
            {"name": "Undercity Sewers",     "jp": "地底街の下水道",      "pair": "UB", "rel": "ally"},
            {"name": "Raucous Theater",      "jp": "大音声の劇場",        "pair": "BR", "rel": "ally"},
            {"name": "Commercial District",  "jp": "商業地区",            "pair": "RG", "rel": "ally"},
            {"name": "Lush Portico",         "jp": "草萌ゆる玄関",        "pair": "GW", "rel": "ally"},
            {"name": "Shadowy Backstreet",   "jp": "薄暗い裏通り",        "pair": "WB", "rel": "enemy"},
            {"name": "Thundering Falls",     "jp": "轟音の滝",            "pair": "UR", "rel": "enemy"},
            {"name": "Underground Mortuary", "jp": "地底の遺体安置所",    "pair": "BG", "rel": "enemy"},
            {"name": "Elegant Parlor",       "jp": "優雅な談話室",        "pair": "RW", "rel": "enemy"},
            {"name": "Hedge Maze",           "jp": "迷路庭園",            "pair": "GU", "rel": "enemy"},
        ],
    },
    {
        "name": "ヴァージランド", "en": "Verge Lands",
        "mechanic": "1色は常時、もう1色は対応基本土地タイプ持ちで出せる",
        "lands": [
            {"name": "Floodfarm Verge",  "jp": "フラッドファームの境界", "pair": "WU", "rel": "ally"},
            {"name": "Gloomlake Verge",  "jp": "グルームレイクの境界",   "pair": "UB", "rel": "ally"},
            {"name": "Blazemire Verge",  "jp": "ブレイズマイアの境界",   "pair": "BR", "rel": "ally"},
            {"name": "Thornspire Verge", "jp": "ソーンスパイアの境界",   "pair": "RG", "rel": "ally"},
            {"name": "Hushwood Verge",   "jp": "ハッシュウッドの境界",   "pair": "GW", "rel": "ally"},
            {"name": "Bleachbone Verge", "jp": "ブリーチボーンの境界",   "pair": "WB", "rel": "enemy"},
            {"name": "Riverpyre Verge",  "jp": "リバーパイアーの境界",   "pair": "UR", "rel": "enemy"},
            {"name": "Willowrush Verge", "jp": "ウィローラッシュの境界", "pair": "GU", "rel": "enemy"},
        ],
    },
    {
        "name": "スクライランド", "en": "Scry Lands / Temples",
        "mechanic": "ETBタップ＋占術1",
        "lands": [
            {"name": "Temple of Enlightenment", "jp": "啓蒙の神殿", "pair": "WU", "rel": "ally"},
            {"name": "Temple of Deceit",        "jp": "欺瞞の神殿", "pair": "UB", "rel": "ally"},
            {"name": "Temple of Malice",        "jp": "悪意の神殿", "pair": "BR", "rel": "ally"},
            {"name": "Temple of Abandon",       "jp": "奔放の神殿", "pair": "RG", "rel": "ally"},
            {"name": "Temple of Plenty",        "jp": "豊潤の神殿", "pair": "GW", "rel": "ally"},
            {"name": "Temple of Silence",       "jp": "静寂の神殿", "pair": "WB", "rel": "enemy"},
            {"name": "Temple of Epiphany",      "jp": "天啓の神殿", "pair": "UR", "rel": "enemy"},
            {"name": "Temple of Malady",        "jp": "疾病の神殿", "pair": "BG", "rel": "enemy"},
            {"name": "Temple of Triumph",       "jp": "凱旋の神殿", "pair": "RW", "rel": "enemy"},
            {"name": "Temple of Mystery",       "jp": "神秘の神殿", "pair": "GU", "rel": "enemy"},
        ],
    },
]

PAIR_ORDER = ["WU", "UB", "BR", "RG", "GW", "WB", "UR", "BG", "RW", "GU"]

_HTML_CSS = """@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;700&family=Noto+Serif+JP:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --bg: #0f1014;
  --panel: #1a1c22;
  --panel-2: #222530;
  --ink: #e8e4d8;
  --ink-dim: #9a9689;
  --ink-faint: #4a4740;
  --accent: #c8a25c;
  --ally: #5b9ea8;
  --enemy: #c07b5a;
  --good: #7aa86d;
  --warn: #d4a84b;
  --bad: #c07b5a;
  --line: #2a2d38;
  --W: #fbf6d6;
  --U: #6ab6e5;
  --B: #a69ba3;
  --R: #e87a56;
  --G: #6aa870;
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 0;
  background: var(--bg);
  background-image:
    radial-gradient(ellipse at top, rgba(200,162,92,0.06), transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(91,158,168,0.04), transparent 60%);
  color: var(--ink);
  font-family: 'Noto Serif JP', 'Cormorant Garamond', Georgia, serif;
  line-height: 1.5;
}
.container { max-width: 1150px; margin: 0 auto; padding: 32px 24px 80px; }
.eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.25em; color: var(--accent); text-transform: uppercase; margin-bottom: 8px; }
h1 { font-family: 'Noto Serif JP', serif; font-weight: 800; font-size: clamp(28px, 4vw, 40px); margin: 0 0 12px; letter-spacing: -0.01em; }
.subtitle { color: var(--ink-dim); font-size: 14px; max-width: 720px; margin-bottom: 28px; }
.top-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 40px; padding-bottom: 28px; border-bottom: 1px solid var(--line); }
.stat { background: var(--panel); border: 1px solid var(--line); padding: 14px 16px; border-radius: 2px; }
.stat-label { font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 0.2em; color: var(--ink-dim); text-transform: uppercase; margin-bottom: 6px; }
.stat-value { font-family: 'Cormorant Garamond', serif; font-size: 30px; font-weight: 500; color: var(--accent); line-height: 1; }
.stat-detail { font-size: 11px; color: var(--ink-dim); margin-top: 4px; }
.cycle { margin-top: 32px; background: var(--panel); border: 1px solid var(--line); border-radius: 2px; overflow: hidden; }
.cycle-header { padding: 16px 22px 12px; background: linear-gradient(180deg, var(--panel-2), var(--panel)); border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 12px; }
.cycle-name h2 { font-family: 'Noto Serif JP', serif; font-weight: 800; font-size: 20px; margin: 0; display: inline-block; margin-right: 12px; }
.cycle-name .en { font-family: 'Cormorant Garamond', serif; font-style: italic; color: var(--accent); font-size: 15px; }
.cycle-mechanic { font-size: 12px; color: var(--ink-dim); margin-top: 4px; }
.progress { display: flex; align-items: center; gap: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.progress-bar { width: 120px; height: 6px; background: var(--panel-2); border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--accent), #e0b770); }
.progress-num { color: var(--accent); font-weight: 600; }
.progress-max { color: var(--ink-dim); }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th { text-align: left; padding: 10px 14px; font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.15em; color: var(--ink-dim); text-transform: uppercase; font-weight: 500; border-bottom: 1px solid var(--line); background: var(--panel-2); }
td { padding: 10px 14px; border-bottom: 1px solid rgba(42,45,56,0.5); vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr.owned td { background: rgba(122,168,109,0.04); }
tr.empty td { opacity: 0.55; }
tr:hover td { background: rgba(200,162,92,0.05); }
.land-name { font-weight: 500; }
.land-name .jp { display: block; font-size: 11px; color: var(--ink-dim); font-weight: 400; margin-top: 1px; }
.mana-pair { display: inline-flex; gap: 3px; }
.mana { width: 20px; height: 20px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: #1a1a1a; border: 1px solid rgba(0,0,0,0.3); }
.mana.W { background: var(--W); }
.mana.U { background: var(--U); color: #0a2030; }
.mana.B { background: var(--B); }
.mana.R { background: var(--R); }
.mana.G { background: var(--G); }
.relation { font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; padding: 3px 7px; border-radius: 2px; display: inline-block; }
.relation.ally { color: var(--ally); border: 1px solid rgba(91,158,168,0.3); background: rgba(91,158,168,0.08); }
.relation.enemy { color: var(--enemy); border: 1px solid rgba(192,123,90,0.3); background: rgba(192,123,90,0.08); }
.set-breakdown { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--ink-dim); }
.set-breakdown .set-pill { display: inline-block; padding: 1px 6px; background: rgba(200,162,92,0.08); border: 1px solid rgba(200,162,92,0.15); border-radius: 2px; margin-right: 3px; color: var(--ink); }
.set-breakdown .set-pill .n { color: var(--accent); margin-left: 3px; font-weight: 600; }
.total-cell { font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 600; text-align: center; width: 80px; }
.total-cell.full { color: var(--good); }
.total-cell.some { color: var(--warn); }
.total-cell.none { color: var(--ink-faint); }
.breakdown-section { margin-top: 48px; padding-top: 32px; border-top: 1px solid var(--line); }
.breakdown-section h3 { font-family: 'Noto Serif JP', serif; font-weight: 800; font-size: 20px; margin: 0 0 20px; }
.pair-matrix { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; }
.pair-cell { background: var(--panel); border: 1px solid var(--line); padding: 14px 16px; border-radius: 2px; }
.pair-cell-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.pair-cell .count { font-family: 'JetBrains Mono', monospace; font-size: 20px; font-weight: 600; color: var(--accent); }
.pair-cell .count .max { color: var(--ink-faint); font-size: 12px; }
.pair-cell .label { font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 0.15em; color: var(--ink-dim); text-transform: uppercase; margin-bottom: 8px; }
.pair-cell .mini-bar { height: 4px; background: var(--panel-2); border-radius: 2px; overflow: hidden; margin-top: 6px; }
.pair-cell .mini-fill { height: 100%; background: var(--accent); }
"""


def _mana_pair_html(pair: str) -> str:
    return "".join(f'<span class="mana {c}">{c}</span>' for c in pair)


def _set_breakdown_html(sets: dict[str, int]) -> str:
    if not sets:
        return '<span style="color:var(--ink-faint)">—</span>'
    return "".join(
        f'<span class="set-pill">{html.escape(s)}<span class="n">×{n}</span></span>'
        for s, n in sets.items()
    )


def _total_cell_class(n: int) -> str:
    if n >= 4:
        return "full"
    if n > 0:
        return "some"
    return "none"


def render_lands_html(rows: list[dict]) -> str:
    wanted = {l["name"] for c in LAND_CYCLES for l in c["lands"]}
    counts: dict[str, dict[str, int]] = {}
    for r in rows:
        name = r.get("Name", "")
        if name in wanted:
            code = r.get("Set Code", "") or "?"
            n = int(r.get("Count", 0) or 0)
            if n <= 0:
                continue
            counts.setdefault(name, {})
            counts[name][code] = counts[name].get(code, 0) + n

    def total(n: str) -> int:
        return sum(counts.get(n, {}).values())

    all_lands = [l for c in LAND_CYCLES for l in c["lands"]]
    total_max = len(all_lands) * 4
    total_owned = sum(total(l["name"]) for l in all_lands)
    types_max = len(all_lands)
    types_owned = sum(1 for l in all_lands if total(l["name"]) > 0)
    ally_lands = [l for l in all_lands if l["rel"] == "ally"]
    enemy_lands = [l for l in all_lands if l["rel"] == "enemy"]
    ally_owned = sum(total(l["name"]) for l in ally_lands)
    ally_max = len(ally_lands) * 4
    enemy_owned = sum(total(l["name"]) for l in enemy_lands)
    enemy_max = len(enemy_lands) * 4

    total_pct = round(total_owned / total_max * 100) if total_max else 0
    types_pct = round(types_owned / types_max * 100) if types_max else 0
    ally_pct = round(ally_owned / ally_max * 100) if ally_max else 0
    enemy_pct = round(enemy_owned / enemy_max * 100) if enemy_max else 0

    top_stats = f"""<div class="top-stats">
  <div class="stat">
    <div class="stat-label">総所持枚数</div>
    <div class="stat-value">{total_owned}<span style="color:var(--ink-dim);font-size:16px"> / {total_max}</span></div>
    <div class="stat-detail">{total_pct}% 完成度（{types_max}種×4）</div>
  </div>
  <div class="stat">
    <div class="stat-label">所持している種類</div>
    <div class="stat-value">{types_owned}<span style="color:var(--ink-dim);font-size:16px"> / {types_max}</span></div>
    <div class="stat-detail">{types_pct}% カバー率</div>
  </div>
  <div class="stat">
    <div class="stat-label">友好色</div>
    <div class="stat-value" style="color:var(--ally)">{ally_owned}<span style="color:var(--ink-dim);font-size:16px"> / {ally_max}</span></div>
    <div class="stat-detail">{ally_pct}%</div>
  </div>
  <div class="stat">
    <div class="stat-label">対抗色</div>
    <div class="stat-value" style="color:var(--enemy)">{enemy_owned}<span style="color:var(--ink-dim);font-size:16px"> / {enemy_max}</span></div>
    <div class="stat-detail">{enemy_pct}%</div>
  </div>
</div>"""

    cycle_html_parts: list[str] = []
    for cycle in LAND_CYCLES:
        cycle_owned = sum(total(l["name"]) for l in cycle["lands"])
        cycle_max = len(cycle["lands"]) * 4
        pct = min(round(cycle_owned / cycle_max * 100), 100) if cycle_max else 0

        rows_html: list[str] = []
        for land in cycle["lands"]:
            t = total(land["name"])
            row_class = "owned" if t > 0 else "empty"
            rel_label = "友好" if land["rel"] == "ally" else "対抗"
            rows_html.append(f"""      <tr class="{row_class}">
        <td class="land-name">{html.escape(land["name"])}<span class="jp">{html.escape(land["jp"])}</span></td>
        <td><span class="mana-pair">{_mana_pair_html(land["pair"])}</span></td>
        <td><span class="relation {land["rel"]}">{rel_label}</span></td>
        <td class="set-breakdown">{_set_breakdown_html(counts.get(land["name"], {}))}</td>
        <td class="total-cell {_total_cell_class(t)}">{t}</td>
      </tr>""")

        cycle_html_parts.append(f"""<section class="cycle">
  <div class="cycle-header">
    <div>
      <div class="cycle-name">
        <h2>{html.escape(cycle["name"])}</h2>
        <span class="en">{html.escape(cycle["en"])}</span>
      </div>
      <div class="cycle-mechanic">{html.escape(cycle["mechanic"])}</div>
    </div>
    <div class="progress">
      <div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div>
      <span class="progress-num">{cycle_owned}</span>
      <span class="progress-max">/ {cycle_max}</span>
    </div>
  </div>
  <table>
    <thead>
      <tr>
        <th>カード名</th>
        <th style="width:100px">色</th>
        <th style="width:70px">関係</th>
        <th>セット内訳</th>
        <th style="width:80px;text-align:center">合計</th>
      </tr>
    </thead>
    <tbody>
{chr(10).join(rows_html)}
    </tbody>
  </table>
</section>""")

    pair_stats: dict[str, dict] = {p: {"owned": 0, "max": 0, "rel": "ally"} for p in PAIR_ORDER}
    for cycle in LAND_CYCLES:
        for land in cycle["lands"]:
            p = land["pair"]
            pair_stats[p]["owned"] += total(land["name"])
            pair_stats[p]["max"] += 4
            pair_stats[p]["rel"] = land["rel"]

    pair_cells: list[str] = []
    for p in PAIR_ORDER:
        st = pair_stats[p]
        pct = min(round(st["owned"] / st["max"] * 100), 100) if st["max"] else 0
        rel_label = "友好色" if st["rel"] == "ally" else "対抗色"
        pair_cells.append(f"""  <div class="pair-cell">
    <div class="pair-cell-head">
      <span class="mana-pair">{_mana_pair_html(p)}</span>
      <span class="count">{st["owned"]}<span class="max"> / {st["max"]}</span></span>
    </div>
    <div class="label">{p} · {rel_label}</div>
    <div class="mini-bar"><div class="mini-fill" style="width:{pct}%"></div></div>
  </div>""")

    pair_section = f"""<div class="breakdown-section">
  <h3>色ペア別 集計</h3>
  <div class="pair-matrix">
{chr(10).join(pair_cells)}
  </div>
</div>"""

    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>MTGA 2色土地コレクション集計</title>
<style>
{_HTML_CSS}</style>
</head>
<body>
<div class="container">
  <div class="eyebrow">MTGA / 2-color lands / collection report</div>
  <h1>2色土地コレクション集計</h1>
  <div class="subtitle">コレクションCSVから、主要な2色土地サイクルを抽出・集計した結果です。各カードはMTGAで最大4枚まで持てますが、複数セットからの印刷を合算しているため4枚を超える場合もあります（デッキ投入には4枚で十分）。</div>
{top_stats}
{chr(10).join(cycle_html_parts)}
{pair_section}
</div>
</body>
</html>
"""
