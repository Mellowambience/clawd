#!/usr/bin/env python3
"""
Generate a themed game asset + UI pack for Ghostline-style projects.

Usage:
  python3 scripts/generate_game_pack.py
  python3 scripts/generate_game_pack.py --out canvas/game_pack
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


THEME = {
    "name": "ghostline-mars",
    "palette": {
        "bg_0": "#13090b",
        "bg_1": "#2f111a",
        "bg_2": "#6f1f2a",
        "ink": "#f7e8d7",
        "muted": "#d9c5b3",
        "accent": "#f0533a",
        "accent_soft": "#ffc3a1",
        "line": "rgba(255, 222, 199, 0.28)",
        "good": "#7df5c3",
        "warn": "#ffd079",
        "bad": "#ff8a8a",
    },
}


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def svg_template(body: str) -> str:
    return dedent(
        f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="none">
          {body}
        </svg>
        """
    )


def hud_frame_svg() -> str:
    return dedent(
        """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 240" fill="none">
          <defs>
            <linearGradient id="frameGlow" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#f0533a" stop-opacity="0.55"/>
              <stop offset="100%" stop-color="#ffc3a1" stop-opacity="0.20"/>
            </linearGradient>
          </defs>
          <rect x="8" y="8" width="944" height="224" rx="24" fill="rgba(15,5,7,0.72)" stroke="url(#frameGlow)" stroke-width="3"/>
          <path d="M 32 30 L 140 30 M 32 210 L 140 210 M 820 30 L 928 30 M 820 210 L 928 210" stroke="#ffd7be" stroke-opacity="0.45" stroke-width="2"/>
        </svg>
        """
    )


