# ✈️ Fly-in-Mag Drone Map Generator

> Generate procedural drone-navigation maps from real OpenStreetMap road networks.

---

## 🌍 Overview

**Fly-in-Mag Drone Map Generator** transforms real-world road infrastructure into custom drone-routing simulation maps.

Using the OpenStreetMap Overpass API, the generator extracts road networks (motorways or all roads), detects intersections and critical routing hubs, then exports a lightweight text-based map format ready for drone simulations, AI pathfinding experiments, swarm systems, or logistics research.

Perfect for:

- 🚁 Drone swarm simulations
- 🧠 Pathfinding & graph algorithms
- 📡 Autonomous routing systems
- 🗺️ Synthetic logistics environments
- 🎮 Simulation games & AI experiments

---

# ✨ Features

## 🛣️ Real-World Road Data
Fetches live OpenStreetMap data directly from the Overpass API.

- Motorways only
- Or every road in a country

---

## 🧭 Smart Hub Detection
Automatically identifies:

- Intersections
- Route endpoints
- Critical navigation hubs

---

## 🔗 Graph Generation
Builds realistic undirected road connections between hubs.

---

## 🎨 Randomized Metadata
Each generated hub may include:

- Zones
  - `normal`
  - `restricted`
  - `priority`
  - `blocked`

- Colors
- Drone capacity limits

---

## 🚦 Dynamic Connection Constraints
Randomly applies link capacities to simulate congestion or bandwidth limits.

---

## 🌎 Country Support
Generate maps for any country using ISO country codes.

Examples:

| Country | Code |
|---|---|
| Austria | `AT` |
| Germany | `DE` |
| Monaco | `MC` |
| France | `FR` |

---

# 📦 Installation

## Requirements

- Python 3.8+
- Internet connection

---

## Clone Repository

```bash
git clone https://github.com/yourusername/fly-in-mag-generator.git
cd fly-in-mag-generator
