import pandas as pd
import numpy as np

def load_and_filter_data(filepath):
    df = pd.read_csv(filepath)
    
    # CRITICAL DATA RULE: Explicitly filter out chain stores and large retail franchises
    # 1. Column-based check (converts chain? to lower string for flexibility)
    is_chain = df['chain?'].astype(str).str.lower().isin(['true', '1', 'yes', 't', 'y'])
    df = df[~is_chain].copy()
    
    # 2. Strict keyword-based check to automatically exclude large national franchises
    large_franchises = [
        'petstock', 'petbarn', 'woolworths', 'coles', 'kmart', 'target', 
        'best & less', 'aldi', 'bunnings', 'myer', 'david jones', 
        'harris scarfe', 'big w', 'officeworks', 'reject shop'
    ]
    name_check = df['name'].astype(str).str.lower()
    is_franchise = name_check.apply(lambda name: any(franchise in name for franchise in large_franchises))
    df = df[~is_franchise].copy()
    
    # KPI Normalization (1-10 Scale)
    if not df.empty:
        den_min = df['pop_density_per_sqkm'].min()
        den_max = df['pop_density_per_sqkm'].max()
        if den_max > den_min:
            df['kpi_score'] = 1.0 + ((df['pop_density_per_sqkm'] - den_min) / (den_max - den_min) * 9.0)
        else:
            df['kpi_score'] = 10.0  # Seeding default score if all matching entries are equal
    else:
        df['kpi_score'] = pd.Series(dtype=float)
        
    return df

def map_to_crm_schema(df):
    crm_df = df.copy()
    
    # Map required columns to CRM schema
    crm_df['number'] = crm_df['phone_number'] if 'phone_number' in crm_df.columns else ''
    
    # Mock missing/default columns
    if 'workers' not in crm_df.columns:
        crm_df['workers'] = crm_df.apply(lambda _: [], axis=1)
        
    if 'actions' not in crm_df.columns:
        crm_df['actions'] = crm_df.apply(lambda _: ['Call Store', 'Log Visit', 'Fetch Live Inventory'], axis=1)
        
    return crm_df

