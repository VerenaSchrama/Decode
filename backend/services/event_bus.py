#!/usr/bin/env python3
"""
Simple Event Bus for Intervention Completion Events
In-memory event bus for decoupled event handling
"""

from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
import logging
import traceback

logger = logging.getLogger(__name__)

class EventBus:
    """Simple in-memory event bus for pub/sub pattern"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Subscribe a handler to an event type
        
        Args:
            event_type: Event type name (e.g., "intervention.completed")
            handler: Callable that takes event data dict
        """
        self._subscribers[event_type].append(handler)
        logger.info(f"✅ Subscribed handler to event: {event_type}")
    
    def publish(self, event_type: str, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Publish an event to all subscribers
        
        Args:
            event_type: Event type name
            event_data: Event payload dictionary
            
        Returns:
            List of results from handlers (for debugging/monitoring)
        """
        results = []
        handlers = self._subscribers.get(event_type, [])
        
        if not handlers:
            logger.warning(f"⚠️ No subscribers for event: {event_type}")
            return results
        
        logger.info(f"📢 Publishing event '{event_type}' to {len(handlers)} handlers")
        
        for handler in handlers:
            try:
                result = handler(event_data)
                results.append({
                    "handler": handler.__name__,
                    "success": True,
                    "result": result
                })
                logger.info(f"✅ Handler {handler.__name__} processed event successfully")
            except Exception as e:
                error_info = {
                    "handler": handler.__name__,
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                results.append(error_info)
                logger.error(f"❌ Handler {handler.__name__} failed: {e}")
                logger.error(traceback.format_exc())
                # Continue processing other handlers even if one fails
        
        return results
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Remove a handler from an event type"""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            logger.info(f"✅ Unsubscribed handler from event: {event_type}")

# Global event bus instance
event_bus = EventBus()

