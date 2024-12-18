from kivy.uix.recycleview import RecycleView
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

from collections import defaultdict
from datetime import datetime


class ExpenseList(RecycleView):
    def __init__(self, expenses, **kwargs):
        super().__init__(**kwargs)
        self.update_data(expenses)

    def update_data(self, expenses):
        self.data = [
            {"text": f"{expense['category']} - {expense['item']} - {expense['amount']} on {expense['date']}"}
            for expense in expenses
        ]


class ExpenseTrackerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expenses = []  # List to store user-added expenses
        self.daily_expenses = defaultdict(lambda: defaultdict(float))  # Daily expenses by category
        self.monthly_budget = 0.0

        # Main container
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # Title
        title = MDLabel(
            text="Expense Tracker",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(title)

        # Input Card
        input_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(450),
            elevation=5
        )

        # Input Fields
        self.category_input = MDTextField(
            hint_text="Enter Category",
            mode="fill",
            helper_text="Required field"
        )
        self.item_input = MDTextField(
            hint_text="Enter Item",
            mode="fill",
            helper_text="Required field"
        )
        self.amount_input = MDTextField(
            hint_text="Enter Amount",
            mode="fill",
            input_filter='float',
            helper_text="Required field"
        )

        # Date input with custom date picker
        self.date_input = MDTextField(
            hint_text="Select Date",
            mode="fill",
            readonly=True
        )

        # Bind the date input to show the date picker
        self.date_input.bind(focus=self.show_date_picker)

        self.description_input = MDTextField(
            hint_text="Enter Description",
            mode="fill",
            multiline=True
        )

        self.budget_input = MDTextField(
            hint_text="Enter Monthly Budget",
            mode="fill",
            input_filter='float'
        )

        # Add inputs to input card
        input_card.add_widget(self.category_input)
        input_card.add_widget(self.item_input)
        input_card.add_widget(self.amount_input)
        input_card.add_widget(self.date_input)
        input_card.add_widget(self.description_input)
        input_card.add_widget(self.budget_input)
        main_layout.add_widget(input_card)

        # Button Layout
        button_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))

        add_button = MDRaisedButton(
            text="Add Expense",
            on_press=self.add_expense,
            md_bg_color=(0.2, 0.6, 1, 1)
        )
        show_button = MDRaisedButton(
            text="Show Expenses",
            on_press=self.show_expenses_popup,
            md_bg_color=(0.2, 0.6, 1, 1)
        )
        daily_exp_button = MDRaisedButton(
            text="Daily Expenses",
            on_press=self.show_daily_expenses_popup,
            md_bg_color=(0.2, 0.6, 1, 1)
        )

        button_layout.add_widget(add_button)
        button_layout.add_widget(show_button)
        button_layout.add_widget(daily_exp_button)
        main_layout.add_widget(button_layout)

        # Monthly Summary Button
        monthly_summary_button = MDRaisedButton(
            text="Monthly Summary",
            on_press=self.show_monthly_summary_popup,
            md_bg_color=(0.2, 0.6, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(monthly_summary_button)

        # Feedback Label
        self.feedback_label = MDLabel(
            text="",
            halign="center",
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(self.feedback_label)

        self.add_widget(main_layout)

    def show_date_picker(self, instance, value):
        if value:  # Focus gained
            date_dialog = MDDatePicker()
            date_dialog.bind(on_save=self.on_date_selected)
            date_dialog.open()

    def on_date_selected(self, instance, value, date_range):
        # Update the date input field with the selected date
        self.date_input.text = value.strftime("%d-%m-%Y")
        # Remove focus from the text field after selecting a date
        self.date_input.focus = False

    def on_cancel(self, instance, value):
        print("Date selection canceled.")


    def add_expense(self, instance):
        # Get input data
        category = self.category_input.text
        item = self.item_input.text
        amount = self.amount_input.text
        date = self.date_input.text
        description = self.description_input.text
        try:
            budget = float(self.budget_input.text)
            self.monthly_budget = budget
        except ValueError:
            self.budget_input.text = ""

        # Validate input
        if not category or not item or not amount or not date:
            self.feedback_label.text = "Please fill in all required fields."
            return

        # Add expense to list
        expense = {
            "category": category,
            "item": item,
            "amount": float(amount),
            "date": date,
            "description": description,
        }
        self.expenses.append(expense)

        # Track daily expenses
        date_key = datetime.strptime(date, "%d-%m-%Y").date()
        self.daily_expenses[date_key][category] += float(amount)

        # Clear input fields
        self.category_input.text = ""
        self.item_input.text = ""
        self.amount_input.text = ""
        self.date_input.text = ""
        self.description_input.text = ""

        # Provide feedback
        self.feedback_label.text = f"Expense Added: {category} - {item} - {amount} on {date}"

    def show_expenses_popup(self, instance):
        # Create a popup with Material Design styling
        popup_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        if not self.expenses:
            popup_layout.add_widget(MDLabel(text="No expenses to show.", halign="center"))
        else:
            # Grouped expenses display
            scroll_view = ScrollView()
            expense_list = MDList()

            # Group expenses by category
            grouped_expenses = {}
            for expense in self.expenses:
                category = expense['category']
                if category not in grouped_expenses:
                    grouped_expenses[category] = {'items': [], 'total': 0}
                grouped_expenses[category]['items'].append(expense)
                grouped_expenses[category]['total'] += expense['amount']

            # Add expenses to list
            for category, details in grouped_expenses.items():
                # Category header
                category_item = OneLineListItem(
                    text=f"{category} - Total: {details['total']:.2f}",
                    font_style="Subtitle1"
                )
                expense_list.add_widget(category_item)

                # Individual expenses
                for expense in details['items']:
                    expense_item = OneLineListItem(
                        text=f"{expense['item']} - {expense['amount']} on {expense['date']}"
                    )
                    expense_list.add_widget(expense_item)

            scroll_view.add_widget(expense_list)
            popup_layout.add_widget(scroll_view)

        # Close button with Material Design
        close_button = MDFlatButton(
            text="Close",
            on_release=self.dismiss_popup
        )
        popup_layout.add_widget(close_button)

        # Create popup
        self.expenses_popup = Popup(
            title="Expense List",
            content=popup_layout,
            size_hint=(0.9, 0.9)
        )
        self.expenses_popup.open()

    def dismiss_popup(self, *args):
        # Generic method to close popups
        if hasattr(self, 'expenses_popup'):
            self.expenses_popup.dismiss()
        if hasattr(self, 'daily_expenses_popup'):
            self.daily_expenses_popup.dismiss()
        if hasattr(self, 'monthly_summary_popup'):
            self.monthly_summary_popup.dismiss()

    def show_daily_expenses_popup(self, instance):
        # Similar structure to show_expenses_popup
        popup_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        if not self.daily_expenses:
            popup_layout.add_widget(MDLabel(text="No daily expenses to show.", halign="center"))
        else:
            scroll_view = ScrollView()
            daily_expense_list = MDList()

            for date, categories in sorted(self.daily_expenses.items()):
                formatted_date = date.strftime("%d-%m-%Y")
                date_item = OneLineListItem(
                    text=f"Date: {formatted_date}",
                    font_style="Subtitle1"
                )
                daily_expense_list.add_widget(date_item)

                for category, total in categories.items():
                    category_item = OneLineListItem(
                        text=f"{category}: {total:.2f}"
                    )
                    daily_expense_list.add_widget(category_item)

            scroll_view.add_widget(daily_expense_list)
            popup_layout.add_widget(scroll_view)

        close_button = MDFlatButton(
            text="Close",
            on_release=self.dismiss_popup
        )
        popup_layout.add_widget(close_button)

        self.daily_expenses_popup = Popup(
            title="Daily Expenses",
            content=popup_layout,
            size_hint=(0.9, 0.9)
        )
        self.daily_expenses_popup.open()

    def show_monthly_summary_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        if not self.expenses:
            popup_layout.add_widget(MDLabel(text="No expenses to show.", halign="center"))
        else:
            # Calculate total spent
            total_spent = sum(expense['amount'] for expense in self.expenses)

            # Create cards for budget information
            budget_card = MDCard(
                orientation='vertical',
                padding=dp(15),
                spacing=dp(10),
                size_hint=(1, None),
                height=dp(250),
                elevation=5
            )

            # Budget information labels
            budget_label = MDLabel(
                text=f"Monthly Budget: {self.monthly_budget:.2f}",
                font_style="Subtitle1"
            )
            spent_label = MDLabel(
                text=f"Total Spent: {total_spent:.2f}",
                font_style="Subtitle1"
            )

            # Remaining budget calculation and color-coded label
            remaining_budget = self.monthly_budget - total_spent
            remaining_label = MDLabel(
                text=f"Remaining Budget: {remaining_budget:.2f}",
                font_style="Subtitle1",
                theme_text_color="Custom",
                text_color=(0, 0.7, 0, 1) if remaining_budget > 0 else (0.7, 0, 0, 1)
            )

            budget_card.add_widget(budget_label)
            budget_card.add_widget(spent_label)
            budget_card.add_widget(remaining_label)

            popup_layout.add_widget(budget_card)

        close_button = MDFlatButton(
            text="Close",
            on_release=self.dismiss_popup
        )
        popup_layout.add_widget(close_button)

        self.monthly_summary_popup = Popup(
            title="Monthly Summary",
            content=popup_layout,
            size_hint=(0.9, 0.9)
        )
        self.monthly_summary_popup.open()


class ExpenseTrackerApp(MDApp):
    def build(self):
        # Create screen manager
        self.sm = MDScreenManager()

        # Create main screen
        main_screen = ExpenseTrackerScreen(name='main')
        self.sm.add_widget(main_screen)

        return self.sm


if __name__ == "__main__":
    ExpenseTrackerApp().run()
