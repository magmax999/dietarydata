from flask import Flask, render_template_string, request
import pandas as pd
import os
import glob

app = Flask(__name__)

# Core Bio-Markers
BIO_MARKERS = {
    'SEQN': 'ID',
    'DR1TFIBE': 'Fiber',
    'DR1TMAGN': 'Magnesium',
    'DR1TCALC': 'Calcium'
}

# --- TEMPLATES ---
LAB_WHITE_STYLE = """
<style>
    body { background-color: #ffffff !important; color: #000000; font-family: "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 50px; }
    .container { max-width: 1100px; margin: auto; }
    .header { border-bottom: 3px solid #000; padding-bottom: 20px; margin-bottom: 40px; }
    h1 { margin: 0; font-size: 3rem; font-weight: 900; letter-spacing: -2px; }
    .summary-bar { display: table; width: 100%; border: 2px solid #000; border-collapse: collapse; margin-bottom: 50px; }
    .summary-item { display: table-cell; border: 1px solid #000; padding: 25px; width: 25%; vertical-align: top; }
    .label { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; color: #666; display: block; margin-bottom: 10px; }
    .value { font-size: 2.2rem; font-weight: 800; display: block; }
    .deficit { color: #cc0000; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { text-align: left; background-color: #f0f0f0; border-top: 2px solid #000; border-bottom: 1px solid #000; padding: 15px; font-size: 0.8rem; font-weight: 900; }
    td { padding: 15px; border-bottom: 1px solid #eee; font-size: 1rem; }
    .tag { font-size: 0.7rem; font-weight: 900; border: 1px solid #000; padding: 3px 6px; }
</style>
"""

COMING_SOON_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DietaryData.com | Coming Soon</title>
    {LAB_WHITE_STYLE}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DIETARYDATA.COM</h1>
            <p><strong>STATUS:</strong> BIOLOGICAL AUDIT ENGINE INITIALIZING</p>
        </div>
        <div style="padding: 100px 0; text-align: center;">
            <p style="font-size: 1.5rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">
                Biological Forensic Auditing.<br>Coming Soon.
            </p>
            <p style="color: #666; margin-top: 20px;">[ Systematic Nutrition Audit & Data Transparency ]</p>
        </div>
    </div>
</body>
</html>
"""

AUDIT_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DietaryData.com | Audit</title>
    {LAB_WHITE_STYLE}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DIETARYDATA.COM</h1>
            <p><strong>BIOLOGICAL AUDIT:</strong> {{ stats.Region }}</p>
        </div>
        <div class="summary-bar">
            <div class="summary-item">
                <span class="label">Fiber Baseline</span>
                <span class="value">{{{{ stats.Fiber_g }}}}g</span>
            </div>
            <div class="summary-item">
                <span class="label">50g Target Gap</span>
                <span class="value deficit">-{{{{ stats.Fiber_Gap }}}}g</span>
            </div>
            <div class="summary-item">
                <span class="label">Magnesium Baseline</span>
                <span class="value">{{{{ stats.Magnesium_mg }}}}mg</span>
            </div>
            <div class="summary-item">
                <span class="label">Ca:Mg Ratio</span>
                <span class="value">{{{{ stats.Ca_Mg_Ratio }}}}</span>
            </div>
        </div>
        <h3>AUDIT LOGS</h3>
        <table>
            <thead>
                <tr><th>LOG_ID</th><th>FIBER (50g)</th><th>MAGNESIUM</th><th>CALCIUM</th><th>RATIO</th><th>STATUS</th></tr>
            </thead>
            <tbody>
                {{% for row in logs %}}
                <tr>
                    <td>#{{{{ row.ID }}}}</td>
                    <td>{{{{ row.Fiber }}}}g</td>
                    <td>{{{{ row.Magnesium }}}}mg</td>
                    <td>{{{{ row.Calcium }}}}mg</td>
                    <td>{{{{ row.Ca_Mg_Ratio }}}}</td>
                    <td><span class="tag">VERIFIED</span></td>
                </tr>
                {{% endfor %}}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def coming_soon():
    return render_template_string(COMING_SOON_TEMPLATE)

@app.route('/<country>/<year>')
def run_audit(country, year):
    # Logic: Finds the file in: /data/us/2017/
    data_dir = os.path.join(os.getcwd(), 'data', country.lower(), year)
    xpt_files = glob.glob(os.path.join(data_dir, "*.XPT"))
    
    if not xpt_files:
        return f"AUDIT_OFFLINE: No asset for {country.upper()} in {year}."

    try:
        df = pd.read_sas(xpt_files[0], format='xport')
        df.columns = [c.decode('utf-8') if isinstance(c, bytes) else c for c in df.columns]
        audit_df = df[list(BIO_MARKERS.keys())].rename(columns=BIO_MARKERS).dropna()
        
        # Rounding Protocol
        audit_df['Fiber'] = audit_df['Fiber'].round(1)
        audit_df['Magnesium'] = audit_df['Magnesium'].round(0).astype(int)
        audit_df['Calcium'] = audit_df['Calcium'].round(0).astype(int)
        audit_df['Ca_Mg_Ratio'] = (audit_df['Calcium'] / audit_df['Magnesium']).round(2)
        audit_df['ID'] = audit_df['ID'].astype(int)
        
        stats = {
            "Region": f"{country.upper()} ({year})",
            "Fiber_g": round(audit_df['Fiber'].mean(), 1),
            "Fiber_Gap": round(50 - audit_df['Fiber'].mean(), 1),
            "Magnesium_mg": round(audit_df['Magnesium'].mean(), 1),
            "Ca_Mg_Ratio": round(audit_df['Ca_Mg_Ratio'].mean(), 2)
        }
        
        return render_template_string(AUDIT_TEMPLATE, stats=stats, logs=audit_df.head(20).to_dict(orient='records'))
    except Exception as e:
        return f"SYSTEM_ERROR: {str(e)}"

app = app