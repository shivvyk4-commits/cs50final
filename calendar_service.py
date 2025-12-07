import os
import logging
import requests
from datetime import datetime, timedelta

connection_settings = None


def get_access_token():
    global connection_settings
    
    if connection_settings and connection_settings.get('settings', {}).get('expires_at'):
        expires_at = connection_settings['settings']['expires_at']
        if datetime.fromisoformat(expires_at.replace('Z', '+00:00')) > datetime.now():
            return connection_settings['settings'].get('access_token')
    
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
    
    if repl_identity:
        x_replit_token = f'repl {repl_identity}'
    elif web_repl_renewal:
        x_replit_token = f'depl {web_repl_renewal}'
    else:
        logging.warning("No Replit token available for calendar connection")
        return None
    
    try:
        response = requests.get(
            f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-calendar',
            headers={
                'Accept': 'application/json',
                'X_REPLIT_TOKEN': x_replit_token
            }
        )
        data = response.json()
        connection_settings = data.get('items', [{}])[0] if data.get('items') else {}
        
        access_token = (connection_settings.get('settings', {}).get('access_token') or 
                       connection_settings.get('settings', {}).get('oauth', {}).get('credentials', {}).get('access_token'))
        
        if not access_token:
            logging.warning("Google Calendar not connected")
            return None
            
        return access_token
    except Exception as e:
        logging.error(f"Error getting calendar access token: {e}")
        return None


def get_calendar_events(time_min=None, time_max=None):
    access_token = get_access_token()
    if not access_token:
        return []
    
    if time_min is None:
        time_min = datetime.utcnow()
    if time_max is None:
        time_max = time_min + timedelta(days=7)
    
    try:
        response = requests.get(
            'https://www.googleapis.com/calendar/v3/calendars/primary/events',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            },
            params={
                'timeMin': time_min.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'singleEvents': True,
                'orderBy': 'startTime'
            }
        )
        data = response.json()
        return data.get('items', [])
    except Exception as e:
        logging.error(f"Error fetching calendar events: {e}")
        return []


def find_available_slot(duration_minutes=30, preferred_hour=None):
    access_token = get_access_token()
    if not access_token:
        return None
    
    now = datetime.utcnow()
    end_search = now + timedelta(days=7)
    
    events = get_calendar_events(now, end_search)
    
    busy_times = []
    for event in events:
        start = event.get('start', {})
        end = event.get('end', {})
        
        start_time = start.get('dateTime') or start.get('date')
        end_time = end.get('dateTime') or end.get('date')
        
        if start_time and end_time:
            try:
                if 'T' in start_time:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    busy_times.append((start_dt.replace(tzinfo=None), end_dt.replace(tzinfo=None)))
            except:
                pass
    
    current = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    
    while current < end_search:
        hour = current.hour
        
        if 6 <= hour <= 22:
            if preferred_hour is not None and hour != preferred_hour:
                current += timedelta(hours=1)
                continue
            
            slot_end = current + timedelta(minutes=duration_minutes)
            
            is_available = True
            for busy_start, busy_end in busy_times:
                if not (slot_end <= busy_start or current >= busy_end):
                    is_available = False
                    break
            
            if is_available:
                return current
        
        current += timedelta(hours=1)
    
    return None


def create_calendar_event(title, start_time, duration_minutes=30, description=""):
    access_token = get_access_token()
    if not access_token:
        return None
    
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC'
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC'
        }
    }
    
    try:
        response = requests.post(
            'https://www.googleapis.com/calendar/v3/calendars/primary/events',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            json=event
        )
        data = response.json()
        return data.get('id')
    except Exception as e:
        logging.error(f"Error creating calendar event: {e}")
        return None


def is_calendar_connected():
    return get_access_token() is not None


def update_calendar_event(event_id, title=None, start_time=None, duration_minutes=None, description=None):
    access_token = get_access_token()
    if not access_token or not event_id:
        return False
    
    try:
        response = requests.get(
            f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
        )
        
        if response.status_code != 200:
            logging.error(f"Failed to get event for update: {response.status_code}")
            return False
        
        existing_event = response.json()
        
        if title:
            existing_event['summary'] = title
        if description:
            existing_event['description'] = description
        if start_time:
            end_time = start_time + timedelta(minutes=duration_minutes or 30)
            existing_event['start'] = {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC'
            }
            existing_event['end'] = {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC'
            }
        
        update_response = requests.put(
            f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            json=existing_event
        )
        
        if update_response.status_code == 200:
            return True
        else:
            logging.error(f"Failed to update event: {update_response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"Error updating calendar event: {e}")
        return False


def delete_calendar_event(event_id):
    access_token = get_access_token()
    if not access_token or not event_id:
        return False
    
    try:
        response = requests.delete(
            f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}',
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )
        
        if response.status_code in [200, 204]:
            return True
        else:
            logging.error(f"Failed to delete event: {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"Error deleting calendar event: {e}")
        return False
