# Product Requirements Document (PRD): Retailer Map & Routing Dashboard

## 1. Project Overview
A web-based application designed to visualize and interact with a database of specialized retailers. The application consumes a standardized CSV dataset, evaluates each store based on a designated KPI, and provides both geographical (map) and tabular (non-map) interfaces. A core feature is an automated routing engine that calculates the most efficient 5-store sequence from a user-defined origin.

## 2. Data Assumptions
* **Input Source:** A static CSV file containing independent and specialized stores (large franchise chains are excluded by default).
* **Schema:** `store_id`, `name`, `address`, `suburb`, `chain?`, `website_url`, `phone_number`, `lat`, `lng`, `apportioned_pop`, `pop_density_per_sqkm`, `distance_km`.

## 3. User Stories
* **US-01 [Visualization]:** As a user, I want to see all stores plotted on an interactive map so that I can understand their geographical distribution.
* **US-02 [KPI Evaluation]:** As a user, I want each store on the map to be visually graded (e.g., color-coded or size-scaled) based on its population density KPI, allowing me to quickly identify high-potential areas.
* **US-03 [Tabular View]:** As a user, I want a non-map list/table interface of the stores so that I can quickly read their details (address, contact info, KPI score) without navigating a map.
* **US-04 [Route Optimization]:** As a user, I want to input my current location (or drop a pin) and request a 5-store route so that the system generates the fastest continuous journey connecting my origin to those 5 locations.

## 4. Functional Requirements
* **FR-1 Data Ingestion:** The system must load and parse the defined CSV format on startup.
* **FR-2 KPI Calculation Engine:** * Initially, the system will normalize the `pop_density_per_sqkm` column to a 1-10 grading scale.
  * The architecture must allow this module to be easily swapped out for a more complex, multi-variable optimization algorithm later.
* **FR-3 Map Interface:**
  * Render markers at the `lat`/`lng` coordinates.
  * Markers must display store `name`, `address`, and KPI grade upon hover or click.
* **FR-4 Tabular Interface:**
  * Display a data grid featuring the CSV columns and the computed KPI grade.
* **FR-5 Routing Engine:**
  * Accept origin coordinates (Latitude/Longitude).
  * Identify the 5 most optimal stores to visit (can be based on proximity to origin, highest KPI, or user selection).
  * Calculate the Traveling Salesperson Problem (TSP) solution for the origin + 5 nodes to output the fastest sequential route.
  * Display the polyline route on the map and a step-by-step itinerary in the UI.

## 5. Out of Scope (Current Iteration)
* Live data scraping or database write-operations.
* Routes exceeding 5 stores.
* Authentication and user profiles.