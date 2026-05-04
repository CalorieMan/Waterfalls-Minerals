# Waterfalls Miner Project — Master Plan and Rebuild Brief

## 1. Core objective

Build a **local-first waterfall discovery app** for the area around **Uvita and Dominical, Costa Rica**.

The app should help the user:

- find **known waterfalls**
- later identify **likely unknown waterfall candidates**
- prioritize waterfalls that are **not far from roads**
- save interesting spots
- export them to formats that work on a phone GPS app

This is the user’s **first vibe-code project**, so the setup must prioritize:

- **fast MVP**
- **easy debugging**
- **pleasant UI**
- **low setup pain**
- **human approval before major actions**

---

## 2. What this project is not

For now, this project is **not**:

- a gold prospecting tool
- a Dockerized production service
- a QGIS-heavy GIS workflow
- a cloud-first app
- a multi-agent autonomous system
- a full terrain-analysis engine from day one

Gold/mineral logic comes later.
QGIS and Docker come later if needed.

---

## 3. Final stack decision

## Development environment
- **MacBook / Apple Silicon**
- **local laptop only**
- **CPU only**
- **Python 3.13.13 from python.org**
- **Git + GitHub**
- **Cursor desktop app**
- **Cursor Agent mode** for building/editing

## App stack
- **Streamlit** for UI
- **Folium** for map rendering
- **streamlit-folium** to embed Folium in Streamlit
- **requests** for API calls
- **pandas** for simple data handling
- **gpxpy** for GPX export

## Data / source strategy for MVP
Start with **OpenStreetMap / Overpass** to fetch known waterfalls, roads, and tracks.

Do **not** start with DEM analysis yet.

Reason:
- much faster to get a useful app working
- lower cognitive and technical overhead
- immediate usefulness for hiking and exploration
- easier for a first vibe-code project

---

## 4. Main UX goal

The first app should let the user:

1. open a map centered on **Uvita / Dominical**
2. load **known waterfalls**
3. show **roads/tracks**
4. filter waterfalls by **distance from road**
5. click and mark waterfalls as:
   - saved
   - maybe
   - ignored
6. export saved spots to:
   - **GPX**
   - **KML**
7. later open those on a phone map/GPS app

Target phone-map usage:
- **Organic Maps** as the simplest free default
- GPX/KML output is the first integration target

---

## 5. Key architecture choices

## Chosen approach
- **Local Python project**
- **No Docker**
- **No QGIS**
- **No cloud deployment**
- **No database at first**
- **No multi-agent orchestration at first**

## Why
This is the least painful path for:
- learning
- fast iteration
- debugging
- building something real immediately

---

## 6. Environment setup that actually worked

There was a problem with Homebrew Python 3.14 creating a venv.
The fix was to use **python.org Python 3.13.13** instead.

## Required interpreter
Use this interpreter path:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
```

Do not use the broken Homebrew 3.14 install for this project.

---

## 7. Project folder

Local folder name used:

```text
uvita-waterfalls
```

GitHub repo name used:

```text
waterfalls-minerals
```

These do **not** need to match.

---

## 8. Git setup decisions

Use:
- **GitHub**
- **private repo**
- local git
- Cursor editing locally

GitHub username:
```text
calorieman
```

Important earlier mistake:
- placeholder repo URLs like `YOUR_USERNAME/...` were accidentally used
- those must be replaced with the real GitHub username

---

## 9. Python setup commands from scratch

From the project folder:

```bash
rm -rf .venv
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m venv .venv
source .venv/bin/activate
python --version
which python
```

Expected result:
- Python 3.13.13
- `which python` points into `uvita-waterfalls/.venv/bin/python`

Then install packages:

```bash
python -m pip install --upgrade pip
pip install streamlit folium streamlit-folium requests pandas gpxpy
pip freeze > requirements.txt
```

---

## 10. Git hygiene

Make sure local environment files are not tracked.

Add this to `.gitignore`:

```text
.venv/
__pycache__/
*.pyc
```

If `.venv` was accidentally committed, fix it with:

```bash
git rm -r --cached .venv
git add .gitignore
git commit -m "Ignore local virtual environment"
git push
```

---

## 11. Cursor usage rules

The user got confused about where to paste the build prompt.

## Correct rule
- **Do not paste natural-language build instructions into the terminal**
- Paste them into **Cursor’s chat / agent panel**
- Use **Agent mode**
- Keep approvals on for:
  - major file edits
  - shell commands
  - package installs
  - anything destructive

## Terminal is only for actual shell commands
Examples:
```bash
streamlit run app.py
pip install -r requirements.txt
git push
```

---

## 12. Initial file structure

Target structure:

```text
uvita-waterfalls/
  app.py
  requirements.txt
  .gitignore
  data/
    raw/
    exports/
    saved/
  scripts/
    fetch_osm_waterfalls.py
    export_gpx.py
    export_kml.py
