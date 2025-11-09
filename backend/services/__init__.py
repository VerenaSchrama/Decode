"""
Services package - Event-driven intervention completion system
"""

from services.event_bus import event_bus
from services.intervention_service import intervention_service
from services.habit_service import complete_related_habits
from services.analytics_service import generate_completion_summary
from services.notification_service import send_completion_notification

# Register event listeners on module import
event_bus.subscribe("intervention.completed", complete_related_habits)
event_bus.subscribe("intervention.completed", generate_completion_summary)
event_bus.subscribe("intervention.completed", send_completion_notification)

__all__ = [
    'event_bus',
    'intervention_service',
    'complete_related_habits',
    'generate_completion_summary',
    'send_completion_notification'
]

