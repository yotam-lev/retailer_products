# Proposed Architecture & Tech Stack

## Front-End & Framework
* **Streamlit / Dash (Python):** Ideal for rapidly standing up data-heavy dashboards with both map and table views.
* **Folium / Plotly Mapbox:** For rendering the interactive map interface and routing polylines.

## Back-End & Logic
* **Pandas:** For loading the CSV, handling the tabular interface, and calculating the baseline KPI.
* **NetworkX / OSMnx:** For calculating real-world driving distances and generating the graph networks needed for the route.
* **Google OR-Tools / SciPy:** For solving the route optimization mathematically (Traveling Salesperson Problem with a 6-node matrix: 1 origin + 5 stores).

## Deployment
* **Docker:** Containerized for easy deployment to cloud providers or local execution.