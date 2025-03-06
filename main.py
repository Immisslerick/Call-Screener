from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineIconListItem
from kivymd.uix.list import IconLeftWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDTimePicker
from kivy.core.window import Window
from kivy.utils import platform
from kivy.metrics import dp
from datetime import datetime

from services.call_screener import CallScreener
from services.sms_screener import SMSScreener

class CallScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        
    def setup_ui(self):
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        
        self.call_status_btn = MDFlatButton(
            text="Enable Call Screening",
            pos_hint={'center_x': .5},
            on_release=self.app.toggle_call_screening
        )
        
        self.block_non_contacts_btn = MDFlatButton(
            text="Block Non-Contacts: OFF",
            pos_hint={'center_x': .5},
            on_release=self.app.toggle_block_non_contacts
        )
        
        add_blocked_number_btn = MDFlatButton(
            text="Add Number to Block List",
            pos_hint={'center_x': .5},
            on_release=lambda x: self.app.show_add_number_dialog('call')
        )
        
        layout.add_widget(self.call_status_btn)
        layout.add_widget(self.block_non_contacts_btn)
        layout.add_widget(add_blocked_number_btn)
        
        self.add_widget(layout)

class SMSScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        
    def setup_ui(self):
        # Main layout with padding for better spacing
        layout = MDBoxLayout(orientation='vertical', spacing=8, padding=[15, 10, 15, 10])
        
        # Basic SMS controls section
        controls_box = MDBoxLayout(orientation='vertical', spacing=5, size_hint_x=None, width="250dp")
        controls_box.pos_hint = {'center_x': .5}
        
        self.sms_status_btn = MDFlatButton(
            text="Enable SMS Screening",
            size_hint_x=1,
            on_release=self.app.toggle_sms_screening
        )
        
        self.sms_block_non_contacts_btn = MDFlatButton(
            text="Block Non-Contact SMS: OFF",
            size_hint_x=1,
            on_release=self.app.toggle_sms_block_non_contacts
        )
        
        controls_box.add_widget(self.sms_status_btn)
        controls_box.add_widget(self.sms_block_non_contacts_btn)
        layout.add_widget(controls_box)
        
        # Spacer
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="10dp"))
        
        # Quiet Hours section
        quiet_hours_box = MDBoxLayout(
            orientation='vertical',
            spacing=5,
            padding=[5, 0, 5, 0],
            size_hint_x=None,
            width="300dp"
        )
        quiet_hours_box.pos_hint = {'center_x': .5}
        
        # Header with switch
        quiet_hours_header = MDBoxLayout(
            orientation='horizontal',
            spacing=5,
            size_hint_y=None,
            height="40dp"
        )
        
        quiet_hours_header.add_widget(
            MDLabel(
                text="Quiet Hours",
                bold=True,
                size_hint_x=0.7
            )
        )
        
        self.quiet_hours_switch = MDSwitch(
            size_hint_x=0.3,
            pos_hint={'center_y': .5}
        )
        self.quiet_hours_switch.bind(active=self.app.toggle_quiet_hours)
        quiet_hours_header.add_widget(self.quiet_hours_switch)
        quiet_hours_box.add_widget(quiet_hours_header)
        
        # Time buttons container
        time_buttons_box = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height="40dp"
        )
        
        self.quiet_start_btn = MDFlatButton(
            text="Start: 10 PM",
            size_hint_x=0.5,
            on_release=lambda x: self.app.show_time_picker('start')
        )
        
        self.quiet_end_btn = MDFlatButton(
            text="End: 7 AM",
            size_hint_x=0.5,
            on_release=lambda x: self.app.show_time_picker('end')
        )
        
        time_buttons_box.add_widget(self.quiet_start_btn)
        time_buttons_box.add_widget(self.quiet_end_btn)
        quiet_hours_box.add_widget(time_buttons_box)
        layout.add_widget(quiet_hours_box)
        
        # Spacer
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="10dp"))
        
        # Message Frequency Limits section
        freq_limit_box = MDBoxLayout(
            orientation='vertical',
            spacing=5,
            padding=[5, 0, 5, 0],
            size_hint_x=None,
            width="300dp"
        )
        freq_limit_box.pos_hint = {'center_x': .5}
        
        freq_limit_header = MDBoxLayout(
            orientation='horizontal',
            spacing=5,
            size_hint_y=None,
            height="40dp"
        )
        
        freq_limit_header.add_widget(
            MDLabel(
                text="Message Frequency Limits",
                bold=True,
                size_hint_x=0.7
            )
        )
        
        self.freq_limit_switch = MDSwitch(
            size_hint_x=0.3,
            pos_hint={'center_y': .5}
        )
        self.freq_limit_switch.bind(active=self.app.toggle_frequency_limits)
        freq_limit_header.add_widget(self.freq_limit_switch)
        freq_limit_box.add_widget(freq_limit_header)
        layout.add_widget(freq_limit_box)
        
        # Spacer
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="15dp"))
        
        # Bottom buttons
        button_container = MDBoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_x=None,
            width="250dp"
        )
        button_container.pos_hint = {'center_x': .5}
        
        filter_categories_btn = MDFlatButton(
            text="Manage Spam Filters",
            size_hint_x=1
        )
        filter_categories_btn.bind(on_release=self.app.show_filter_categories)
        
        add_keyword_btn = MDFlatButton(
            text="Add Custom Filter",
            size_hint_x=1
        )
        add_keyword_btn.bind(on_release=lambda x: self.app.show_add_number_dialog('keyword'))
        
        button_container.add_widget(filter_categories_btn)
        button_container.add_widget(add_keyword_btn)
        layout.add_widget(button_container)
        
        self.add_widget(layout)

class CallScreenApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call_screener = CallScreener()
        self.sms_screener = SMSScreener()
        self.dialog = None
        self.menu = None
        self.time_picker = None
        Window.softinput_mode = "below_target"  

    def build(self):
        # Set theme
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # Main layout
        layout = MDBoxLayout(orientation='vertical')
        
        # Create toolbar for navigation
        toolbar = MDTopAppBar(title="Call Screen")
        layout.add_widget(toolbar)
        
        # Create screen manager
        self.screen_manager = MDScreenManager()
        
        # Create screens
        call_screen = CallScreen(name="call")
        call_screen.app = self
        call_screen.setup_ui()  
        
        sms_screen = SMSScreen(name="sms")
        sms_screen.app = self
        sms_screen.setup_ui()  
        
        # Add screens to manager
        self.screen_manager.add_widget(call_screen)
        self.screen_manager.add_widget(sms_screen)
        
        # Create navigation buttons
        nav_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height="56dp",
            spacing=10,
            padding=10
        )
        
        call_nav_btn = MDFlatButton(
            text="Call Screening",
            on_release=lambda x: self.screen_manager.switch_to(call_screen, direction='right')
        )
        
        sms_nav_btn = MDFlatButton(
            text="SMS Screening",
            on_release=lambda x: self.screen_manager.switch_to(sms_screen, direction='left')
        )
        
        nav_box.add_widget(call_nav_btn)
        nav_box.add_widget(sms_nav_btn)
        
        # Add widgets to main layout
        layout.add_widget(self.screen_manager)
        layout.add_widget(nav_box)
        
        return layout

    def toggle_call_screening(self, instance):
        is_active = self.call_screener.toggle_screening()
        self.screen_manager.get_screen('call').call_status_btn.text = "Disable Call Screening" if is_active else "Enable Call Screening"
        
    def toggle_sms_screening(self, instance):
        is_active = self.sms_screener.toggle_screening()
        self.screen_manager.get_screen('sms').sms_status_btn.text = "Disable SMS Screening" if is_active else "Enable SMS Screening"
    
    def toggle_block_non_contacts(self, instance):
        """Toggle blocking of non-contact numbers"""
        is_active = self.call_screener.toggle_block_non_contacts()
        self.screen_manager.get_screen('call').block_non_contacts_btn.text = "Block Non-Contacts: ON" if is_active else "Block Non-Contacts: OFF"

    def toggle_sms_block_non_contacts(self, instance):
        """Toggle blocking of non-contact SMS"""
        is_active = self.sms_screener.toggle_block_non_contacts()
        self.screen_manager.get_screen('sms').sms_block_non_contacts_btn.text = "Block Non-Contact SMS: ON" if is_active else "Block Non-Contact SMS: OFF"

    def toggle_quiet_hours(self, instance, value):
        """Toggle quiet hours feature"""
        self.sms_screener.toggle_time_restrictions(value)

    def toggle_frequency_limits(self, instance, value):
        """Toggle message frequency limits"""
        self.sms_screener.toggle_frequency_limits(value)

    def show_time_picker(self, time_type):
        """Show time picker dialog for quiet hours start/end time."""
        self.time_picker = MDTimePicker()
        self.time_picker.bind(on_save=lambda instance, time: self.set_time(time_type, time))
        self.time_picker.open()
        
    def set_time(self, time_type, time):
        """Set the quiet hours start/end time."""
        if time_type == 'start':
            self.screen_manager.get_screen('sms').quiet_start_btn.text = f"Start: {time.strftime('%I:%M %p')}"
            self.sms_screener.set_quiet_hours(start_hour=time.hour, end_hour=None)
        else:
            self.screen_manager.get_screen('sms').quiet_end_btn.text = f"End: {time.strftime('%I:%M %p')}"
            self.sms_screener.set_quiet_hours(start_hour=None, end_hour=time.hour)
        self.time_picker = None

    def toggle_filter_category(self, category):
        """Toggle a filter category and update UI"""
        if self.sms_screener.toggle_filter_category(category):
            # Update dialog content to reflect changes
            if self.dialog:
                self.dialog.dismiss()
                self.show_filter_categories(None)

    def show_filter_categories(self, instance):
        """Show dialog to manage spam filter categories"""
        content = MDList()
        
        # Add list items for each category
        for category in self.sms_screener.filter_categories:
            # Convert category name to display name
            display_name = category.replace('_', ' ').title()
            is_active = self.sms_screener.is_category_active(category)
            
            # Create list item with icon
            item = OneLineIconListItem(text=display_name)
            icon = IconLeftWidget(
                icon="check-circle" if is_active else "circle-outline"
            )
            item.add_widget(icon)
            
            # Store category for callback
            item.category = category
            item.bind(on_release=lambda x: self.toggle_filter_category(x.category))
            
            content.add_widget(item)
        
        # Create dialog
        self.dialog = MDDialog(
            title="Spam Filter Categories",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="Close",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def show_add_number_dialog(self, dialog_type):
        """Show dialog to add blocked number or keyword"""
        title = "Add Number to Block List" if dialog_type == 'call' else "Add Custom Filter"
        hint = "Enter phone number" if dialog_type == 'call' else "Enter keyword or phrase"
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10,
            size_hint_y=None,
            height="100dp"
        )
        
        self.dialog_text = MDTextField(
            hint_text=hint,
            size_hint_y=None,
            height="48dp"
        )
        content.add_widget(self.dialog_text)
        
        buttons = [
            MDFlatButton(
                text="Cancel",
                on_release=lambda x: self.dialog.dismiss()
            ),
            MDFlatButton(
                text="Add",
                on_release=lambda x: self.add_blocked_item(dialog_type)
            )
        ]
        
        self.dialog = MDDialog(
            title=title,
            content_cls=content,
            type="custom",
            buttons=buttons
        )
        self.dialog.open()

    def close_dialog(self, *args):
        self.dialog.dismiss()
        self.dialog = None
    
    def add_blocked_item(self, dialog_type):
        """Add a new filter (number or keyword)"""
        if dialog_type == 'keyword':
            keyword = self.dialog_text.text.strip()
            if keyword:
                self.sms_screener.add_keyword_filter(keyword)
        else:
            number = self.dialog_text.text.strip()
            if number:
                if dialog_type == 'call':
                    self.call_screener.add_blocked_number(number)
                else:
                    self.sms_screener.add_blocked_number(number)
        self.close_dialog()

    def on_start(self):
        # Check permissions when app starts
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_PHONE_STATE,
                Permission.READ_CALL_LOG,
                Permission.READ_SMS,
                Permission.RECEIVE_SMS,
                Permission.READ_CONTACTS  
            ])

if __name__ == '__main__':
    CallScreenApp().run()
