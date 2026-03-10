import json
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

class StatsCollector:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.stats_file = Path("logs/stats.json")
        self._ensure_stats_file()
        self.history_file = Path("logs/history.json")
        self._ensure_history_file()
        
    def _ensure_stats_file(self):
        if not self.stats_file.exists():
            with open(self.stats_file, 'w') as f:
                json.dump({
                    "total_moves": 0,
                    "categories": {},
                    "file_types": {},
                    "daily_moves": {},
                    "hourly_activity": defaultdict(int),
                    "largest_file_moved": {"size": 0, "name": "", "category": ""},
                    "most_active_day": {"date": "", "count": 0}
                }, f, indent=2)
    
    def _ensure_history_file(self):
        if not self.history_file.exists():
            with open(self.history_file, 'w') as f:
                json.dump([], f)
    
    def record_move(self, filename, source, destination, category, file_size, file_type):
        timestamp = datetime.now().isoformat()
        
        # Record in history
        history_entry = {
            "timestamp": timestamp,
            "filename": filename,
            "source": str(source),
            "destination": str(destination),
            "category": category,
            "file_size": file_size,
            "file_type": file_type
        }
        
        self._add_to_history(history_entry)
        
        # Update statistics
        self._update_stats(history_entry)
        
        # Update database if available
        if self.db_manager:
            self._update_database(history_entry)
    
    def _add_to_history(self, entry):
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        except:
            history = []
        
        history.append(entry)
        
        # Keep only last 1000 entries to prevent file from growing too large
        if len(history) > 1000:
            history = history[-1000:]
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def _update_stats(self, entry):
        with open(self.stats_file, 'r') as f:
            stats = json.load(f)
        
        # Update total moves
        stats["total_moves"] += 1
        
        # Update category statistics
        category = entry["category"]
        if category not in stats["categories"]:
            stats["categories"][category] = {
                "count": 0,
                "total_size": 0,
                "last_moved": ""
            }
        
        stats["categories"][category]["count"] += 1
        stats["categories"][category]["total_size"] += entry["file_size"]
        stats["categories"][category]["last_moved"] = entry["timestamp"]
        
        # Update file type statistics
        file_type = entry["file_type"]
        if file_type not in stats["file_types"]:
            stats["file_types"][file_type] = 0
        stats["file_types"][file_type] += 1
        
        # Update daily moves
        date = entry["timestamp"][:10]  # YYYY-MM-DD
        if date not in stats["daily_moves"]:
            stats["daily_moves"][date] = 0
        stats["daily_moves"][date] += 1
        
        # Update hourly activity
        hour = int(entry["timestamp"][11:13])
        if "hourly_activity" not in stats:
            stats["hourly_activity"] = defaultdict(int)
        stats["hourly_activity"][str(hour)] += 1
        
        # Update largest file moved
        if entry["file_size"] > stats["largest_file_moved"]["size"]:
            stats["largest_file_moved"] = {
                "size": entry["file_size"],
                "name": entry["filename"],
                "category": entry["category"]
            }
        
        # Update most active day
        if stats["daily_moves"][date] > stats["most_active_day"]["count"]:
            stats["most_active_day"] = {
                "date": date,
                "count": stats["daily_moves"][date]
            }
        
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def _update_database(self, entry):
        if self.db_manager:
            try:
                self.db_manager.execute_query(
                    "INSERT INTO file_moves (timestamp, filename, source, destination, category, file_size, file_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (entry["timestamp"], entry["filename"], entry["source"], 
                     entry["destination"], entry["category"], entry["file_size"], entry["file_type"])
                )
            except Exception as e:
                print(f"Database error: {e}")
    
    def get_overview_stats(self):
        with open(self.stats_file, 'r') as f:
            stats = json.load(f)
        
        # Calculate some derived statistics
        total_size = sum(cat["total_size"] for cat in stats["categories"].values())
        
        # Get top categories
        categories_sorted = sorted(
            stats["categories"].items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        # Get recent activity (last 24 hours)
        cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()
        recent_count = 0
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                history = json.load(f)
                recent_count = len([h for h in history if h["timestamp"] > cutoff_time])
        
        return {
            "total_moves": stats["total_moves"],
            "total_categories": len(stats["categories"]),
            "total_file_types": len(stats["file_types"]),
            "total_size_moved": total_size,
            "top_categories": categories_sorted[:5],
            "most_active_day": stats.get("most_active_day", {"date": "", "count": 0}),
            "largest_file": stats.get("largest_file_moved", {"size": 0, "name": "", "category": ""}),
            "recent_24h_moves": recent_count,
            "hourly_activity": dict(stats.get("hourly_activity", {})),
            "daily_moves": stats.get("daily_moves", {})
        }
    
    def get_category_stats(self):
        with open(self.stats_file, 'r') as f:
            stats = json.load(f)
        
        categories = stats.get("categories", {})
        result = []
        
        for category, data in categories.items():
            avg_size = data["total_size"] / data["count"] if data["count"] > 0 else 0
            result.append({
                "category": category,
                "count": data["count"],
                "total_size": data["total_size"],
                "avg_size": avg_size,
                "last_moved": data["last_moved"],
                "percentage": (data["count"] / stats["total_moves"] * 100) if stats["total_moves"] > 0 else 0
            })
        
        return sorted(result, key=lambda x: x["count"], reverse=True)
    
    def get_recent_moves(self, limit=50):
        if not self.history_file.exists():
            return []
        
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        # Return most recent first
        return list(reversed(history[-limit:]))
    
    def get_time_series_data(self, days=7):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        
        with open(self.stats_file, 'r') as f:
            stats = json.load(f)
        
        daily_moves = stats.get("daily_moves", {})
        
        series_data = []
        for date in date_range:
            series_data.append({
                "date": date,
                "count": daily_moves.get(date, 0)
            })
        
        return series_data
    
    def clear_history(self):
        """Clear all history and reset statistics"""
        with open(self.history_file, 'w') as f:
            json.dump([], f)
        
        with open(self.stats_file, 'w') as f:
            json.dump({
                "total_moves": 0,
                "categories": {},
                "file_types": {},
                "daily_moves": {},
                "hourly_activity": defaultdict(int),
                "largest_file_moved": {"size": 0, "name": "", "category": ""},
                "most_active_day": {"date": "", "count": 0}
            }, f, indent=2)
        
        # Clear database if available
        if self.db_manager:
            try:
                self.db_manager.execute_query("DELETE FROM file_moves")
            except:
                pass
    
    def export_stats(self, export_format='json'):
        """Export statistics in specified format"""
        overview = self.get_overview_stats()
        categories = self.get_category_stats()
        recent = self.get_recent_moves(100)
        
        if export_format == 'json':
            return json.dumps({
                "overview": overview,
                "categories": categories,
                "recent_moves": recent,
                "exported_at": datetime.now().isoformat()
            }, indent=2)
        
        return None

# Singleton instance for easy access
stats_collector = None

def get_stats_collector(db_manager=None):
    global stats_collector
    if stats_collector is None:
        stats_collector = StatsCollector(db_manager)
    return stats_collector