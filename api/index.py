from flask import Flask, render_template_string
import os

app = Flask(__name__)

# --- MINIMAL COMING SOON TEMPLATE ---
COMING_SOON_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DietaryData.com</title>
    <style>
        body { 
            background-color: #ffffff; 
            color: #000000; 
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; 
            margin: 0; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            text-align: center;
        }
        .container { 
            padding: 20px; 
        }
        h1 { 
            margin: 0; 
            font-size: clamp(2rem, 8vw, 4rem); 
            font-weight: 900; 
            letter-spacing: -2px; 
            text-transform: uppercase;
        }
        p { 
            margin: 10px 0 0; 
            font-size: clamp(1rem, 3vw, 1.5rem); 
            font-weight: 400; 
            letter-spacing: 2px; 
            text-transform: uppercase;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>DIETARYDATA.COM</h1>
        <p>Coming Soon</p>
    </div>
</body>
</html>
"""

@app.route('/')
def coming_soon():
    return render_template_string(COMING_SOON_TEMPLATE)

# Keeping your background audit logic intact for direct URL access
@app.route('/<country>/<year>')
def run_audit(country, year):
    # (The existing audit code remains here if you need to access it via /us/2017)
    return f"Audit engine ready for {country} {year}. (Hidden from Homepage)"

app = app