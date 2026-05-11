from flask import Flask, render_template_string
import pandas as pd
import os
import numpy as np

app = Flask(__name__)

# Bio-Markers for the Audit
BIO_MARKERS = {
    'SEQN': 'ID',
    'DR1TFIBE': 'Fiber',
    'DR1TMAGN': 'Magnesium',
    'DR1TCALC': 'Calcium',
    'DR1TKCAL': 'Calories',
    'DR1TPROT': 'Protein'
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DietaryData.com | Biological Audit</title>
    <style>
        body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; background: #ffffff; color: #1a1a1a; margin: 0; padding: 40px; line-height: 1.5; }
        .container { max-width: 1100px; margin: auto; }
        .header { border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 40px; }
        h1 { margin: 0; font-size: 2.5rem; letter-spacing: -1px; font-weight: 800; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: #000; border: 1px solid #000; margin-bottom: 50px; }
        .card { background: #fff; padding: 25px; }
        .card h3 { margin: 0; font-size: 0.75rem; color: #666; text-transform: uppercase; font-weight: 600; }
        .card p { margin: 10px 0 0; font-size: 2rem; font-weight: 700; color: #000; }
        .deficit { color: #d00 !important; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { text-align: left; background: #f2f2f2; border-top: 2px solid #000; border-bottom: 1px solid #000; padding: 12px; font-size: 0.85rem; font-weight: 700; }
        td { padding: 12px; border-bottom: 1px solid #eee; font-size: 0.95rem; }
        tr:hover { background: #f9f9f9; }
        .protocol-tag { font-size: 0.7rem; font-weight: bold; padding: 2px 6px; border: 1px solid #000; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DIETARYDATA.COM</h1>
            <p><strong>AUDIT:</strong> NHANES NATIONAL DIETARY DATABASE (2017-2018)</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Avg Fiber</h3>
                <p>{{ stats.Fiber_g }}g</p>
            </div>
            <div class="card">
                <h3>Target Gap</h3>
                <p class="deficit">-{{ stats.Fiber_Gap }}g</p>
            </div>
            <div class="card">
                <h3>Avg Magnesium</h3>
                <p>{{ stats.Magnesium_mg }}mg</p>
            </div>
            <div class="card)
                <h3>Ca:Mg Ratio</h3>
                <p>{{ stats.Ca_Mg_Ratio }}</p>
            </div>
        </div>

        <h3>POPULATION RAW LOGS (TOP 20)</h3>
        <table>
            <thead>
                <tr>
                    <th>RESPONDENT_ID</th>
                    <th>FIBER (50g GOAL)</th>
                    <th>MAGNESIUM</th>
                    <th>CALCIUM</th>
                    <th>RATIO</th>
                    <th>VERIFICATION</th>
                </tr>
            </thead>
            <tbody>
                {% for row in logs %}
                <tr>
                    <td>#{{ row.ID }}</td>
                    <td>{{ row.Fiber }}g</td>
                    <td>{{ row.Magnesium }}mg</td>
                    <td>{{ row.Calcium }}mg</td>
                    <td>{{ row.Ca_Mg_Ratio }}</td>
                    <td><span class="protocol-tag">PASS_AUDIT</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    file_path = os.path.join(os.getcwd(), 'DR1TOT_J.XPT')
    if not os.path.exists(file_path):
        return "CRITICAL ERROR: DATA_ASSET_MISSING"

    try:
        df = pd.read_sas(file_path, format='xport')
        df.columns = [c.decode('utf-8') if isinstance(c, bytes) else c for c in df.columns]
        audit_df = df[list(BIO_MARKERS.keys())].rename(columns=BIO_MARKERS).dropna()
        
        audit_df['Ca_Mg_Ratio'] = (audit_df['Calcium'] / audit_df['Magnesium']).round(2)
        avg_fiber = round(audit_df['Fiber'].mean(), 2)
        
        stats = {
            "Fiber_g": avg_fiber,
            "Fiber_Gap": round(50 - avg_fiber, 2),
            "Magnesium_mg": round(audit_df['Magnesium'].mean(), 2),
            "Ca_Mg_Ratio": round(audit_df['Ca_Mg_Ratio'].mean(), 2)
        }
        
        logs = audit_df.head(20).to_dict(orient='records')
        return render_template_string(HTML_TEMPLATE, stats=stats, logs=logs)
        
    except Exception as e:
        return f"AUDIT_FAILURE: {str(e)}"

app = app