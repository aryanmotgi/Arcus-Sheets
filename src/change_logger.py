"""
Change Logger - Tracks all changes made to Google Sheets for undo/revert functionality
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ChangeLogger:
    """Logs and manages changes to Google Sheets"""
    
    def __init__(self, log_file: str = 'config/sheet_changes.json'):
        """Initialize change logger"""
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def log_change(self, change_type: str, description: str, details: Dict[str, Any]) -> str:
        """
        Log a change to the sheet
        
        Args:
            change_type: Type of change (formula_update, column_move, format, etc.)
            description: Human-readable description
            details: Change details (formulas, ranges, values, etc.)
        
        Returns:
            Change ID for later reference
        """
        change_id = f"change_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        change_entry = {
            'id': change_id,
            'timestamp': datetime.now().isoformat(),
            'type': change_type,
            'description': description,
            'details': details,
            'reverted': False
        }
        
        # Load existing changes
        changes = self.load_changes()
        
        # Add new change
        changes.append(change_entry)
        
        # Keep only last 100 changes
        if len(changes) > 100:
            changes = changes[-100:]
        
        # Save changes
        self.save_changes(changes)
        
        self.logger.info(f"Logged change: {change_id} - {description}")
        return change_id
    
    def load_changes(self) -> List[Dict[str, Any]]:
        """Load all changes from log file"""
        if not self.log_file.exists():
            return []
        
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading changes: {e}")
            return []
    
    def save_changes(self, changes: List[Dict[str, Any]]):
        """Save changes to log file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(changes, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving changes: {e}")
    
    def get_recent_changes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent changes"""
        changes = self.load_changes()
        return [c for c in changes if not c.get('reverted', False)][-limit:]
    
    def get_change_by_id(self, change_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific change by ID"""
        changes = self.load_changes()
        for change in changes:
            if change['id'] == change_id:
                return change
        return None
    
    def mark_reverted(self, change_id: str):
        """Mark a change as reverted"""
        changes = self.load_changes()
        for change in changes:
            if change['id'] == change_id:
                change['reverted'] = True
                change['reverted_at'] = datetime.now().isoformat()
                break
        self.save_changes(changes)
    
    def get_change_history(self) -> List[Dict[str, Any]]:
        """Get full change history"""
        return self.load_changes()
    
    def clear_history(self):
        """Clear all change history"""
        self.save_changes([])
        self.logger.info("Change history cleared")
