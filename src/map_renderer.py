import folium
from folium import DivIcon

def create_map(df, center, route_data=None):
    """
    Generate an interactive Folium Map displaying store markers color-coded by KPI scores,
    and optional driving route polylines with numbered itinerary markers.
    """
    m = folium.Map(location=[center['lat'], center['lng']], zoom_start=12, tiles="cartodbpositron")
    
    # Draw all baseline stores if no specific route is focused (or keep them as small background markers)
    for _, row in df.iterrows():
        # Color coding threshold:
        # High KPI (>= 7.0): Green
        # Medium KPI (>= 4.0): Orange
        # Low KPI (< 4.0): Red
        kpi = row['kpi_score']
        if kpi >= 7.0:
            color = '#2E7D32'  # Green
            badge_cls = 'badge-high'
        elif kpi >= 4.0:
            color = '#EF6C00'  # Orange
            badge_cls = 'badge-medium'
        else:
            color = '#C62828'  # Red
            badge_cls = 'badge-low'
            
        # HTML styled popup for store details
        popup_html = f"""
        <div style="font-family: 'Outfit', 'Inter', sans-serif; font-size: 13px; color: #2C3E50; max-width: 250px;">
            <h5 style="margin: 0 0 5px 0; color: #1E293B; font-weight: 700; font-size: 15px;">{row['name']}</h5>
            <p style="margin: 0 0 8px 0; color: #64748B; font-size: 12px;">{row['address']}, {row['suburb']}</p>
            <div style="margin-bottom: 8px;">
                <span class="{badge_cls}" style="
                    background-color: {color}; 
                    color: white; 
                    padding: 2px 8px; 
                    border-radius: 4px; 
                    font-weight: bold; 
                    font-size: 11px;
                ">KPI: {kpi:.1f}</span>
            </div>
            <div style="border-top: 1px solid #E2E8F0; padding-top: 8px; font-size: 11px;">
                <b>Phone:</b> {row['phone_number'] if pd.notna(row['phone_number']) else 'N/A'}<br>
                <b>Website:</b> <a href="{row['website_url']}" target="_blank" style="color: #3B82F6; text-decoration: none;">Link</a>
            </div>
        </div>
        """
        
        # Simple HTML tooltip for hover
        tooltip_text = f"{row['name']} (KPI Score: {kpi:.1f})"
        
        # Draw base markers (slightly translucent if a route is displayed, to draw focus to the route)
        opacity = 0.4 if route_data else 0.95
        
        folium.CircleMarker(
            location=[row['lat'], row['lng']],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=opacity,
            opacity=opacity,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tooltip_text
        ).add_to(m)
        
    # If route calculations exist, overlay route polylines and numbered stops
    if route_data:
        polyline_coords = route_data.get('polyline_coords')
        stops = route_data.get('stops')  # list of dicts/rows in optimized travel order
        origin = route_data.get('origin')
        
        # 1. Plot Origin Marker
        origin_popup = """
        <div style="font-family: sans-serif; font-size: 12px;">
            <b style="color: #4F46E5;">STARTING ORIGIN</b><br>
            Coordinates: {:.4f}, {:.4f}
        </div>
        """.format(origin[0], origin[1])
        
        # Beautiful star-shaped or colored origin DivIcon
        origin_html = """
        <div style="
            background-color: #4F46E5; 
            color: white; 
            border-radius: 50%; 
            width: 26px; 
            height: 26px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-weight: bold; 
            border: 2px solid white;
            box-shadow: 0 3px 6px rgba(0,0,0,0.4);
        ">★</div>
        """
        folium.Marker(
            location=origin,
            popup=folium.Popup(origin_popup, max_width=200),
            tooltip="Origin",
            icon=DivIcon(icon_size=(26, 26), icon_anchor=(13, 13), html=origin_html)
        ).add_to(m)
        
        # 2. Plot Route Stops
        for idx, stop in enumerate(stops, 1):
            stop_color = '#10B981' if stop['kpi_score'] >= 7.0 else ('#F59E0B' if stop['kpi_score'] >= 4.0 else '#EF4444')
            stop_html = f"""
            <div style="
                background-color: {stop_color}; 
                color: white; 
                border-radius: 50%; 
                width: 28px; 
                height: 28px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-weight: 800; 
                font-size: 13px;
                border: 2.5px solid white;
                box-shadow: 0 4px 8px rgba(0,0,0,0.5);
                font-family: 'Outfit', 'Inter', sans-serif;
            ">{idx}</div>
            """
            
            stop_popup = f"""
            <div style="font-family: 'Outfit', sans-serif; font-size: 13px; color: #2C3E50;">
                <b style="color: #10B981;">STOP #{idx}</b>
                <h5 style="margin: 3px 0; color: #1E293B; font-size: 14px;">{stop['name']}</h5>
                <p style="margin: 0 0 5px 0; color: #64748B; font-size: 11px;">{stop['address']}</p>
                <span style="font-weight: bold; color: {stop_color};">KPI Score: {stop['kpi_score']:.1f}</span>
            </div>
            """
            
            folium.Marker(
                location=[stop['lat'], stop['lng']],
                popup=folium.Popup(stop_popup, max_width=250),
                tooltip=f"Stop {idx}: {stop['name']}",
                icon=DivIcon(icon_size=(28, 28), icon_anchor=(14, 14), html=stop_html)
            ).add_to(m)
            
        # 3. Draw Road-Network Driving Polyline
        if polyline_coords:
            # Draw primary line
            folium.PolyLine(
                locations=polyline_coords,
                color="#4F46E5",
                weight=6,
                opacity=0.85,
                tooltip="Optimized Driving Route"
            ).add_to(m)
            
            # Draw subtle glowing shadow/border under the polyline
            folium.PolyLine(
                locations=polyline_coords,
                color="#818CF8",
                weight=10,
                opacity=0.4,
            ).add_to(m)

    return m

# Importing pandas here inside the popup helper so it works if not imported elsewhere
import pandas as pd

