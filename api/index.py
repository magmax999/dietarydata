from flask import Flask, jsonify
import pandas as pd
import os
import numpy as np

app = Flask(__name__)

# Primary Bio-Markers for the Audit & Patch Protocol
BIO_MARKERS = {
    'SEQN': 'Respondent_ID',
    'DR1TFIBE': 'Fiber_g',
    'DR1TMAGN': 'Magnesium_mg',
    'DR1TCALC': 'Calcium_mg',
    'DR1TKCAL': 'Calories_kcal',
    'DR1TPROT': 'Protein_g',
    'DR1TCARB': 'Carbs_g',
    'DR1TSUGR': 'Sugar_Total_g',
    'DR1TVB6': 'B6_mg'
}

@app.route('/')
def biological_audit():
    file_path = os.path.join(os.getcwd(), 'DR1TOT_J.XPT')
    
    if not os.path.exists(file_path):
        return jsonify({"status": "Error", "message": "Data asset missing."})

    try:
        # 1. Load Raw Data
        df = pd.read_sas(file_path, format='xport')
        df.columns = [c.decode('utf-8') if isinstance(c, bytes) else c for c in df.columns]
        
        # 2. Filter & Map Columns
        audit_df = df[list(BIO_MARKERS.keys())].rename(columns=BIO_MARKERS)
        
        # 3. Data Cleaning: Remove "Null" Days (NaN) and Zero-Calorie errors
        # This ensures we are only auditing actual consumption events.
        audit_df = audit_df.dropna(subset=['Fiber_g', 'Magnesium_mg', 'Calories_kcal'])
        audit_df = audit_df[audit_df['Calories_kcal'] > 0]

        # 4. Calculate Logic: Calcium-to-Magnesium Ratio
        # Ideal balance is often cited as 2:1 or 1:1; population average is usually skewed.
        audit_df['Ca_Mg_Ratio'] = (audit_df['Calcium_mg'] / audit_df['Magnesium_mg']).round(2)

        # 5. Protocol Benchmarking
        stats = {
            "Metadata": {
                "Project": "DietaryData.com",
                "Cycle": "2017-2018 NHANES",
                "Clean_Sample_Size": len(audit_df)
            },
            "Population_Averages": {
                "Fiber_g": round(audit_df['Fiber_g'].mean(), 2),
                "Magnesium_mg": round(audit_df['Magnesium_mg'].mean(), 2),
                "Calcium_mg": round(audit_df['Calcium_mg'].mean(), 2),
                "Avg_Ca_Mg_Ratio": round(audit_df['Ca_Mg_Ratio'].mean(), 2)
            },
            "Protocol_Gap_Analysis": {
                "Fiber_Deficit_vs_50g_Target": round(50 - audit_df['Fiber_g'].mean(), 2),
                "Magnesium_Deficit_vs_420mg_Target": round(420 - audit_df['Magnesium_mg'].mean(), 2)
            },
            "Individual_Audit_Logs": audit_df.head(15).replace([np.inf, -np.inf], 0).to_dict(orient='records')
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"status": "Protocol_Failure", "error": str(e)})

# Vercel entry point
app = app