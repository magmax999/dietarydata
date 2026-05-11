from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def home():
    # Looks for the data file in the root directory (one level up from /api)
    file_path = os.path.join(os.getcwd(), 'DR1TOT_J.XPT')
    
    if os.path.exists(file_path):
        try:
            # Read the first 10 rows to verify the data is loading
            df = pd.read_sas(file_path, format='xport').head(10)
            
            # Clean column names (decoding bytes to strings if necessary)
            df.columns = [c.decode('utf-8') if isinstance(c, bytes) else c for c in df.columns]
            
            return jsonify({
                "status": "Connected",
                "dataset": "NHANES 2017-2018 Total Nutrients",
                "message": "DietaryData.com is live.",
                "data_preview": df.to_dict(orient='records')
            })
        except Exception as e:
            return jsonify({"status": "Error", "message": f"Failed to read SAS file: {str(e)}"})
    else:
        return jsonify({
            "status": "Error", 
            "message": f"File not found. Expected it at: {file_path}"
        })

# Required for Vercel
if __name__ == "__main__":
    app.run()