```

Optional later:
```text
  utils/
  assets/
  tests/
```

---

## 13. MVP feature spec

## MVP version 1
Build a **local Streamlit app** with:

### Map
- Folium map embedded in Streamlit
- centered on **Uvita / Dominical**

### Filters
Sidebar should include:
- radius filter
- max distance from road filter
- category filter:
  - known
  - saved
  - ignored

### Data loading
- fetch known waterfalls from **OpenStreetMap via Overpass**
- load roads and tracks from OSM too

### Interaction
- click waterfall points
- save them to shortlist
- mark as maybe / ignored

### Export
- export saved shortlist to:
  - **GPX**
  - **KML**

### Data storage
simple local file storage in:
- `data/raw`
- `data/saved`
- `data/exports`

### UI
- clean
- pleasant
- dark-mode friendly
- minimal clutter

---

## 14. Exact build prompt for Cursor Agent

Use this as the main initial prompt:

```text
Build a local Python MVP for finding waterfalls around Uvita and Dominical, Costa Rica.

Requirements:
- Use Streamlit for the UI.
- Use Folium for the interactive map.
- Center the map on Uvita/Dominical.
- Create a simple sidebar with:
  - radius filter
  - max distance from road filter
  - category filter: known / saved / ignored
- Add a script that loads known waterfalls from OpenStreetMap via Overpass.
- Show roads and tracks on the map.
- Let me click a waterfall and save it to a shortlist.
- Export shortlisted points to GPX and KML.
- Store data locally in a simple data/ folder.
- Keep dependencies minimal.
- Do not use Docker.
- Do not use QGIS.
- Ask for approval before any major file changes or shell commands.
- Make the UI clean and pleasant, dark mode friendly.
- Start with a minimal working app, then improve.
```

---

## 15. How to run the app

Once files exist:

```bash
source .venv/bin/activate
streamlit run app.py
```

Expected local app URL:
```text
http://localhost:8501
```

---

## 16. Phase plan

## Phase 1 — working useful MVP
Goal: a useful waterfall browser for Uvita / Dominical.

Deliverables:
- map UI
- OSM waterfalls
- roads/tracks
- filter by distance from road
- save/maybe/ignore
- GPX/KML export

This is the first success state.

---

## Phase 2 — improve usefulness
After MVP works, add:

- prettier point styling
- thumbnail/info cards
- local persistence for decisions
- route hints
- “closest road access” logic
- better export names and labels
- grouped saved lists

---

## Phase 3 — add terrain intelligence
Only after MVP works.

Add:
- DEM data
- slope / relief
- stream network logic
- likely waterfall candidate scoring
- distinction between:
  - known waterfalls
  - likely unknown waterfall candidates

This phase is where the app becomes more original.

---

## Phase 4 — optional agentification
Later, once codebase exists and works:

- supervisor workflow
- fetch/update scripts
- refresh waterfall candidates automatically
- export new candidate packs
- maybe notify user of newly ranked spots

Do **not** start here.

---

## 17. User constraints that matter

Another agent should respect these:

- user is **not a dev**
- user is somewhat comfortable with:
  - terminal
  - Python
  - Git
- user is **not comfortable** with:
  - Docker
  - QGIS
- user wants:
  - fast MVP
  - easy debugging
  - nice UI
  - local setup
  - free tools for now
  - human approval before big changes
- user wants this as a **first vibe-code project**
- user wants **waterfalls first**, not gold
- user wants results that can go onto a phone GPS app

---

## 18. What another agent should not do

Another agent should **not**:

- push Docker
- push QGIS immediately
- propose cloud architecture first
- make this a large autonomous multi-agent system
- start with Costa Rica-wide raster processing
- start with geology/minerals/gold
- require paid APIs
- over-engineer storage or infra
- ask user to learn a bunch of GIS before MVP

---

## 19. Recommended workflow for another LLM/agent

Use this order:

1. inspect existing repo structure
2. confirm `.venv` and interpreter path
3. confirm `requirements.txt`
4. create/update minimal Streamlit + Folium app
5. create OSM Overpass fetch script
6. run app locally
7. fix errors
8. keep UI clean
9. add save/export logic
10. only then add advanced features

---

## 20. Current likely technical priorities

If rebuilding from scratch, the next coding tasks should be:

### Task 1
Create:
- `app.py`
- `scripts/fetch_osm_waterfalls.py`

### Task 2
Implement Overpass fetch for:
- waterfalls
- roads/tracks

### Task 3
Render:
- map centered on Uvita / Dominical
- waterfall points
- roads/tracks

### Task 4
Add sidebar filtering:
- radius
- road distance
- category

### Task 5
Add persistence:
- save / maybe / ignore
- simple JSON/CSV storage

### Task 6
Export saved set:
- GPX
- KML

---

## 21. Suggested local data formats

For simplicity:

### Raw fetched data
- JSON

### Saved review states
- CSV or JSON

### Exports
- GPX
- KML

Avoid databases for now.

---

## 22. Recovery notes / earlier pitfalls

### Problem encountered
Homebrew Python 3.14 venv creation failed with `ensurepip` error.

### Fix
Use python.org Python 3.13.13.

### Problem encountered
User tried to use `cursor .` in terminal.

### Resolution
Not necessary. Open the Cursor desktop app directly and open the project folder manually.

### Problem encountered
User pasted build instructions into terminal.

### Resolution
Build instructions go into Cursor Agent chat, not terminal.

### Problem encountered
Git remote used placeholder values like:
- `YOUR_USERNAME`
- `YOUR_GITHUB_USERNAME`

### Fix
Use actual GitHub username:
```text
calorieman
```

### Problem encountered
`.venv` was being tracked by git.

### Fix
Add `.venv/` to `.gitignore` and untrack it.

---

## 23. One-paragraph project concept

This project is a local-first Python app for discovering and organizing waterfalls around Uvita and Dominical, Costa Rica. The first version should use OpenStreetMap/Overpass data to show known waterfalls, roads, and tracks in a clean Streamlit + Folium interface, with filters for accessibility and distance from roads, plus shortlist and GPX/KML export for phone navigation. It should be built in Cursor using Agent mode, with a local Python 3.13 venv, GitHub-backed version control, minimal dependencies, no Docker, and no QGIS. The goal is a fast, pleasant, useful MVP that can later evolve into a more advanced terrain-intelligence tool that identifies likely unknown waterfalls from topography and stream analysis.

---

## 24. Hand-off prompt for another LLM or agent

Use this if you need to restart with another model:

```text
You are helping build a local-first Python app called Waterfalls Miner.

