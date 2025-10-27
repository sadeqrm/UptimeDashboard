from flask import Flask, render_template, jsonify
from flask_caching import Cache
import requests
from datetime import datetime, timedelta
import os
import time

app = Flask(__name__)

# Configure caching
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# UptimeRobot API endpoint
API_URL = "https://api.uptimerobot.com/v3/monitors"
API_KEY = os.getenv('UPTIMEROBOT_API_KEY', 'uur2774746-bf6e7863549xxxxxxxxx')

@cache.cached(timeout=60)
def get_monitors():
    """Fetch all monitors from UptimeRobot"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            app.logger.info(f"Fetching monitors from UptimeRobot (attempt {attempt + 1}/{max_retries})...")
            
            # Make API request to new v3 endpoint
            headers = {
                'accept': 'application/json',
                'authorization': f'Bearer {API_KEY}',
            }

            response = requests.get(
                API_URL,
                headers=headers,
                timeout=90
            )
            response.raise_for_status()
            result = response.json()
            
            app.logger.info(f"API response status: {result.get('stat')}")
            
            if result.get('stat') == 'ok':
                app.logger.info(f"Successfully fetched {len(result.get('monitors', []))} monitors")
                return result
            else:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                app.logger.error(f"API error: {error_msg}")
                return None
                
        except requests.exceptions.Timeout as e:
            app.logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                app.logger.error("Max retries reached for timeout")
                return None
                
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Request error: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return None
                
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            return None
    
    return None

def parse_monitor_data(monitors_json):
    """Parse monitor data and calculate statistics"""
    if not monitors_json or 'monitors' not in monitors_json:
        app.logger.error("No monitors found in API response")
        return []
    
    monitors = []
    for monitor in monitors_json['monitors']:
        try:
            # Status color based on monitor status
            status_map = {0: 'Paused', 1: 'Not Checked Yet', 2: 'Up', 8: 'Seems Down', 9: 'Down'}
            status_name = status_map.get(monitor.get('status'), 'Unknown')
            
            # Get response time
            response_time = 'N/A'
            if monitor.get('response_times'):
                response_times = monitor['response_times']
                if response_times and len(response_times) > 0:
                    latest_response = response_times[0].get('value', 'N/A')
                    if latest_response != 'N/A' and isinstance(latest_response, (int, float)):
                        response_time = int(latest_response)
                    else:
                        response_time = 'N/A'
            
            # Try to get from the monitor's average response time if available
            if response_time == 'N/A' and monitor.get('average_response_time'):
                avg_time = monitor.get('average_response_time')
                if isinstance(avg_time, (int, float)):
                    response_time = int(avg_time)
            
            # Get URL
            url = monitor.get('url', 'N/A')
            if url == '':
                url = monitor.get('host', 'N/A')
            
            # Get location/server info
            # UptimeRobot monitors from different servers around the world
            # Check for monitoring server location data
            location_info = 'Global Monitoring'
            
            # Try to get location from various possible fields
            if monitor.get('monitor_server_location'):
                location_info = monitor.get('monitor_server_location')
            elif monitor.get('location'):
                loc = monitor.get('location')
                if isinstance(loc, dict):
                    if loc.get('country'):
                        country = loc.get('country')
                        if isinstance(country, dict):
                            location_info = country.get('name', 'Global')
                        else:
                            location_info = str(country)
                    else:
                        location_info = str(loc)
                else:
                    location_info = str(loc)
            elif monitor.get('country'):
                location_info = str(monitor.get('country'))
            
            monitor_data = {
                'id': monitor['id'],
                'name': monitor['friendly_name'],
                'url': url,
                'type': 'HTTP' if monitor['type'] == 1 else 'Keyword' if monitor['type'] == 2 else 'Ping' if monitor['type'] == 3 else 'Port',
                'status': status_name,
                'status_code': monitor.get('status'),
                'response_time': response_time,
                'location': location_info
            }
            
            monitors.append(monitor_data)
        except Exception as e:
            app.logger.error(f"Error parsing monitor {monitor.get('id', 'unknown')}: {e}")
            continue
    
    return monitors

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/test')
def test_api():
    """Test endpoint to check API connection"""
    try:
        result = get_monitors()
        if result:
            return jsonify({
                'status': 'success',
                'monitors_count': len(result.get('monitors', [])),
                'api_response': result.get('stat'),
                'message': 'Successfully connected to UptimeRobot API'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to connect to UptimeRobot API'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/monitors')
def monitors_api():
    """API endpoint to get monitors data"""
    try:
        monitors_data = get_monitors()
        
        if not monitors_data:
            app.logger.error("Failed to fetch monitors from API")
            return jsonify({
                'error': 'Failed to fetch monitors from UptimeRobot API. The API request timed out. Please try again in a moment.',
                'cached': False
            }), 500
        
        app.logger.info(f"Successfully fetched monitors data")
        parsed_monitors = parse_monitor_data(monitors_data)
        
        return jsonify({
            'monitors': parsed_monitors,
            'total': len(parsed_monitors),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        app.logger.error(f"Error in monitors_api: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=True)

