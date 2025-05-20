import uuid
from datetime import datetime
from typing import Dict, Optional
import re

# Mock reservation data storage
reservations: Dict[str, dict] = {}

def validate_phone_number(phone: str) -> bool:
    """Validate phone number in E.164 format."""
    pattern = r'^\+[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone))

def validate_date_time(date_str: str, time_str: str) -> bool:
    try:
        # Parse the date and time
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        # Check if date is in the past
        if dt < datetime.now():
            return False
            
        # Check if time is within business hours (14:00-22:00)
        hour = dt.hour
        if hour < 14 or hour >= 22:
            return False
            
        return True
    except ValueError:
        return False

def validate_party_size(party_size: int) -> bool:
    """Validate party size is within reasonable limits."""
    return 1 <= party_size <= 20  # Maximum party size of 20

def create_reservation_response(data: dict) -> str:
    try:
        name = data["name"]
        party_size = int(data["party_size"])
        date = data["date"]
        time = data["time"]
        phone_number = data["phone_number"]

        if not validate_phone_number(phone_number):
            return "Invalid phone number format. Please use E.164 format (e.g., +19185551234)."

        if not validate_party_size(party_size):
            return "Party size must be between 1 and 20 people."

        if not validate_date_time(date, time):
            return "Invalid date or time. Reservations must be for future dates during business hours (14:00-22:00)."

        if phone_number in reservations:
            return "A reservation already exists for this phone number."

        # Check for overlapping reservations
        for existing_res in reservations.values():
            if existing_res["date"] == date and existing_res["time"] == time:
                return "This time slot is already booked. Please choose a different time."

        reservations[phone_number] = {
            "name": name,
            "party_size": party_size,
            "date": date,
            "time": time
        }

        return "Reservation successfully created."

    except KeyError as e:
        return f"Missing required field: {str(e)}"
    except Exception as e:
        return f"Error creating reservation: {str(e)}"

def get_reservation_response(data: dict) -> str:
    try:
        phone_number = data["phone_number"]
        
        if not validate_phone_number(phone_number):
            return "Invalid phone number format. Please use E.164 format (e.g., +19185551234)."

        reservation = reservations.get(phone_number)
        if reservation:
            return f"Reservation found: {reservation['name']} for {reservation['party_size']} people on {reservation['date']} at {reservation['time']}. Contact: {phone_number}"
        return "No reservation found for this phone number."

    except KeyError:
        return "Phone number is required."
    except Exception as e:
        return f"Error retrieving reservation: {str(e)}"

def update_reservation_response(data: dict) -> str:
    try:
        phone_number = data["phone_number"]
        
        if not validate_phone_number(phone_number):
            return "Invalid phone number format. Please use E.164 format (e.g., +19185551234)."

        if phone_number not in reservations:
            return "No reservation found for this phone number."

        current_reservation = reservations[phone_number]
        
        if "date" in data and "time" in data:
            if not validate_date_time(data["date"], data["time"]):
                return "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."

        if "party_size" in data and int(data["party_size"]) < 1:
            return "Party size must be at least 1 person."

        updated_reservation = {
            "name": data.get("name", current_reservation["name"]),
            "party_size": int(data.get("party_size", current_reservation["party_size"])),
            "date": data.get("date", current_reservation["date"]),
            "time": data.get("time", current_reservation["time"])
        }

        reservations[phone_number] = updated_reservation
        return f"Reservation updated: {updated_reservation['name']} for {updated_reservation['party_size']} people on {updated_reservation['date']} at {updated_reservation['time']}. Contact: {phone_number}"

    except KeyError:
        return "Phone number is required."
    except Exception as e:
        return f"Error updating reservation: {str(e)}"

def cancel_reservation_response(data: dict) -> str:
    try:
        phone_number = data["phone_number"]
        
        if not validate_phone_number(phone_number):
            return "Invalid phone number format. Please use E.164 format (e.g., +19185551234)."

        if phone_number in reservations:
            reservation = reservations[phone_number]
            del reservations[phone_number]
            return "Reservation canceled successfully."
        return "No reservation found for this phone number."

    except KeyError:
        return "Phone number is required."
    except Exception as e:
        return f"Error canceling reservation: {str(e)}"

def move_reservation_response(data: dict) -> str:
    try:
        phone_number = data["phone_number"]
        new_date = data["new_date"]
        new_time = data["new_time"]
        
        if not validate_phone_number(phone_number):
            return "Invalid phone number format. Please use E.164 format (e.g., +19185551234)."

        if not validate_date_time(new_date, new_time):
            return "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."

        if phone_number in reservations:
            reservation = reservations[phone_number]
            old_date = reservation["date"]
            old_time = reservation["time"]
            
            reservation["date"] = new_date
            reservation["time"] = new_time
            
            return "Reservation moved successfully."
        return "No reservation found for this phone number."

    except KeyError as e:
        return f"Missing required field: {str(e)}"
    except Exception as e:
        return f"Error moving reservation: {str(e)}" 