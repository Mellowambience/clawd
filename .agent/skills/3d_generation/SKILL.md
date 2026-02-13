---
description: 3D Character Generation & Orchestration Pipeline
version: 1.0.0
author: MIST/Antigravity
---

# 3D Character Synthesis Skill

## 1. Objective
To orchestrate the generation of a rigged, game-ready 3D character mesh from 2D reference images using the Antigravity Agentic Workflow.

## 2. Pipeline Overview
1.  **Concept Phase**: Generate "Orthographic Turnaround" (Front/Side/Back) using Nano Banana Pro (Image Gen).
2.  **Mesh Generation**: Process Turnaround through 3D Generative Model (Rodin/Meshy/Tripo) to get `.obj` or `.glb`.
3.  **Refinement**: Clean topology, reduce poly count for web/game engine.
4.  **Rigging**: Apply Humanoid Skeletal Rig via Blender MCP.
5.  **Integration**: Load into Three.js/Engine.

## 3. Step-by-Step Instructions

### Phase 1: Visual Foundation (Current Step)
-   **Action**: Generate a high-fidelity Character Sheet.
-   **Prompt Requirements**: T-Pose, Neutral Lighting, Orthographic projections, "3D Reference".
-   **Output**: `assets/ref/mist_turnaround.png`.

### Phase 2: Mesh Synthesis
-   **Tool**: External 3D AI (Rodin/Meshy). *Pending API integration.*
-   **Input**: The image from Phase 1.
-   **Goal**: Solid geometry, no non-manifold edges.

### Phase 3: Rigging (Blender MCP)
-   **Script**: `scripts/auto_rig.py` (To be created).
-   **Logic**: Import Mesh -> Scale to Unit -> Generate Metarig -> Match to Volumetric Bounds -> Parent with Automatic Weights.

## 4. Safety & Verification
-   **Check**: Ensure mesh does not exceed 50k triangles for web performance.
-   **Check**: Verify UV map has no overlapping islands.
-   **Visual Test**: Browser Subagent rotates model 360 degrees to check for "melting" or artifacts.
