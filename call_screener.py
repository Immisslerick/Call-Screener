from kivy.utils import platform
from plyer import notification
import json
import os

class CallScreener:
    def __init__(self):
        self.is_active = False
        self.block_non_contacts = False  # New flag for blocking non-contacts
        self.blocked_numbers = set()
        self.whitelist = set()
        self.rules = []
        self.load_settings()

    def load_settings(self):
        """Load blocked numbers and rules from storage"""
        try:
            if os.path.exists('blocked_numbers.json'):
                with open('blocked_numbers.json', 'r') as f:
                    data = json.load(f)
                    self.blocked_numbers = set(data.get('blocked', []))
                    self.whitelist = set(data.get('whitelist', []))
                    self.rules = data.get('rules', [])
                    self.block_non_contacts = data.get('block_non_contacts', False)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save blocked numbers and rules to storage"""
        try:
            with open('blocked_numbers.json', 'w') as f:
                json.dump({
                    'blocked': list(self.blocked_numbers),
                    'whitelist': list(self.whitelist),
                    'rules': self.rules,
                    'block_non_contacts': self.block_non_contacts
                }, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

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

    def is_contact(self, number):
        """Check if a number is in the phone's contacts"""
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                from android import activity
                from jnius import autoclass, cast

                # Request contacts permission if not already granted
                request_permissions([Permission.READ_CONTACTS])

                # Get the Android Context and ContentResolver
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                resolver = context.getContentResolver()

                # Define the URI for contacts
                ContactsContract = autoclass('android.provider.ContactsContract')
                uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI

                # Prepare the query
                projection = ['data1']  # data1 is the phone number
                selection = 'data1 = ?'
                selection_args = [number]

                # Execute query
                cursor = resolver.query(uri, projection, selection, selection_args, None)
                
                if cursor is not None:
                    exists = cursor.getCount() > 0
                    cursor.close()
                    return exists
                return False
            except Exception as e:
                print(f"Error checking contacts: {e}")
                return False
        return True  # Default to true for non-Android platforms during testing

    def toggle_block_non_contacts(self):
        """Toggle blocking of non-contact numbers"""
        self.block_non_contacts = not self.block_non_contacts
        self.save_settings()
        return self.block_non_contacts

    def should_block_call(self, number):
        """Determine if a call should be blocked"""
        if not self.is_active:
            return False
        
        # Always allow whitelisted numbers
        if number in self.whitelist:
            return False
            
        # Block if number is in blocked list
        if number in self.blocked_numbers:
            return True
            
        # Check if we should block non-contacts
        if self.block_non_contacts and not self.is_contact(number):
            return True
            
        # Apply custom rules
        for rule in self.rules:
            if rule['type'] == 'prefix' and number.startswith(rule['value']):
                return True
            elif rule['type'] == 'pattern' and rule['value'] in number:
                return True
                
        return False

    def handle_incoming_call(self, number):
        """Handle an incoming call"""
        if self.should_block_call(number):
            message = "Blocked call from unknown number" if self.block_non_contacts else f"Blocked call from {number}"
            self.show_notification(message)
            return True  # Block the call
        return False  # Allow the call

    def show_notification(self, message):
        """Show a notification when a call is blocked"""
        try:
            notification.notify(
                title='Call Screener',
                message=message,
                app_icon=None,
                timeout=10,
            )
        except Exception as e:
            print(f"Error showing notification: {e}")

    def toggle_screening(self):
        """Toggle call screening on/off"""
        self.is_active = not self.is_active
        return self.is_active
