from flask import Flask, render_template, jsonify, request, abort
import logging
from datetime import datetime
from pathlib import Path
import json
import sys
import os

# Add project root to path for module imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from models.stats import StatsManager
    from database.db_manager import DatabaseManager
    from config.settings import WEB_INTERFACE_CONFIG, LOGS_CONFIG
except ImportError:
    # Fallback to mock implementations if modules aren't available
    class StatsManager:
        def __init__(self):
            self.categories = {}
            
        def get_statistics(self):
            return {
                'total_files': 0,
                'by_category': {},
                'by_date': {},
                'recent_activity': []
            }
    
    class DatabaseManager:
        def __init__(self):
            pass
            
        def get_recent_moves(self, limit=100):
            return []
            
        def get_category_stats(self):
            return {}
            
        def get_daily_stats(self, days=30):
            return {}

    WEB_INTERFACE_CONFIG = {
        'host': 'localhost',
        'port': 8080,
        'debug': True,
        'refresh_interval': 5000
    }
    
    LOGS_CONFIG = {
        'organizer_log': 'logs/organizer.log',
        'webserver_log': 'logs/webserver.log'
    }

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_CONFIG['webserver_log']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize managers
stats_manager = StatsManager()
db_manager = DatabaseManager()

def parse_log_line(line):
    """Parse a single log line to extract information."""
    try:
        # Format: [2024-01-01 12:00:00] [INFO] Moved file.ext from /path/to/src to /path/to/dest
        if 'Moved' not in line:
            return None
            
        parts = line.split(' ')
        if len(parts) < 9:
            return None
            
        timestamp = f"{parts[0][1:]} {parts[1][:-1]}"
        filename = parts[3]
        src_path = parts[5]
        dest_path = parts[8]
        
        # Extract category from destination path
        category = Path(dest_path).parent.name
        
        return {
            'timestamp': timestamp,
            'filename': filename,
            'src_path': src_path,
            'dest_path': dest_path,
            'category': category
        }
    except Exception as e:
        logger.error(f"Error parsing log line: {e}")
        return None

def read_organizer_log(limit=100):
    """Read organizer log file and parse recent moves."""
    log_entries = []
    log_file = LOGS_CONFIG['organizer_log']
    
    if not os.path.exists(log_file):
        return log_entries
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Read lines in reverse (newest first) and parse
        for line in reversed(lines[-limit*2:]):  # Read extra lines to account for non-move entries
            parsed = parse_log_line(line.strip())
            if parsed:
                log_entries.append(parsed)
                if len(log_entries) >= limit:
                    break
                    
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
    
    return log_entries

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template(
        'index.html',
        refresh_interval=WEB_INTERFACE_CONFIG['refresh_interval']
    )

@app.route('/stats')
def stats():
    """Render the statistics page."""
    return render_template('stats.html')

@app.route('/history')
def history():
    """Render the history page."""
    return render_template('history.html')

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint for dashboard data."""
    try:
        stats_data = stats_manager.get_statistics()
        
        # Ensure all required keys exist
        dashboard_data = {
            'total_files': stats_data.get('total_files', 0),
            'categories': stats_data.get('by_category', {}),
            'daily_stats': stats_data.get('by_date', {}),
            'recent_activity': stats_data.get('recent_activity', [])[:10]
        }
        
        return jsonify(dashboard_data)
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({
            'total_files': 0,
            'categories': {},
            'daily_stats': {},
            'recent_activity': []
        })

@app.route('/api/stats')
def api_stats():
    """API endpoint for detailed statistics."""
    try:
        # Try to get stats from database first
        category_stats = db_manager.get_category_stats()
        daily_stats = db_manager.get_daily_stats(days=30)
        
        # Fallback to log parsing if database is empty
        if not category_stats:
            log_entries = read_organizer_log(limit=1000)
            category_counts = {}
            
            for entry in log_entries:
                category = entry['category']
                category_counts[category] = category_counts.get(category, 0) + 1
            
            category_stats = category_counts
        
        # Prepare response
        stats_data = {
            'categories': category_stats,
            'daily': daily_stats,
            'top_categories': sorted(
                category_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
        
        return jsonify(stats_data)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'categories': {},
            'daily': {},
            'top_categories': []
        })

@app.route('/api/history')
def api_history():
    """API endpoint for file move history."""
    try:
        # Try to get history from database
        recent_moves = db_manager.get_recent_moves(limit=50)
        
        # Fallback to log parsing if database returns empty
        if not recent_moves:
            recent_moves = read_organizer_log(limit=50)
        
        return jsonify({
            'history': recent_moves,
            'count': len(recent_moves)
        })
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({
            'history': [],
            'count': 0
        })

@app.route('/api/status')
def api_status():
    """API endpoint for service status."""
    try:
        # Check if organizer log is being written to
        log_file = LOGS_CONFIG['organizer_log']
        is_active = False
        
        if os.path.exists(log_file):
            # Check if log has been modified in the last 5 minutes
            mod_time = os.path.getmtime(log_file)
            time_diff = datetime.now().timestamp() - mod_time
            is_active = time_diff < 300  # 5 minutes
        
        return jsonify({
            'status': 'active' if is_active else 'inactive',
            'last_update': datetime.fromtimestamp(os.path.getmtime(log_file)).isoformat() if os.path.exists(log_file) else None,
            'log_file': log_file,
            'webserver': 'running',
            'uptime': 'N/A'
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'status': 'unknown',
            'last_update': None,
            'log_file': LOGS_CONFIG['organizer_log'],
            'webserver': 'running',
            'uptime': 'N/A'
        })

@app.route('/api/settings')
def api_settings():
    """API endpoint for current settings."""
    try:
        # Read config.json
        config_path = Path(__file__).parent / 'config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        return jsonify({
            'watch_path': config.get('watch_path', 'Downloads'),
            'rules': config.get('rules', {}),
            'web_interface': WEB_INTERFACE_CONFIG
        })
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({
            'watch_path': 'Unknown',
            'rules': {},
            'web_interface': WEB_INTERFACE_CONFIG
        })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting web interface on {WEB_INTERFACE_CONFIG['host']}:{WEB_INTERFACE_CONFIG['port']}")
    app.run(
        host=WEB_INTERFACE_CONFIG['host'],
        port=WEB_INTERFACE_CONFIG['port'],
        debug=WEB_INTERFACE_CONFIG['debug']
    )