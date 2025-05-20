import pytest
from app_new import app
from datetime import datetime, timedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def send_swaig_payload(client, function_name, args):
    payload = {"function": function_name, "arguments": args}
    return client.post('/swaig', json=payload)

def test_create_reservation(client):
    date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    args = {
        "name": "John Doe",
        "party_size": 4,
        "date": date_str,
        "time": "19:00",
        "phone_number": "+19185551234"
    }
    response = send_swaig_payload(client, "create_reservation", args)
    data = response.get_json()
    assert data and (data.get('success') or data.get('response'))

def test_get_reservation(client):
    date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    # Create reservation first
    args = {
        "name": "Jane Smith",
        "party_size": 2,
        "date": date_str,
        "time": "20:00",
        "phone_number": "+19185551235"
    }
    send_swaig_payload(client, "create_reservation", args)
    # Now try to get
    get_args = {"phone_number": "+19185551235"}
    response = send_swaig_payload(client, "get_reservation", get_args)
    data = response.get_json()
    assert data and (data.get('success') or data.get('response'))

def test_update_reservation(client):
    date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    # Create reservation first
    args = {
        "name": "Bob Wilson",
        "party_size": 3,
        "date": date_str,
        "time": "18:30",
        "phone_number": "+19185551236"
    }
    send_swaig_payload(client, "create_reservation", args)
    # Now try to update
    update_args = {
        "phone_number": "+19185551236",
        "party_size": 4,
        "time": "19:00"
    }
    response = send_swaig_payload(client, "update_reservation", update_args)
    data = response.get_json()
    assert data and (data.get('success') or data.get('response'))

def test_cancel_reservation(client):
    date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    # Create reservation first
    args = {
        "name": "Alice Brown",
        "party_size": 2,
        "date": date_str,
        "time": "21:00",
        "phone_number": "+19185551237"
    }
    send_swaig_payload(client, "create_reservation", args)
    # Now try to cancel
    cancel_args = {"phone_number": "+19185551237"}
    response = send_swaig_payload(client, "cancel_reservation", cancel_args)
    data = response.get_json()
    assert data and (data.get('success') or data.get('response')) 