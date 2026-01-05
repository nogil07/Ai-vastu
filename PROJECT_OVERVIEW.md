# Project Overview: Vastu AI
**Version:** 1.0
**Domain:** Architecture / Generative AI / Vedic Science

## 1. Project Definition
Vastu AI is an intelligent architectural design system that generates floor plans and validation reports based on user requirements and ancient Vastu Shastra principles. Unlike standard layout generators, it treats Vastu compliance (directional alignment, zonal strength) as a hard constraint in its optimization engine.

## 2. Core Workflow
1.  **User Input**: User provides Plot dimensions, Facing, Room needs, and Lifestyle preferences via the **Next.js Frontend**.
2.  **Rule Engine**: The **FastAPI Backend** processes these inputs:
    *   Calculates the *Brahmasthan* (Center).
    *   Maps directions (N, S, E, W) to elemental zones (Fire, Water, Earth, Air).
    *   Determines ideal zones for each room (e.g., Kitchen in SE/NW).
3.  **Layout Generation (AI)**:
    *   The system allocates rooms to a 2D grid based on plot size.
    *   It uses a "Floor Allocator" algorithm to fit rooms into valid Vastu zones.
    *   Generates 3 distinct variants.
4.  **Reporting**:
    *   Calculates a "Vastu Score" (0-100).
    *   Generates an architectural Blueprint (Images).
    *   Creates a detailed PDF Report explaining *why* the design is good (using local LLM `distilgpt2` for text).

## 3. Module Breakdown

### Frontend (`/frontend`)
*   **Framework**: Next.js 14 (App Router), TypeScript.
*   **Key Components**:
    *   `VastuForm.tsx`: The main interactive engine. Handles state for 8 distinct data categories.
    *   `ArchitecturalScene.tsx`: 3D visual layer using React Three Fiber.
*   **Styling**: Tailwind CSS v4 (Glassmorphism, Dark/Gold Luxury Theme).

### Backend (`/app`)
*   **`main.py`**: The API Gateway. Defines `POST /generate-design`.
*   **`schemas.py`**: Pydantic models defining the strict data contract (Input/Output).
*   **`rule_engine.py`**: The "Vastu Expert" logic. Contains the dictionary of favorable directions for every room type.
*   **`floor_allocator.py`**: The "Architect" logic. Uses basic constrained packing to fit rooms onto the plot grid.
*   **`report_generator.py`**: Uses `ReportLab` to draw professional PDFs.
*   **`text_generator.py`**: Connects to local HuggingFace models (`distilgpt2`) to caption the report with "AI Insights".

## 4. Key Features
*   **Granular Vastu Control**: Strict, Balanced, or Relaxed modes.
*   **Local Processing**: Runs entirely offline (Local LLM, Local Image Generation).
*   **Professional Output**: Generates downloadable PDF reports suitable for client presentation.