def bar_fill_svg(kind: str) -> str:
    if kind == "hp":
        left, right = "#f7d19d", "#f0533a"
    else:
        left, right = "#a3f5d7", "#66c9e2"
    return dedent(
        f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 40" fill="none">
          <rect x="1" y="1" width="598" height="38" rx="18" fill="rgba(255,255,255,0.10)" stroke="rgba(255,255,255,0.20)" />
          <rect x="6" y="6" width="588" height="28" rx="14" fill="url(#grad)"/>
          <defs>
            <linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stop-color="{left}" />
              <stop offset="100%" stop-color="{right}" />
            </linearGradient>
          </defs>
        </svg>
        """
    )


def icon_svgs() -> dict[str, str]:
    return {
        "icon_attack.svg": svg_template(
            """
            <circle cx="128" cy="128" r="104" stroke="#ffc3a1" stroke-width="14" stroke-opacity="0.7"/>
            <path d="M128 40L150 112H222L165 156L186 220L128 178L70 220L91 156L34 112H106L128 40Z" fill="#f0533a"/>
            """
        ),
        "icon_heal.svg": svg_template(
            """
            <circle cx="128" cy="128" r="104" stroke="#7df5c3" stroke-width="14" stroke-opacity="0.7"/>
            <rect x="112" y="56" width="32" height="144" rx="10" fill="#7df5c3"/>
            <rect x="56" y="112" width="144" height="32" rx="10" fill="#7df5c3"/>
            """
        ),
        "icon_shield.svg": svg_template(
            """
            <path d="M128 28L214 62V122C214 173 180 214 128 228C76 214 42 173 42 122V62L128 28Z" fill="#66c9e2" fill-opacity="0.26" stroke="#a3f5d7" stroke-width="10"/>
            <path d="M128 62L184 84V126C184 160 163 188 128 201C93 188 72 160 72 126V84L128 62Z" fill="#a3f5d7" fill-opacity="0.45"/>
            """
        ),
        "icon_energy.svg": svg_template(
            """
            <circle cx="128" cy="128" r="96" fill="#66c9e2" fill-opacity="0.24" stroke="#a3f5d7" stroke-width="10"/>
            <path d="M146 32L90 138H132L110 224L170 116H128L146 32Z" fill="#a3f5d7"/>
            """
        ),
        "icon_swap.svg": svg_template(
            """
            <path d="M54 88H188L156 56" stroke="#ffc3a1" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M202 168H68L100 200" stroke="#f0533a" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>
            """
        ),
        "icon_sigil.svg": svg_template(
            """
            <circle cx="128" cy="128" r="100" stroke="#ffc3a1" stroke-width="8" stroke-opacity="0.65"/>
            <circle cx="128" cy="128" r="62" stroke="#f0533a" stroke-width="8" stroke-opacity="0.85"/>
            <path d="M128 52L170 128L128 204L86 128L128 52Z" stroke="#ffd079" stroke-width="8"/>
            <circle cx="128" cy="128" r="12" fill="#ffd079"/>
            """
        ),
    }


def background_svgs() -> dict[str, str]:
    return {
        "mars_haze.svg": dedent(
            """
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" fill="none">
              <defs>
                <radialGradient id="g1" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(220 180) rotate(21) scale(760 540)">
                  <stop stop-color="#ffc3a1" stop-opacity="0.42"/>
                  <stop offset="1" stop-color="#ffc3a1" stop-opacity="0"/>
                </radialGradient>
                <radialGradient id="g2" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(1520 150) rotate(-16) scale(650 540)">
                  <stop stop-color="#f0533a" stop-opacity="0.38"/>
                  <stop offset="1" stop-color="#f0533a" stop-opacity="0"/>
                </radialGradient>
                <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0" stop-color="#13090b"/>
                  <stop offset="0.55" stop-color="#2f111a"/>
                  <stop offset="1" stop-color="#6f1f2a"/>
                </linearGradient>
              </defs>
              <rect width="1920" height="1080" fill="url(#bg)"/>
              <rect width="1920" height="1080" fill="url(#g1)"/>
              <rect width="1920" height="1080" fill="url(#g2)"/>
              <g opacity="0.18" stroke="#ffd7be">
                <circle cx="330" cy="750" r="90"/>
                <circle cx="1600" cy="720" r="180"/>
                <circle cx="1040" cy="460" r="140"/>
              </g>
            </svg>
            """
        ),
        "signal_grid.svg": dedent(
            """
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1200" fill="none">
              <rect width="1200" height="1200" fill="#13090b"/>
              <g stroke="#ffc3a1" stroke-opacity="0.16">
                <path d="M0 150H1200M0 300H1200M0 450H1200M0 600H1200M0 750H1200M0 900H1200M0 1050H1200"/>
                <path d="M150 0V1200M300 0V1200M450 0V1200M600 0V1200M750 0V1200M900 0V1200M1050 0V1200"/>
              </g>
              <circle cx="600" cy="600" r="330" stroke="#f0533a" stroke-opacity="0.30" stroke-width="4"/>
              <circle cx="600" cy="600" r="210" stroke="#ffd079" stroke-opacity="0.30" stroke-width="4"/>
              <circle cx="600" cy="600" r="90" stroke="#a3f5d7" stroke-opacity="0.30" stroke-width="4"/>
            </svg>
            """
        ),
    }


def tokens_css() -> str:
    p = THEME["palette"]
    return dedent(
        f"""
        :root {{
          --gh-bg-0: {p["bg_0"]};
          --gh-bg-1: {p["bg_1"]};
          --gh-bg-2: {p["bg_2"]};
          --gh-ink: {p["ink"]};
          --gh-muted: {p["muted"]};
          --gh-accent: {p["accent"]};
          --gh-accent-soft: {p["accent_soft"]};
          --gh-line: {p["line"]};
          --gh-good: {p["good"]};
          --gh-warn: {p["warn"]};
          --gh-bad: {p["bad"]};
          --gh-radius-sm: 10px;
          --gh-radius-md: 14px;
          --gh-radius-lg: 18px;
          --gh-shadow: 0 18px 40px rgba(0, 0, 0, 0.38);
          --gh-font-ui: "Space Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
          --gh-font-display: "Cinzel", Georgia, serif;
        }}
        """
    )


def components_css() -> str:
    return dedent(
        """
        @import url("https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Space+Mono:wght@400;700&display=swap");
        @import url("./tokens.css");

        .gh-root {
          color: var(--gh-ink);
          font-family: var(--gh-font-ui);
          background:
            radial-gradient(circle at 16% 12%, rgba(255, 195, 161, 0.22), transparent 46%),
            radial-gradient(circle at 84% 8%, rgba(240, 83, 58, 0.25), transparent 42%),
            linear-gradient(135deg, var(--gh-bg-0), var(--gh-bg-1) 45%, var(--gh-bg-2));
        }

        .gh-panel {
          background: rgba(15, 5, 7, 0.72);
          border: 1px solid var(--gh-line);
          border-radius: var(--gh-radius-lg);
          box-shadow: var(--gh-shadow);
          backdrop-filter: blur(5px);
        }

        .gh-title {
          margin: 0;
          font-family: var(--gh-font-display);
          letter-spacing: 0.05em;
          color: #ffe7d5;
        }

        .gh-subtitle {
          color: var(--gh-muted);
          font-size: 0.92rem;
        }

        .gh-pill {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          border: 1px solid var(--gh-line);
          background: rgba(255, 255, 255, 0.04);
          border-radius: 999px;
          padding: 4px 10px;
          font-size: 0.76rem;
        }

        .gh-pill.good { color: var(--gh-good); }
        .gh-pill.warn { color: var(--gh-warn); }
        .gh-pill.bad { color: var(--gh-bad); }

        .gh-btn {
          border: 1px solid var(--gh-line);
          border-radius: 12px;
          background: linear-gradient(130deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.02));
          color: var(--gh-ink);
          padding: 10px 12px;
          font: inherit;
          cursor: pointer;
          transition: 180ms ease;
        }

        .gh-btn:hover {
          border-color: rgba(255, 195, 161, 0.75);
          transform: translateY(-1px);
          background: linear-gradient(130deg, rgba(240, 83, 58, 0.22), rgba(255, 255, 255, 0.04));
        }

        .gh-bars {
          display: grid;
          gap: 8px;
        }

        .gh-bar {
          height: 10px;
          background: rgba(255, 255, 255, 0.12);
          border: 1px solid rgba(255, 255, 255, 0.18);
          border-radius: 999px;
          overflow: hidden;
        }

        .gh-bar > span {
          display: block;
          height: 100%;
          width: 100%;
        }

        .gh-bar.hp > span { background: linear-gradient(90deg, #f7d19d, #f0533a); }
        .gh-bar.en > span { background: linear-gradient(90deg, #a3f5d7, #66c9e2); }
        """
    )


def hud_overlay_html() -> str:
    return dedent(
        """
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Ghostline HUD Overlay</title>
          <link rel="stylesheet" href="./components.css" />
          <style>
            html, body { margin: 0; min-height: 100%; }
            body {
              display: grid;
              place-items: center;
              padding: 24px;
              background: url("../assets/backgrounds/mars_haze.svg") center / cover no-repeat fixed;
            }
            .wrap {
              width: min(980px, 96vw);
              padding: 16px;
            }
            .hud {
              display: grid;
              gap: 14px;
              padding: 18px;
            }
            .row {
              display: flex;
              justify-content: space-between;
              align-items: center;
              gap: 12px;
              flex-wrap: wrap;
            }
            .moves {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 10px;
            }
            .move {
              display: grid;
              gap: 6px;
            }
            .move small {
              color: var(--gh-muted);
            }
            .icons {
              display: flex;
              gap: 10px;
              flex-wrap: wrap;
            }
            .icon {
              width: 42px;
              height: 42px;
              border: 1px solid var(--gh-line);
              border-radius: 10px;
              padding: 7px;
              background: rgba(255,255,255,0.04);
            }
            @media (max-width: 760px) {
              .moves { grid-template-columns: 1fr; }
            }
          </style>
        </head>
        <body class="gh-root">
          <main class="wrap gh-panel">
            <section class="hud">
              <div class="row">
                <div>
                  <h1 class="gh-title">AetherRose Combat HUD</h1>
                  <div class="gh-subtitle">Reference overlay generated by script. Wire these classes in your game scenes.</div>
                </div>
                <div class="icons">
                  <img class="icon" src="../assets/icons/icon_attack.svg" alt="attack" />
                  <img class="icon" src="../assets/icons/icon_heal.svg" alt="heal" />
                  <img class="icon" src="../assets/icons/icon_shield.svg" alt="shield" />
                  <img class="icon" src="../assets/icons/icon_energy.svg" alt="energy" />
                  <img class="icon" src="../assets/icons/icon_swap.svg" alt="swap" />
                  <img class="icon" src="../assets/icons/icon_sigil.svg" alt="sigil" />
                </div>
              </div>

              <div class="row">
                <span class="gh-pill good">Stable</span>
                <span class="gh-pill">Shield 12</span>
                <span class="gh-pill warn">Energy 3/5</span>
                <span class="gh-pill bad">Threat: Champion Burst</span>
              </div>

              <div class="gh-bars">
                <div class="gh-subtitle">Health</div>
                <div class="gh-bar hp"><span style="width:72%"></span></div>
                <div class="gh-subtitle">Energy</div>
                <div class="gh-bar en"><span style="width:60%"></span></div>
              </div>

              <div class="moves">
                <button class="gh-btn move">
                  <strong>Rose Flare</strong>
                  <small>Flame | Dmg 24 | Cost 0</small>
                </button>
                <button class="gh-btn move">
                  <strong>Protocol Break</strong>
                  <small>Void | Dmg 38 | Cost 2</small>
                </button>
                <button class="gh-btn move">
                  <strong>Mars Veil</strong>
                  <small>Flame | Heal 20 | Cost 1</small>
                </button>
                <button class="gh-btn move">
                  <strong>Swap Sigil</strong>
                  <small>Utility | Tactical switch</small>
                </button>
              </div>
            </section>
          </main>
        </body>
        </html>
        """
    )


def ux_flows_md() -> str:
    return dedent(
        """
        # Ghostline UX Flows

        ## Core Loop
        1. Start Run
        2. Review Champion Forecast
        3. Select Active Sigil
        4. Execute turn actions
        5. Resolve status + energy
        6. Intermission tuning (optional swap)
        7. Advance or fail and restart

        ## HUD Priorities
        - Keep HP and Energy visible at all times.
        - Show one high-contrast threat indicator before enemy burst turns.
        - Preserve move readability with type + cost + output in one line.

        ## UI Rules
        - Combat actions: minimum 44px touch target.
        - Critical state uses `--gh-bad`; avoid red for neutral labels.
        - Success moments use brief motion (120-300ms), no long delays.
        - Mobile layout stacks move cards into one column under 760px width.
        """
    )


def ui_schema_json() -> str:
    data = {
        "theme": THEME["name"],
        "screens": [
            {
                "id": "main_menu",
                "widgets": ["start_button", "run_history", "lore_tip"],
            },
            {
                "id": "battle",
                "widgets": [
                    "player_status",
                    "enemy_status",
                    "move_grid",
                    "battle_log",
                    "threat_indicator",
                ],
            },
            {
                "id": "intermission",
                "widgets": ["roster_swap", "heal_choice", "next_champion_preview"],
            },
        ],
        "hud": {
            "always_visible": ["hp_bar", "energy_bar", "shield_pill"],
            "conditional": ["critical_alert", "burst_warning"],
        },
    }
    return json.dumps(data, indent=2)


def readme_md(out_dir: Path) -> str:
    rel_out = out_dir.as_posix()
    return dedent(
        f"""
        # Ghostline Game Pack

        Generated assets, HUD templates, and UI/UX scaffolding for your battle game.

        ## Regenerate

        ```bash
        python3 scripts/generate_game_pack.py --out {rel_out}
        ```

        ## Contents
        - `assets/icons/*.svg` - combat and utility icons.
        - `assets/hud/*.svg` - frame + bar references.
        - `assets/backgrounds/*.svg` - themed backdrops.
        - `ui/tokens.css` - design tokens.
        - `ui/components.css` - reusable HUD/GUI styles.
        - `ui/hud_overlay.html` - visual reference implementation.
        - `ux/flows.md` - interaction flow guidance.
        - `data/ui_schema.json` - screen/widget map.
        - `manifest.json` - generation metadata and file index.
        """
    )


def generate(out_dir: Path) -> None:
    files: dict[str, str] = {}

    # Core docs and style system
    files["README.md"] = readme_md(out_dir)
    files["ui/tokens.css"] = tokens_css()
    files["ui/components.css"] = components_css()
    files["ui/hud_overlay.html"] = hud_overlay_html()
    files["ux/flows.md"] = ux_flows_md()
    files["data/ui_schema.json"] = ui_schema_json()

    # HUD assets
    files["assets/hud/hud_frame.svg"] = hud_frame_svg()
    files["assets/hud/hp_bar_fill.svg"] = bar_fill_svg("hp")
    files["assets/hud/energy_bar_fill.svg"] = bar_fill_svg("energy")

    # Icon assets
    for name, svg in icon_svgs().items():
        files[f"assets/icons/{name}"] = svg

    # Background assets
    for name, svg in background_svgs().items():
        files[f"assets/backgrounds/{name}"] = svg

    written = []
    for rel_path, content in files.items():
        path = out_dir / rel_path
        write_file(path, content)
        written.append(rel_path)

    manifest = {
        "name": "Ghostline Game Pack",
        "theme": THEME["name"],
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "file_count": len(written),
        "files": sorted(written),
    }
    write_file(out_dir / "manifest.json", json.dumps(manifest, indent=2))

    print(f"Generated {len(written) + 1} files in {out_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Ghostline game assets/HUD/UI pack.")
    parser.add_argument(
        "--out",
        default="canvas/game_pack",
        help="Output directory (default: canvas/game_pack)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out).expanduser().resolve()
    generate(out_dir)


if __name__ == "__main__":
    main()
