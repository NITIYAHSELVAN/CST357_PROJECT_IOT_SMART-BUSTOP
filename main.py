import functions_framework
from google.cloud import firestore
import datetime
import requests

# 1. Database setup
db = firestore.Client(database="smartbuststop")

# --- THINGSBOARD SETUP ---
TB_HOST = "eu.thingsboard.cloud" 
TB_ACCESS_TOKEN = "mxuhNss1u6ZklVzdDKAm" 

@functions_framework.http
def smart_bus_stop_data_store(request):
    if request.method == 'POST':
        request_json = request.get_json(silent=True)
        if request_json:
            # --- MALAYSIA TIME STRING ---
            msia_now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            msia_time_str = msia_now.strftime('%Y-%m-%d %H:%M:%S')
            request_json['timestamp'] = msia_time_str
            
            # Force Data Types
            temp = float(request_json.get('temp', 0))
            hum = float(request_json.get('hum', 0))
            ldr = int(request_json.get('ldr', 0))
            presence = request_json.get('presence', False)
            
            # --- LOGIC ALIGNMENT ---
            # We use the mode sent by ESP32, but keep this as a fallback
            request_json['light_mode'] = "Night" if ldr > 2000 else "Day"
            
            # The fan_mode is now primarily controlled by the ESP32 Timer
            # We read what the ESP32 sent, or fallback to the logic
            fan_mode = request_json.get('fan_mode', "OFF")
            
            # 1. UPDATE LATEST STATUS
            db.collection('status').document('latest').set(request_json)

            # 2. THROTTLE LOGS (20s)
            timer_ref = db.collection('settings').document('log_timer')
            timer_doc = timer_ref.get()
            should_log = True
            if timer_doc.exists:
                last_time_str = timer_doc.to_dict().get('last_time')
                last_time = datetime.datetime.strptime(last_time_str, '%Y-%m-%d %H:%M:%S')
                if (msia_now - last_time).total_seconds() < 20:
                    should_log = False
            if should_log:
                db.collection('logs').add(request_json)
                timer_ref.set({'last_time': msia_time_str})

            # 3. PUSH TO THINGSBOARD
            tb_url = f"https://{TB_HOST}/api/v1/{TB_ACCESS_TOKEN}/telemetry"
            tb_payload = {
                "temperature": temp,
                "humidity": hum,
                "ldr_intensity": ldr,
                "passenger_present_num": 1 if presence else 0,
                "fan_status_num": 1 if fan_mode == "ON" else 0,
                "light_status_num": 1 if request_json['light_mode'] == "Night" else 0,
                "light_label": request_json['light_mode']
            }
            try:
                requests.post(tb_url, json=tb_payload, timeout=2)
            except:
                pass

            return "Success", 200
        return "No Data", 400

    else:
        # --- DASHBOARD VIEW ---
        doc = db.collection('status').document('latest').get()
        latest = doc.to_dict() if doc.exists else {}
        
        t = latest.get('temp', 0)
        h = latest.get('hum', 0)
        presence = latest.get('presence', False)
        fan_mode = latest.get('fan_mode', "OFF")
        light_mode = latest.get('light_mode', "Day")
        db_time = latest.get('timestamp', "No Data")

        # Color logic for the dashboard
        light_card_bg = "#2c3e50" if light_mode == "Night" else "#f1c40f"
        light_text_color = "white" if light_mode == "Night" else "#333"

        html = f"""
        <!DOCTYPE html>
        <html><head>
            <meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
            <meta http-equiv='refresh' content='1'>
            <title>Smart Bus Stop Admin</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: #eef2f3; margin: 0; padding: 20px; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; max-width: 1000px; margin: 0 auto; }}
                .card {{ background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; transition: 0.3s; }}
                .card h3 {{ margin: 0; color: #7f8c8d; font-size: 0.8em; text-transform: uppercase; }}
                .value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
                .presence-box {{ grid-column: 1 / -1; background: #2c3e50; color: white; padding: 30px; }}
                .status-on {{ color: #27ae60; }}
                .status-off {{ color: #e74c3c; }}
                .light-card {{ background: {light_card_bg}; color: {light_text_color}; }}
            </style>
        </head><body>
            <div style="text-align:center; padding: 20px;">
                <h1>🚍 Smart Bus Stop Dashboard</h1>
            </div>
            <div class="grid">
                <div class="card presence-box">
                    <h3>Occupancy Status</h3>
                    <div class="value">{"👤 PASSENGER" if presence else "📭 EMPTY"}</div>
                </div>
                <div class="card">
                    <h3>Temperature</h3>
                    <div class="value">{t}°C</div>
                </div>
                <div class="card">
                    <h3>Humidity</h3>
                    <div class="value">{h}%</div>
                </div>
                <div class="card">
                    <h3>Cooling Fan</h3>
                    <div class="value {"status-on" if fan_mode=="ON" else "status-off"}">{fan_mode}</div>
                </div>
                <div class="card light-card">
                    <h3>System Lighting</h3>
                    <div class="value">{"🌙 " if light_mode == "Night" else "☀️ "}{light_mode}</div>
                </div>
            </div>
            <div style="text-align:center; margin-top:30px; color:gray; font-size:0.8em;">
                Last Update: {db_time}
            </div>
        </body></html>
        """
        return html