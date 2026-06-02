# Objective
Extend the existing Streamlit dashboard (`src/app.py`) to include a detailed, clickable Store Directory UI. This UI must integrate with the schema definitions from the `hempflow-logistic-crm` codebase.

# Constraints
- Framework: Streamlit (`st`).
- Styling: Maintain the existing Glassmorphic/Premium styling (Outfit and Inter fonts) established in `src/app.py`.
- Integration: The data must conform to the Hempflow CRM schema, which expects the following entity structure: `store_id`, `name`, `number` (phone), `address`, `workers` (list/count), and `actions` (e.g., call, log visit).

# Tasks
1. **Data Mapping (`src/data_processor.py`)**:
   - Add a function `map_to_crm_schema(df)` that takes the existing filtered pandas DataFrame and maps its columns to match the `hempflow-logistic-crm` schema requirements. 
   - Mock empty/default columns for `workers` (e.g., default to `[]` or `0`) and `actions` if they do not exist in the current CSV.

2. **UI Implementation (`src/app.py`)**:
   - Below the "Bottom Grid Panel" in the current layout, create a new section titled "CRM Store Directory".
   - Iterate through the mapped CRM dataframe and render each store as a clickable Streamlit container or expander (`st.expander`).
   - **Inside the Expander/Dialog**:
     - Display the Store Name and Address.
     - Display the `number` (phone).
     - Display the `workers` assigned to this store (from the CRM schema).
     - Create interactive Streamlit buttons for `actions` (e.g., `st.button("Log Visit", key=f"visit_{store_id}")` and `st.button("Fetch Live Inventory", key=f"inv_{store_id}")`).
   - If the "Fetch Live Inventory" button is clicked, it should trigger `live_product_extraction` from `src/search_api.py` and display the deducer results as a JSON/Table snippet inside the expander.

# Output
Provide the updated code blocks for `src/data_processor.py` (mapping function) and `src/app.py` (UI rendering logic).