Goal:
Build a useful MVP for finding waterfalls around Uvita and Dominical, Costa Rica.

User profile:
- first vibe-code project
- not a developer
- wants fast MVP, easy debugging, nice UI
- local laptop only
- Mac Apple Silicon
- CPU only
- free tools for now
- wants human approval before major actions
- does not want Docker or QGIS yet

Environment:
- local folder: uvita-waterfalls
- GitHub repo: waterfalls-minerals
- GitHub username: calorieman
- use python.org Python 3.13.13, not Homebrew 3.14
- venv should be created from:
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3

Current stack:
- Streamlit
- Folium
- streamlit-folium
- requests
- pandas
- gpxpy
- Git + GitHub
- Cursor desktop app in Agent mode

Do not:
- propose Docker
- propose QGIS
- start with gold/minerals
- over-engineer infrastructure
- require paid APIs
- start with country-scale raster analysis

MVP requirements:
- map centered on Uvita/Dominical
- fetch known waterfalls from OpenStreetMap via Overpass
- show roads and tracks
- sidebar filters:
  - radius
  - max distance from road
  - category filter: known / saved / ignored
- click and save waterfall spots
- export saved shortlist to GPX and KML
- store data locally in simple files under data/

Preferred file structure:
- app.py
- requirements.txt
- data/raw
- data/saved
- data/exports
- scripts/fetch_osm_waterfalls.py
- scripts/export_gpx.py
- scripts/export_kml.py

Workflow:
1. confirm venv/interpreter
2. create minimal files
3. implement Overpass fetch
4. render map in Streamlit
5. add filters
6. add save/ignore logic
7. add GPX/KML export
8. run locally and debug
9. only later add terrain-based unknown-waterfall candidate logic
```

---

## 25. Minimal “from zero” rebuild checklist

```text
[ ] Install python.org Python 3.13.13
[ ] Create .venv from python.org interpreter
[ ] Activate venv
[ ] Install streamlit, folium, streamlit-folium, requests, pandas, gpxpy
[ ] Create requirements.txt
[ ] Add .gitignore
[ ] Ensure repo connected to GitHub
[ ] Open folder in Cursor desktop app
[ ] Use Cursor Agent mode
[ ] Paste MVP build prompt into agent chat
[ ] Approve file creation
[ ] Run streamlit run app.py
[ ] Debug until map loads
[ ] Add OSM waterfall fetch
[ ] Add save/export
```
