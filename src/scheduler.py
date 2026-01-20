"""
Scheduler module for managing sync operations
"""
import schedule
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class SyncScheduler:
    """Manages scheduled sync operations with incremental update support"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize scheduler
        
        Args:
            config_path: Path to config directory for storing sync state
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or Path(__file__).parent.parent / "config"
        self.state_file = self.config_path / "sync_state.json"
        self.last_sync_timestamp = self._load_last_sync_timestamp()
    
    def _load_last_sync_timestamp(self) -> Optional[str]:
        """
        Load last sync timestamp from state file
        
        Returns:
            Last sync timestamp string or None
        """
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    timestamp = state.get('last_sync_timestamp')
                    self.logger.info(f"Loaded last sync timestamp: {timestamp}")
                    return timestamp
        except Exception as e:
            self.logger.warning(f"Could not load last sync timestamp: {e}")
        
        return None
    
    def save_last_sync_timestamp(self, timestamp: Optional[str] = None):
        """
        Save last sync timestamp to state file
        
        Args:
            timestamp: Timestamp string (ISO 8601 format). If None, uses current time.
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        try:
            state = {
                'last_sync_timestamp': timestamp,
                'last_sync_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            self.last_sync_timestamp = timestamp
            self.logger.info(f"Saved last sync timestamp: {timestamp}")
        except Exception as e:
            self.logger.error(f"Failed to save last sync timestamp: {e}")
    
    def get_since_date(self) -> Optional[str]:
        """
        Get date string for incremental sync (since last sync)
        
        Returns:
            ISO 8601 date string or None for full sync
        """
        if self.last_sync_timestamp:
            try:
                # Parse timestamp and return as ISO 8601
                dt = datetime.fromisoformat(self.last_sync_timestamp.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%dT%H:%M:%S')
            except:
                # If parsing fails, try to extract date part
                return self.last_sync_timestamp[:10] if len(self.last_sync_timestamp) >= 10 else None
        
        return None
    
    def is_full_sync(self) -> bool:
        """
        Check if this should be a full sync (no previous sync timestamp)
        
        Returns:
            True if full sync, False if incremental
        """
        return self.last_sync_timestamp is None
    
    def setup_schedule(self, frequency: str, time_str: str, sync_function):
        """
        Set up scheduled sync
        
        Args:
            frequency: Sync frequency ('daily', 'hourly', 'weekly')
            time_str: Time string (e.g., '02:00' for daily)
            sync_function: Function to call for sync
        """
        frequency = frequency.lower()
        
        if frequency == 'daily':
            schedule.every().day.at(time_str).do(sync_function)
            self.logger.info(f"Scheduled daily sync at {time_str}")
        elif frequency == 'hourly':
            # Extract minutes from time_str (format: HH:MM)
            minutes = time_str.split(':')[1] if ':' in time_str else '0'
            schedule.every().hour.at(f":{minutes}").do(sync_function)
            self.logger.info(f"Scheduled hourly sync at :{minutes}")
        elif frequency == 'weekly':
            # time_str should be day:time (e.g., 'monday:02:00')
            if ':' in time_str:
                parts = time_str.split(':')
                day = parts[0].lower()
                time_part = f"{parts[1]}:{parts[2]}" if len(parts) > 2 else parts[1]
                
                day_map = {
                    'monday': schedule.every().monday,
                    'tuesday': schedule.every().tuesday,
                    'wednesday': schedule.every().wednesday,
                    'thursday': schedule.every().thursday,
                    'friday': schedule.every().friday,
                    'saturday': schedule.every().saturday,
                    'sunday': schedule.every().sunday
                }
                
                if day in day_map:
                    day_map[day].at(time_part).do(sync_function)
                    self.logger.info(f"Scheduled weekly sync on {day} at {time_part}")
                else:
                    raise ValueError(f"Invalid day: {day}")
            else:
                raise ValueError("Weekly schedule requires format: 'day:HH:MM'")
        else:
            raise ValueError(f"Unknown frequency: {frequency}")
    
    def run_pending(self):
        """Run pending scheduled tasks"""
        schedule.run_pending()
    
    def clear_schedule(self):
        """Clear all scheduled tasks"""
        schedule.clear()
        self.logger.info("Cleared all scheduled tasks")

