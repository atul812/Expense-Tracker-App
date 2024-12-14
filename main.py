from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivymd.uix.picker import MDDatePicker
from kivymd.app import MDApp
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


class ExpenseTrackerApp(MDApp):
    def build(self):
        self.expenses = []  # List to store user-added expenses
        self.daily_expenses = defaultdict(lambda: defaultdict(float))  # Daily expenses by category
        self.monthly_budget = 0.0

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Create a title
        title = Label(text="Expense Tracker", font_size='24sp', size_hint=(1, 0.1), halign="center")
        main_layout.add_widget(title)

        # Widgets for user input
        self.category_input = TextInput(hint_text="Enter Category", size_hint=(1, 0.1), multiline=False)
        self.item_input = TextInput(hint_text="Enter Item", size_hint=(1, 0.1), multiline=False)
        self.amount_input = TextInput(hint_text="Enter Amount", input_filter='float', size_hint=(1, 0.1),
                                      multiline=False)

        # Date input field
        self.date_input = TextInput(hint_text="Select Date", size_hint=(1, 0.1), multiline=False, readonly=True)
        self.date_input.bind(on_touch_down=self.show_date_picker)

        self.description_input = TextInput(hint_text="Enter Description", size_hint=(1, 0.1), multiline=False)

        self.budget_input = TextInput(hint_text="Enter Monthly Budget", size_hint=(1, 0.1), multiline=False)

        # Buttons
        button_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        add_button = Button(text="Add Expense", size_hint=(0.33, 1), on_press=self.add_expense,
                            background_color=(0.2, 0.6, 1, 1))
        show_button = Button(text="Show Expenses", size_hint=(0.33, 1), on_press=self.show_expenses_popup,
                             background_color=(0.2, 0.6, 1, 1))
        daily_exp_button = Button(text="Daily Expenses", size_hint=(0.33, 1), on_press=self.show_daily_expenses_popup,
                                  background_color=(0.2, 0.6, 1, 1))

        monthly_summary_button = Button(text="Monthly Summary", size_hint=(1, 0.1),
                                        on_press=self.show_monthly_summary_popup, background_color=(0.2, 0.6, 1, 1))

        button_layout.add_widget(add_button)
        button_layout.add_widget(show_button)
        button_layout.add_widget(daily_exp_button)

        # Feedback label
        self.feedback_label = Label(text="", size_hint=(1, 0.1))

        # RecycleView for expense list (not displayed in the popup)
        self.expense_list_view = ExpenseList(self.expenses)

        # Add widgets to main layout
        main_layout.add_widget(self.category_input)
        main_layout.add_widget(self.item_input)
        main_layout.add_widget(self.amount_input)
        main_layout.add_widget(self.date_input)
        main_layout.add_widget(self.description_input)
        main_layout.add_widget(self.budget_input)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(monthly_summary_button)
        main_layout.add_widget(self.feedback_label)

        return main_layout

    def show_date_picker(self, instance, touch):
        if instance.collide_point(*touch.pos):
            date_dialog = MDDatePicker()
            date_dialog.bind(on_save=self.on_date_selected)
            date_dialog.open()
            return True
        return False

    def on_date_selected(self, instance, value, date_range):
        self.date_input.text = value.strftime("%d-%m-%Y")

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

        # Update the RecycleView
        self.expense_list_view.update_data(self.expenses)

        # Clear input fields
        self.category_input.text = ""
        self.item_input.text = ""
        self.amount_input.text = ""
        self.date_input.text = ""
        self.description_input.text = ""

        # Provide feedback
        self.feedback_label.text = f"Expense Added: {category} - {item} - {amount} on {date}"

    def show_expenses_popup(self, instance):
        # Create a layout for the popup content
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        if not self.expenses:
            popup_layout.add_widget(Label(text="No expenses to show."))
        else:
            # Group expenses by category
            grouped_expenses = {}
            for expense in self.expenses:
                category = expense['category']
                if category not in grouped_expenses:
                    grouped_expenses[category] = {'items': [], 'total': 0}
                grouped_expenses[category]['items'].append(expense)
                grouped_expenses[category]['total'] += expense['amount']

            # Add all expenses to the popup layout
            scroll_view = ScrollView()
            expense_list = BoxLayout(orientation='vertical', size_hint_y=None)
            expense_list.bind(minimum_height=expense_list.setter('height'))

            for category, details in grouped_expenses.items():
                category_label = Label(text=f"Category: {category} - Total Spent: {details['total']}", size_hint_y=None,
                                       height=40, bold=True)
                expense_list.add_widget(category_label)

                for expense in details['items']:
                    expense_label = Label(
                        text=f"{expense['item']} - {expense['amount']} on {expense['date']} in {expense['description']}",
                        size_hint_y=None,
                        height=40
                    )
                    expense_list.add_widget(expense_label)

                expense_list.add_widget(Label(text=""))  # Add a blank label for spacing

            scroll_view.add_widget(expense_list)
            popup_layout.add_widget(scroll_view)

        # Close button
        close_button = Button(text="Close", size_hint=(1, 0.2), background_color=(0.8, 0, 0, 1))
        popup_layout.add_widget(close_button)

        # Create the popup
        popup = Popup(title="Expense List", content=popup_layout, size_hint=(0.9, 0.9))
        close_button.bind(on_press=popup.dismiss)

        # Open the popup
        popup.open()

    def show_daily_expenses_popup(self, instance):
        # Create a layout for the popup content
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        if not self.daily_expenses:
            popup_layout.add_widget(Label(text="No daily expenses to show."))
        else:
            # Add daily expenses to the popup layout
            scroll_view = ScrollView()
            daily_expense_list = BoxLayout(orientation='vertical', size_hint_y=None)
            daily_expense_list.bind(minimum_height=daily_expense_list.setter('height'))

            for date, categories in sorted(self.daily_expenses.items()):
                formatted_date = date.strftime("%d-%m-%Y")  # Format the date
                date_label = Label(text=f"Date: {formatted_date}", size_hint_y=None, height=40, bold=True)
                daily_expense_list.add_widget(date_label)

                for category, total in categories.items():
                    category_label = Label(text=f"{category}:", size_hint_y=None, height=30, bold=True)
                    daily_expense_list.add_widget(category_label)

                    # Add items under each category
                    for expense in self.expenses:
                        if expense['category'] == category and datetime.strptime(expense['date'],
                                                                                 "%d-%m-%Y").date() == date:
                            item_label = Label(text=f"    - {expense['item']}: {expense['amount']}", size_hint_y=None,
                                               height=30)
                            daily_expense_list.add_widget(item_label)

                daily_expense_list.add_widget(Label(text=""))  # Add a blank label for spacing

            scroll_view.add_widget(daily_expense_list)
            popup_layout.add_widget(scroll_view)

            # Close button
        close_button = Button(text="Close", size_hint=(1, 0.1), background_color=(0.8, 0, 0, 1))
        popup_layout.add_widget(close_button)

        # Create the popup
        popup = Popup(title="Daily Expenses", content=popup_layout, size_hint=(0.9, 0.9))
        close_button.bind(on_press=popup.dismiss)

        # Open the popup
        popup.open()

    def show_monthly_summary_popup(self, instance):
        # Create a layout for the popup content
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        if not self.expenses:
            popup_layout.add_widget(Label(text="No expenses to show."))
        else:
            # Calculate total spent
            total_spent = sum(expense['amount'] for expense in self.expenses)

            # Display budget and total spent
            budget_label = Label(text=f"Monthly Budget: {self.monthly_budget}", size_hint_y=None, height=40, bold=True)
            spent_label = Label(text=f"Total Spent: {total_spent}", size_hint_y=None, height=40, bold=True)

            popup_layout.add_widget(budget_label)
            popup_layout.add_widget(spent_label)

            # Display remaining budget
            remaining_budget = self.monthly_budget - total_spent
            remaining_label = Label(text=f"Remaining Budget: {remaining_budget}", size_hint_y=None, height=40,
                                    bold=True)
            popup_layout.add_widget(remaining_label)

        # Close button
        close_button = Button(text="Close", size_hint=(1, 0.1), background_color=(0.8, 0, 0, 1))
        popup_layout.add_widget(close_button)

        # Create the popup
        popup = Popup(title="Monthly Summary", content=popup_layout, size_hint=(0.9, 0.9))
        close_button.bind(on_press=popup.dismiss)

        # Open the popup
        popup.open()

if __name__ == "__main__":
    ExpenseTrackerApp().run()
