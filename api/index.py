from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)

# NHANES Variable Mapping for high-integrity auditing
BIO_MARKERS = {
    'SEQN': 'Respondent_ID',
    'DR1TFIBE': 'Fiber_g',
    'DR1TMAGN': 'Magnesium_mg',
    'DR1TVB6': 'B6_mg',
    'DR1TKCAL': 'Calories_kcal',
    'DR1TPROT': 'Protein_g',
    'DR1TCARB': 'Carbs_g',
    'DR1TSUGR': 'Sugar_Total_g'
}

@app.route('/')
def audit_summary():
    file_path = os.path.join(os.getcwd(), 'DR1TOT_J.XPT')
    
    if not os.path.exists(file_path):
        return jsonify({"error": "Data asset missing from root."})

    try:
        # Load the dataset
        df = pd.read_sas(file_path, format='xport')
        
        # Clean column names
        df.columns = [c.decode('utf-8') if isinstance(c, bytes) else c for c in df.columns]
        
        # Filter for our specific bio-markers
        audit_df = df[list(BIO_MARKERS.keys())].rename(columns=BIO_MARKERS)
        
        # Calculate Averages for the 2017-2018 Population Cycle
        stats = {
            "Cycle": "2017-2018",
            "Population_Sample_Size": len(audit_df),
            "Averages": {
                "Daily_Fiber_Avg": round(audit_df['Fiber_g'].mean(), 2),
                "Daily_Magnesium_Avg": round(audit_df['Magnesium_mg'].mean(), 2),
                "Fiber_Deficit_vs_50g_Goal": round(50 - audit_df['Fiber_g'].mean(), 2)
            },
            "Top_10_Audit_Logs": audit_df.head(10).to_dict(orient='records')
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": str(e)})

app = app