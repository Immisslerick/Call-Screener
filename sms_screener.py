from kivy.utils import platform
from plyer import notification
import json
import os
import re
from datetime import datetime

class SMSScreener:
    def __init__(self):
        self.is_active = False
        self.block_non_contacts = False
        self.blocked_numbers = set()
        self.whitelist = set()
        self.keyword_filters = []
        
        # Categorized spam patterns
        self.spam_patterns = {
            'financial_scams': [
                r'\b(win|won|winner|lottery|prize|cash|money|payment)\b',
                r'\$\d+[kKmM]?\b',  # Money amounts
                r'\b(investment|invest|bitcoin|crypto|forex|stocks)\b',
                r'\b(inheritance|bank|account|transfer|wire)\b',
                r'\b(loan|credit|debt|mortgage|refinance)\b'
            ],
            'urgent_action': [
                r'\b(urgent|immediate|action required|limited time|expires|expiring)\b',
                r'\b(account suspended|account blocked|security alert|unusual activity)\b',
                r'\b(verify|validate|confirm|update|upgrade)\b',
                r'!!+|⚠️|🚨',  # Multiple exclamation marks or warning emojis
            ],
            'promotional': [
                r'\b(free|discount|save|%\s*off|deal|offer|special)\b',
                r'\b(buy|purchase|order|shop|store)\b',
                r'\b(limited time|exclusive|vip|premium)\b',
                r'\b(subscription|trial|membership)\b'
            ],
            'suspicious_links': [
                r'https?://(?:bit\.ly|tinyurl\.com|goo\.gl)/\S+',  # URL shorteners
                r'https?://[^\s/$.?#].[^\s]*',  # General URLs
                r'\b(click|tap|visit|check|see)\s+(?:here|now|this)\b',
            ],
            'adult_content': [
                r'\b(adult|dating|single|meet|chat|hot|sexy)\b',
                r'\b(private|intimate|personal|video|photo)\b',
            ],
            'common_spam': [
                r'\b(congratulations|congrats|selected|chosen|lucky)\b',
                r'\b(warranty|insurance|coverage|policy|claim)\b',
                r'\b(gift card|reward|bonus|points)\b',
                r'\b(unsubscribe|stop|opt[ -]out)\b',
            ]
        }
        
        # Initialize filter categories
        self.filter_categories = list(self.spam_patterns.keys())
        self.active_categories = set(self.filter_categories)  # All categories active by default
        
        # Time-based patterns (messages at odd hours)
        self.time_restrictions = {
            'enabled': False,
            'quiet_hours': {
                'start': 22,  # 10 PM
                'end': 7      # 7 AM
            }
        }
        
        # Message frequency limits
        self.frequency_limits = {
            'enabled': False,
            'max_per_hour': 5,
            'max_per_day': 20,
            'message_history': {}  # Tracks message frequency per number
        }
        
        self.load_settings()

    def load_settings(self):
        """Load blocked numbers and filters from storage"""
        try:
            if os.path.exists('sms_filters.json'):
                with open('sms_filters.json', 'r') as f:
                    data = json.load(f)
                    self.blocked_numbers = set(data.get('blocked', []))
                    self.whitelist = set(data.get('whitelist', []))
                    self.keyword_filters = data.get('keywords', [])
                    self.block_non_contacts = data.get('block_non_contacts', False)
                    self.time_restrictions = data.get('time_restrictions', self.time_restrictions)
                    self.frequency_limits = data.get('frequency_limits', self.frequency_limits)
                    self.active_categories = set(data.get('active_categories', self.filter_categories))
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save blocked numbers and filters to storage"""
        try:
            with open('sms_filters.json', 'w') as f:
                json.dump({
                    'blocked': list(self.blocked_numbers),
                    'whitelist': list(self.whitelist),
                    'keywords': self.keyword_filters,
                    'block_non_contacts': self.block_non_contacts,
                    'time_restrictions': self.time_restrictions,
                    'frequency_limits': self.frequency_limits,
                    'active_categories': list(self.active_categories)
                }, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def toggle_time_restrictions(self, enabled=None):
        """Toggle time-based message restrictions"""
        if enabled is None:
            self.time_restrictions['enabled'] = not self.time_restrictions['enabled']
        else:
            self.time_restrictions['enabled'] = enabled
        self.save_settings()
        return self.time_restrictions['enabled']

    def set_quiet_hours(self, start_hour=None, end_hour=None):
        """Set quiet hours for message blocking"""
        current_start = self.time_restrictions['quiet_hours']['start']
        current_end = self.time_restrictions['quiet_hours']['end']
        
        # Update only the provided values
        if start_hour is not None:
            if 0 <= start_hour <= 23:
                current_start = start_hour
        if end_hour is not None:
            if 0 <= end_hour <= 23:
                current_end = end_hour
        
        # Update settings
        self.time_restrictions['quiet_hours']['start'] = current_start
        self.time_restrictions['quiet_hours']['end'] = current_end
        self.save_settings()

    def toggle_frequency_limits(self, enabled=None):
        """Toggle message frequency limiting"""
        if enabled is None:
            self.frequency_limits['enabled'] = not self.frequency_limits['enabled']
        else:
            self.frequency_limits['enabled'] = enabled
        self.save_settings()
        return self.frequency_limits['enabled']

    def set_frequency_limits(self, per_hour=None, per_day=None):
        """Set message frequency limits"""
        if per_hour is not None:
            self.frequency_limits['max_per_hour'] = per_hour
        if per_day is not None:
            self.frequency_limits['max_per_day'] = per_day
        self.save_settings()

    def check_message_frequency(self, number):
        """Check if a number has exceeded message frequency limits"""
        if not self.frequency_limits['enabled']:
            return False

        current_time = datetime.now()
        if number not in self.frequency_limits['message_history']:
            self.frequency_limits['message_history'][number] = []

        # Clean up old messages
        self.frequency_limits['message_history'][number] = [
            timestamp for timestamp in self.frequency_limits['message_history'][number]
            if (current_time - timestamp).total_seconds() < 86400  # 24 hours
        ]

        # Check frequency limits
        messages_last_hour = sum(
            1 for timestamp in self.frequency_limits['message_history'][number]
            if (current_time - timestamp).total_seconds() < 3600  # 1 hour
        )
        messages_last_day = len(self.frequency_limits['message_history'][number])

        # Add current message timestamp
        self.frequency_limits['message_history'][number].append(current_time)

        return (messages_last_hour >= self.frequency_limits['max_per_hour'] or 
                messages_last_day >= self.frequency_limits['max_per_day'])

    def is_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.time_restrictions['enabled']:
            return False

        current_hour = datetime.now().hour
        start = self.time_restrictions['quiet_hours']['start']
        end = self.time_restrictions['quiet_hours']['end']

        if start <= end:
            return start <= current_hour < end
        else:  # Handle case where quiet hours span midnight
            return current_hour >= start or current_hour < end

    def is_spam_content(self, message_content):
        """Check if message content matches spam patterns"""
        message_lower = message_content.lower()
        
        # Check custom keyword filters
        for filter_rule in self.keyword_filters:
            if filter_rule['keyword'] in message_lower and filter_rule['is_spam']:
                return True, 'custom_keyword'
        
        # Check categorized spam patterns
        for category, patterns in self.spam_patterns.items():
            if category in self.active_categories:
                for pattern in patterns:
                    if re.search(pattern, message_lower):
                        return True, category
                
        return False, None

    def should_block_sms(self, number, message_content):
        """Determine if an SMS should be blocked"""
        if not self.is_active:
            return False, None
        
        # Always allow whitelisted numbers
        if number in self.whitelist:
            return False, None
            
        # Block if number is in blocked list
        if number in self.blocked_numbers:
            return True, 'blocked_number'
            
        # Block non-contacts if enabled
        if self.block_non_contacts and not self.is_contact(number):
            return True, 'unknown_number'
            
        # Check quiet hours
        if self.is_quiet_hours():
            return True, 'quiet_hours'
            
        # Check message frequency
        if self.check_message_frequency(number):
            return True, 'frequency_limit'
            
        # Check message content for spam
        is_spam, category = self.is_spam_content(message_content)
        if is_spam:
            return True, f'spam_{category}'
                
        return False, None

    def handle_incoming_sms(self, number, message_content):
        """Handle an incoming SMS"""
        should_block, reason = self.should_block_sms(number, message_content)
        if should_block:
            reason_messages = {
                'blocked_number': 'blocked number',
                'unknown_number': 'unknown number',
                'quiet_hours': 'received during quiet hours',
                'frequency_limit': 'too many messages',
                'custom_keyword': 'matched blocked keyword'
            }
            
            # Handle spam categories
            if reason and reason.startswith('spam_'):
                category = reason.split('_', 1)[1]
                reason_message = f'detected {category.replace("_", " ")}'
            else:
                reason_message = reason_messages.get(reason, reason)
            
            self.show_notification(f"Blocked SMS from {number} ({reason_message})")
            return True  # Block the SMS
        return False  # Allow the SMS

    def show_notification(self, message):
        """Show a notification when an SMS is blocked"""
        try:
            notification.notify(
                title='SMS Screener',
                message=message,
                app_icon=None,
                timeout=10,
            )
        except Exception as e:
            print(f"Error showing notification: {e}")

    def toggle_screening(self):
        """Toggle SMS screening on/off"""
        self.is_active = not self.is_active
        return self.is_active

    def toggle_block_non_contacts(self):
        """Toggle blocking of messages from non-contacts"""
        self.block_non_contacts = not self.block_non_contacts
        self.save_settings()
        return self.block_non_contacts

    def add_blocked_number(self, number):
        """Add a number to the blocked list"""
        self.blocked_numbers.add(number)
        self.save_settings()

    def remove_blocked_number(self, number):
        """Remove a number from the blocked list"""
        if number in self.blocked_numbers:
            self.blocked_numbers.remove(number)
            self.save_settings()

    def add_to_whitelist(self, number):
        """Add a number to the whitelist"""
        self.whitelist.add(number)
        if number in self.blocked_numbers:
            self.blocked_numbers.remove(number)
        self.save_settings()

    def add_keyword_filter(self, keyword, is_spam=True):
        """Add a keyword filter"""
        self.keyword_filters.append({
            'keyword': keyword.lower(),
            'is_spam': is_spam
        })
        self.save_settings()

    def toggle_filter_category(self, category):
        """Toggle a specific filter category on/off"""
        if category in self.filter_categories:
            if category in self.active_categories:
                self.active_categories.remove(category)
            else:
                self.active_categories.add(category)
            self.save_settings()
            return True
        return False

    def is_category_active(self, category):
        """Check if a filter category is active"""
        return category in self.active_categories

    def is_contact(self, number):
        """Check if a number is a contact"""
        # TO DO: implement contact checking logic
        pass
