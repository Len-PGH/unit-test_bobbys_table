from flask import Flask, jsonify, request, abort
from dotenv import load_dotenv
import logging
import os
from signalwire_swaig.swaig import SWAIG, SWAIGArgument
import secrets
import base64
import json
import io
import inspect

from reservation_system import (
    create_reservation_response,
    get_reservation_response,
    update_reservation_response,
    cancel_reservation_response,
    move_reservation_response,
    reservations
)
import random
from swaig_handler import transform_swaig_request

def validate_environment():
    required_vars = ['HTTP_USERNAME', 'HTTP_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Validate PORT if present
    port = os.getenv('PORT')
    if port and not port.isdigit():
        raise ValueError("PORT environment variable must be a number")

logging.getLogger('werkzeug').setLevel(logging.WARNING)

if os.environ.get('DEBUG'):
    print("Debug mode is enabled")
    # Use secrets module for cryptographically secure random numbers
    debug_pin = f"{secrets.randbelow(900) + 100}-{secrets.randbelow(900) + 100}-{secrets.randbelow(900) + 100}"
    os.environ['WERKZEUG_DEBUG_PIN'] = debug_pin
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    print(f"Debugger PIN: {debug_pin}")

load_dotenv()
validate_environment()

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.static_folder = os.path.abspath('static')
swaig = SWAIG(
    app,
    auth=(os.getenv('HTTP_USERNAME'), os.getenv('HTTP_PASSWORD'))
)

auth_str = "admin:secret"
b64_auth = base64.b64encode(auth_str.encode()).decode()
print(b64_auth)  # Use this in the header

headers={"Authorization": "Basic YWRtaW46c2VjcmV0"}

@swaig.endpoint(
    description="Create a new reservation for a customer",
    name=SWAIGArgument(type="string", description="The name of the person making the reservation", required=True),
    party_size=SWAIGArgument(type="integer", description="Number of people in the party", required=True),
    date=SWAIGArgument(type="string", description="Date of reservation in YYYY-MM-DD format", required=True),
    time=SWAIGArgument(type="string", description="Time of reservation in HH:MM format (24-hour)", required=True),
    phone_number=SWAIGArgument(type="string", description="Contact phone number in E.164 format (e.g., +19185551234)", required=True)
)
def create_reservation(name, party_size, date, time, phone_number, **kwargs):
    with open('swaig_debug_payload.json', 'a') as f:
        f.write(f'CREATE_RESERVATION_ARGS: name={name}, party_size={party_size}, date={date}, time={time}, phone_number={phone_number}, kwargs={kwargs}\n')
    return create_reservation_response({
        "name": name,
        "party_size": party_size,
        "date": date,
        "time": time,
        "phone_number": phone_number
    })

@swaig.endpoint(
    description="Retrieve an existing reservation",
    phone_number=SWAIGArgument(type="string", description="Phone number used for the reservation in E.164 format", required=True)
)
def get_reservation(phone_number, **kwargs):
    return get_reservation_response({"phone_number": phone_number})

@swaig.endpoint(
    description="Update an existing reservation",
    phone_number=SWAIGArgument(type="string", description="Phone number of the existing reservation", required=True),
    name=SWAIGArgument(type="string", description="Updated name (optional)", required=False),
    party_size=SWAIGArgument(type="integer", description="Updated party size (optional)", required=False),
    date=SWAIGArgument(type="string", description="Updated date in YYYY-MM-DD format (optional)", required=False),
    time=SWAIGArgument(type="string", description="Updated time in HH:MM format (optional)", required=False)
)
def update_reservation(phone_number, name=None, party_size=None, date=None, time=None, **kwargs):
    current_reservation = reservations.get(phone_number, {})
    updated_reservation = {
        "name": name if name else current_reservation.get("name"),
        "party_size": int(party_size) if party_size else current_reservation.get("party_size"),
        "date": date if date else current_reservation.get("date"),
        "time": time if time else current_reservation.get("time")
    }
    return update_reservation_response(updated_reservation)

@swaig.endpoint(
    description="Cancel an existing reservation",
    phone_number=SWAIGArgument(type="string", description="Phone number of the reservation to cancel", required=True)
)
def cancel_reservation(phone_number, **kwargs):
    return cancel_reservation_response({"phone_number": phone_number})

@swaig.endpoint(
    description="Move an existing reservation to a new date and time",
    phone_number=SWAIGArgument(type="string", description="Phone number of the existing reservation", required=True),
    new_date=SWAIGArgument(type="string", description="New date in YYYY-MM-DD format", required=True),
    new_time=SWAIGArgument(type="string", description="New time in HH:MM format", required=True)
)
def move_reservation(phone_number, new_date, new_time, **kwargs):
    return move_reservation_response({
        "phone_number": phone_number,
        "new_date": new_date,
        "new_time": new_time
    })

def scramble_phone_number(phone):
    if not phone or len(phone) < 6:
        return phone
    return phone[:-6] + ''.join(random.choices('0123456789', k=6))

def get_reservations_table_html():
    if not reservations:
        return "<p>No reservations yet.</p>"
    
    table_html = """
    <table border="1">
        <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Date</th>
            <th>Time</th>
            <th>Party Size</th>
        </tr>
    """
    
    for phone, details in reservations.items():
        scrambled = scramble_phone_number(phone)
        table_html += f"""
        <tr>
            <td>{details['name']}</td>
            <td>{scrambled}</td>
            <td>{details['date']}</td>
            <td>{details['time']}</td>
            <td>{details['party_size']}</td>
        </tr>
        """
    
    table_html += "</table>"
    return table_html

@app.route('/swaig', methods=['GET'])
@app.route('/', methods=['GET'])
def serve_reservation_html():
    try:
        static_file_path = os.path.join(app.static_folder, 'reservation.html')
        if not os.path.exists(static_file_path):
            return jsonify({
                "error": "Reservation page template not found",
                "details": "The reservation.html file is missing from the static folder"
            }), 500
            
        with open(static_file_path, 'r') as file:
            html_content = file.read()
        
        reservations_table = get_reservations_table_html()
        
        # Replace placeholders with actual data
        html_content = html_content.replace("{{reservations_table}}", reservations_table)
        
        # Insert Google Tag Manager script if the tag is available
        GOOGLE_TAG = os.getenv("GOOGLE_TAG")
        if GOOGLE_TAG:
            gtm_script = f"""
            <script async src="https://www.googletagmanager.com/gtag/js?id={GOOGLE_TAG}"></script>
            <script>
              window.dataLayer = window.dataLayer || [];
              function gtag(){{dataLayer.push(arguments);}}
              gtag('js', new Date());
              gtag('config', '{GOOGLE_TAG}');
            </script>
            """
            html_content = html_content.replace("</head>", f"{gtm_script}</head>")
        
        return html_content
    except Exception as e:
        return jsonify({
            "error": "Failed to serve HTML",
            "details": str(e)
        }), 500

@app.route('/swaig', methods=['POST'])
def swaig_dispatch():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    function_name = data.get('function')
    arguments = data.get('arguments', None)
    argument_parsed = None
    if 'argument' in data and 'parsed' in data['argument']:
        argument_parsed = data['argument']['parsed'][0]
    if not function_name:
        return jsonify({"error": "Missing 'function' in request"}), 400
    # Debug: print all available endpoints and arguments
    with open('swaig_debug_payload.json', 'a') as f:
        f.write(f"DISPATCH: Looking for function '{function_name}'\n")
        f.write(f"DISPATCH: Available endpoints: {list(app.view_functions.keys())}\n")
        f.write(f"DISPATCH: Arguments: {arguments}\n")
        f.write(f"DISPATCH: Argument parsed: {argument_parsed}\n")
    func = globals().get(function_name)
    if not func:
        func = app.view_functions.get(function_name)
    if func:
        func = inspect.unwrap(func)
    with open('swaig_debug_payload.json', 'a') as f:
        f.write(f"DISPATCH: func object: {func}\n")
        if func:
            f.write(f"DISPATCH: func signature: {inspect.signature(func)}\n")
    if not func:
        with open('swaig_debug_payload.json', 'a') as f:
            f.write(f"DISPATCH: Function '{function_name}' not found!\n")
        return jsonify({"error": f"Function '{function_name}' not found"}), 404
    try:
        if arguments is not None:
            result = func(**arguments)
        elif argument_parsed is not None:
            result = func(**argument_parsed)
        else:
            result = func()
        with open('swaig_debug_payload.json', 'a') as f:
            f.write(f"DISPATCH: Result: {result}\n")
        if isinstance(result, dict):
            return jsonify(result)
        else:
            return jsonify({"response": result})
    except Exception as e:
        with open('swaig_debug_payload.json', 'a') as f:
            f.write(f"DISPATCH: Exception: {str(e)}\n")
        return jsonify({"response": f"Invalid arguments for function '{function_name}': {e}"})

# Register our custom /swaig POST route last, forcibly overwriting any previous handler
app.add_url_rule('/swaig', view_func=swaig_dispatch, methods=['POST'], endpoint='swaig_dispatch')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5001), debug=os.getenv("DEBUG")) 