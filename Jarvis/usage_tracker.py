"""
API Usage Tracker for Jarvis
============================
Tracks and persists API usage data.
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional

class UsageTracker:
    """Tracks API usage stats."""
    
    def __init__(self, storage_file: str = "jarvis_usage.json"):
        self.storage_file = storage_file
        self.usage_data = self._load_data()
        
    def _load_data(self) -> Dict:
        """Load usage data from file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return self._init_data()
        return self._init_data()
    
    def _init_data(self) -> Dict:
        """Initialize empty data structure."""
        return {
            "total_calls": 0,
            "total_tokens": 0,  # Estimated or tracked if available
            "models": {},
            "history": []
        }
    
    def _save_data(self):
        """Save usage data to file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            print(f"Error saving usage data: {e}")

    def increment_usage(self, model: str, tokens: int = 0):
        """Record a new API call."""
        self.usage_data["total_calls"] += 1
        self.usage_data["total_tokens"] += tokens
        
        # Update model specific stats
        if model not in self.usage_data["models"]:
            self.usage_data["models"][model] = {"calls": 0, "tokens": 0}
        
        self.usage_data["models"][model]["calls"] += 1
        self.usage_data["models"][model]["tokens"] += tokens
        
        # Add to history (keep last 100 entries)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "tokens": tokens
        }
        self.usage_data["history"].append(entry)
        if len(self.usage_data["history"]) > 100:
            self.usage_data["history"] = self.usage_data["history"][-100:]
            
        self._save_data()
        
    def get_usage_summary(self) -> Dict:
        """Get summary of usage."""
        return {
            "total_calls": self.usage_data["total_calls"],
            "total_tokens": self.usage_data.get("total_tokens", 0),
            "models": self.usage_data["models"]
        }
