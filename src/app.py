import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
from src.data_processor import load_and_filter_data
from src.map_renderer import create_map
from src.routing_engine import solve_tsp, get_osrm_route_geometry, haversine_distance

# Set up page configurations
st.set_page_config(
    page_title="Retail Routing & KPI Dashboard",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Outfit and Inter Google Fonts + Glassmorphic Cards)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');
        
        /* Font assignments */
        html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6, .outfit-font {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
        }
        
        /* Custom Header Styling */
        .app-title {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
            padding-bottom: 0px;
        }
        
        .app-subtitle {
            color: #64748B;
            font-size: 1.05rem;
            margin-top: 0px;
            margin-bottom: 2rem;
        }
        
        /* Glassmorphic card design */
        .premium-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(226, 232, 240, 0.8);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            padding: 1.25rem;
            margin-bottom: 1rem;
        }
        
        .itinerary-stop {
            border-left: 4px solid #4F46E5;
            padding-left: 1rem;
            margin-bottom: 0.8rem;
            background: #F8FAFC;
            border-radius: 0 8px 8px 0;
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
            border-top: 1px solid #F1F5F9;
            border-bottom: 1px solid #F1F5F9;
            border-right: 1px solid #F1F5F9;
        }
        
        .kpi-badge {
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            color: white;
        }
        
        .kpi-high { background-color: #10B981; }
        .kpi-medium { background-color: #F59E0B; }
        .kpi-low { background-color: #EF4444; }
        
        /* Table enhancements */
        .dataframe {
            border-collapse: collapse;
            width: 100%;
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Metric badges */
        .metric-badge {
            background-color: #EEF2F6;
            color: #4F46E5;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            margin-right: 0.5rem;
            border: 1px solid #E2E8F0;
        }
    </style>
""", unsafe_allow_html=True)

# App title and subtitle
st.markdown("<h1 class='app-title outfit-font'>Retail Map & Routing Optimizer</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>A collaborative multi-agent platform for specialized retail analytics, KPI color-coding, and Traveling Salesperson (TSP) route generation.</p>", unsafe_allow_html=True)

# Load CSV data
DATA_FILE = "data/sorted_results.csv"
try:
    df = load_and_filter_data(DATA_FILE)
except Exception as e:
    st.error(f"Error loading CSV data from '{DATA_FILE}': {e}")
    st.stop()

# Initialize session state for route calculations
if 'route_data' not in st.session_state:
    st.session_state.route_data = None

# ---- SIDEBAR CONTROLLERS ----
with st.sidebar:
    st.markdown("<h3 class='outfit-font' style='margin-bottom: 1rem; color: #1E293B;'>📍 Routing Parameters</h3>", unsafe_allow_html=True)
    
    # 1. Custom Origin Configuration
    st.markdown("<b>Configure Starting Origin</b>", unsafe_allow_html=True)
    # Seeding defaults close to Macquarie Park/Ryde (where most stores are clustered)
    origin_lat = st.number_input("Latitude", value=-33.7850, format="%.6f")
    origin_lng = st.number_input("Longitude", value=151.1200, format="%.6f")
    origin = (origin_lat, origin_lng)
    
    st.markdown("<hr style='margin: 1.25rem 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
    
    # 2. Select Route Optimization Strategy
    st.markdown("<b>Select Route Strategy</b>", unsafe_allow_html=True)
    strategy = st.selectbox(
        "Choose strategy to select 5 stores:",
        [
            "Top 5 KPI Specialized Stores",
            "5 Closest Specialized Stores",
            "Manual Store Selection"
        ]
    )
    
    # Render different inputs based on chosen strategy
    target_stores_df = pd.DataFrame()
    if strategy == "Top 5 KPI Specialized Stores":
        # Sort by KPI score descending and take top 5
        target_stores_df = df.sort_values(by='kpi_score', ascending=False).head(5)
        st.info("ℹ️ System will select the 5 specialized stores with the highest population density KPI scores.")
        
    elif strategy == "5 Closest Specialized Stores":
        # Calculate straight-line distance to origin and sort
        df_dist = df.copy()
        df_dist['dist_to_origin'] = df_dist.apply(
            lambda r: haversine_distance(origin, (r['lat'], r['lng'])), axis=1
        )
        target_stores_df = df_dist.sort_values(by='dist_to_origin').head(5)
        st.info("ℹ️ System will select the 5 specialized stores closest to your specified origin.")
        
    elif strategy == "Manual Store Selection":
        st.write("Pick exactly 5 stores to visit:")
        selected_names = st.multiselect(
            "Select specialized stores:",
            options=df['name'].tolist(),
            default=df['name'].head(5).tolist()
        )
        if len(selected_names) != 5:
            st.warning("⚠️ Please select exactly 5 stores to compute the route.")
        else:
            target_stores_df = df[df['name'].isin(selected_names)].copy()
            
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # 3. Action Button
    calc_ready = (len(target_stores_df) == 5)
    if st.button("Generate Optimized Route ➔", disabled=not calc_ready, type="primary"):
        with st.spinner("Solving Traveling Salesperson Problem (TSP) using OR-Tools..."):
            store_coords = target_stores_df[['lat', 'lng']].values.tolist()
            store_records = target_stores_df.to_dict('records')
            
            # Solve TSP
            # route_idx is a list of sequence indices: e.g. [0, 2, 4, 1, 3, 5, 0]
            # where 0 is the starting origin and 1-5 correspond to the stores
            route_idx, dist_matrix = solve_tsp(origin, store_coords)
            
            # Map index back to ordered store coordinates & data records
            ordered_coords = [origin]
            ordered_stops = []
            for r_idx in route_idx[1:-1]:
                # r_idx corresponds to (store index + 1) in coords array
                store_item = store_records[r_idx - 1]
                ordered_coords.append((store_item['lat'], store_item['lng']))
                ordered_stops.append(store_item)
            ordered_coords.append(origin)  # complete loop
            
            # Query actual driving road segments geometry from OSRM
            polyline_coords, total_dist_m, total_dur_s = get_osrm_route_geometry(ordered_coords)
            
            # Save to session state
            st.session_state.route_data = {
                'polyline_coords': polyline_coords,
                'stops': ordered_stops,
                'origin': origin,
                'total_distance_km': total_dist_m / 1000.0,
                'total_duration_min': total_dur_s / 60.0
            }
            st.success("TSP Solution found!")

# ---- DASHBOARD MAIN LAYOUT ----
col_map, col_details = st.columns([1.6, 1.0])

# Left column: Interactive Map Panel
with col_map:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<h3 class='outfit-font' style='margin-top:0; color: #1E293B;'>🗺️ Interactive Spatial Map</h3>", unsafe_allow_html=True)
    
    # Center map on specified origin or average of dataset
    map_center = {'lat': origin_lat, 'lng': origin_lng}
    
    # Generate Map with active route overlay if calculated
    m = create_map(df, map_center, route_data=st.session_state.route_data)
    folium_static(m, width=760, height=520)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Right column: Route Details & Itinerary Panel
with col_details:
    st.markdown("<div class='premium-card' style='height: 590px; overflow-y: auto;'>", unsafe_allow_html=True)
    
    if st.session_state.route_data is None:
        st.markdown("<h3 class='outfit-font' style='margin-top:0; color: #1E293B;'>⚡ Route Optimizer Details</h3>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; color: #64748B; padding-top: 5rem;'>
                <p style='font-size: 4rem; margin-bottom: 1rem;'>🧭</p>
                <h4>No Route Generated Yet</h4>
                <p style='font-size: 13px;'>Configure the origin coordinates and select a strategy in the sidebar, then click <b>Generate Optimized Route</b> to compute the fastest sequential road journey.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        rd = st.session_state.route_data
        st.markdown("<h3 class='outfit-font' style='margin-top:0; color: #1E293B;'>🏎️ Optimized TSP Route</h3>", unsafe_allow_html=True)
        
        # Performance Indicators/Metrics
        st.markdown(f"""
            <div style='margin-bottom: 1.25rem;'>
                <span class='metric-badge'>📏 {rd['total_distance_km']:.2f} km</span>
                <span class='metric-badge'>⏱️ {rd['total_duration_min']:.1f} mins driving</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Rich Text Itinerary Listing
        st.markdown("<b>Step-by-Step Itinerary</b>", unsafe_allow_html=True)
        
        # Starting point card
        st.markdown(f"""
            <div class='itinerary-stop' style='border-left-color: #4F46E5;'>
                <span class='kpi-badge' style='background-color: #4F46E5; margin-bottom: 4px;'>START</span>
                <div style='font-weight: 700; font-size: 14px; color: #1E293B;'>Starting Origin Point</div>
                <div style='font-size: 12px; color: #64748B;'>Latitude: {rd['origin'][0]:.5f}, Longitude: {rd['origin'][1]:.5f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Stop-by-stop cards
        for idx, stop in enumerate(rd['stops'], 1):
            kpi = stop['kpi_score']
            kpi_badge_class = 'kpi-high' if kpi >= 7.0 else ('kpi-medium' if kpi >= 4.0 else 'kpi-low')
            
            st.markdown(f"""
                <div class='itinerary-stop' style='border-left-color: {"#10B981" if kpi >= 7.0 else ("#F59E0B" if kpi >= 4.0 else "#EF4444")};'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>
                        <span class='kpi-badge' style='background-color: #06B6D4;'>STOP #{idx}</span>
                        <span class='kpi-badge {kpi_badge_class}'>KPI: {kpi:.1f}</span>
                    </div>
                    <div style='font-weight: 700; font-size: 14px; color: #1E293B;'>{stop['name']}</div>
                    <div style='font-size: 12px; color: #64748B;'>{stop['address']}, {stop['suburb']}</div>
                    <div style='font-size: 11px; color: #94A3B8; margin-top: 2px;'>
                        📞 {stop['phone_number'] if pd.notna(stop['phone_number']) else 'No phone'} | 🔗 <a href="{stop['website_url']}" target="_blank" style="color: #3B82F6;">Website</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # Ending loop card
        st.markdown(f"""
            <div class='itinerary-stop' style='border-left-color: #4F46E5;'>
                <span class='kpi-badge' style='background-color: #4F46E5; margin-bottom: 4px;'>END</span>
                <div style='font-weight: 700; font-size: 14px; color: #1E293B;'>Return to Starting Origin</div>
                <div style='font-size: 12px; color: #64748B;'>Latitude: {rd['origin'][0]:.5f}, Longitude: {rd['origin'][1]:.5f}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---- BOTTOM GRID PANEL ----
st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
st.markdown("<h3 class='outfit-font' style='margin-top:0; color: #1E293B;'>📊 Tabular Specialized Store Listing</h3>", unsafe_allow_html=True)

# Prepare dataframe for displaying
display_cols = ['store_id', 'name', 'address', 'suburb', 'lat', 'lng', 'pop_density_per_sqkm', 'kpi_score', 'phone_number', 'website_url']
grid_df = df[display_cols].copy()
grid_df.rename(columns={
    'store_id': 'Store ID',
    'name': 'Store Name',
    'address': 'Street Address',
    'suburb': 'Suburb',
    'lat': 'Latitude',
    'lng': 'Longitude',
    'pop_density_per_sqkm': 'Pop Density /sqkm',
    'kpi_score': 'KPI Score (1-10)',
    'phone_number': 'Phone Number',
    'website_url': 'Website Link'
}, inplace=True)

# Render interactive table in Streamlit
st.dataframe(
    grid_df.style.format({
        'Latitude': '{:.6f}',
        'Longitude': '{:.6f}',
        'Pop Density /sqkm': '{:,.0f}',
        'KPI Score (1-10)': '{:.2f}'
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("</div>", unsafe_allow_html=True)

# ---- CRM STORE DIRECTORY PANEL ----
st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
st.markdown("<h3 class='outfit-font' style='margin-top:0; color: #1E293B;'>📇 CRM Store Directory</h3>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 0.9rem; margin-bottom: 1.5rem;'>Detailed directory views conforming to the Hempflow CRM schema. Expand a store to log events, call, or fetch real-time inventory classification.</p>", unsafe_allow_html=True)

from src.data_processor import map_to_crm_schema
crm_df = map_to_crm_schema(df)

# Render directory cards
for idx, row in crm_df.iterrows():
    store_id = row.get('store_id', str(idx))
    store_name = row.get('name', 'Unknown Store')
    phone = row.get('number', '')
    address = row.get('address', 'No address available')
    suburb = row.get('suburb', '')
    workers = row.get('workers', [])
    
    title = f"📍 {store_name} ({suburb})" if suburb else f"📍 {store_name}"
    
    with st.expander(title, expanded=False):
        st.markdown(f"**Store ID:** `{store_id}`")
        st.markdown(f"**Address:** {address}")
        st.markdown(f"**Phone (Number):** {phone if phone else 'No phone registered'}")
        
        # Assigned workers
        if isinstance(workers, list) and len(workers) > 0:
            st.markdown(f"**Assigned Workers:** {', '.join(workers)}")
        else:
            st.markdown("**Assigned Workers:** 0 workers assigned")
            
        # CRM Actions
        st.markdown("<br/><b>Interactive CRM Actions</b>", unsafe_allow_html=True)
        col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
        
        with col_act1:
            if st.button("📞 Call Store", key=f"call_{store_id}", use_container_width=True):
                if phone:
                    st.info(f"Initiating call to {phone}...")
                else:
                    st.warning("No phone registered to call.")
                    
        with col_act2:
            if st.button("📝 Log Visit", key=f"visit_{store_id}", use_container_width=True):
                st.success(f"Visit logged successfully for {store_name}!")
                
        with col_act3:
            fetch_clicked = st.button("🔍 Fetch Live Inventory", key=f"inv_{store_id}", type="primary", use_container_width=True)
            
        if fetch_clicked:
            st.markdown("<hr style='margin: 1rem 0; border: 0; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
            st.markdown("##### 🚀 Fetching Live Inventory...")
            with st.spinner("Connecting to site and deducing bedding/litter catalog via Ollama..."):
                try:
                    from src.search_api import live_product_extraction
                    from urllib.parse import urlparse
                    
                    website_url = row.get('website_url', '')
                    if website_url:
                        parsed_uri = urlparse(website_url)
                        domain = parsed_uri.netloc or website_url
                    else:
                        domain = "example.com"
                        
                    results = live_product_extraction(domain, store_id)
                    if results:
                        st.success(f"Successfully deduced {len(results)} inventory items!")
                        # Format list cleanly
                        results_df = pd.DataFrame(results)
                        st.dataframe(results_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No specialized animal bedding or cat litter products detected on this site.")
                except Exception as ex:
                    st.error(f"Error fetching live inventory: {ex}")

st.markdown("</div>", unsafe_allow_html=True)

