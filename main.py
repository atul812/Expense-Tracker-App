from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore
from datetime import datetime
from collections import deque, defaultdict
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen


class LinkedListNode:
    def __init__(self, data):
        self.data = data
        self.next = None


class RecurringExpensesLinkedList:
    def __init__(self):
        self.head = None

    def add_expense(self, expense):
        new_node = LinkedListNode(expense)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def get_expenses(self):
        expenses = []
        current = self.head
        while current:
            expenses.append(current.data)
            current = current.next
        return expenses


class ExpenseTrackerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expenses = []  # List to store user-added expenses
        self.daily_expenses = defaultdict(lambda: defaultdict(float))  # Daily expenses by category
        self.monthly_budget = 0.0  # Initialize monthly budget

        # Input for monthly budget
        self.budget_input = MDTextField(
            hint_text="Enter Monthly Budget",
            mode="fill",
            input_filter='float',
            helper_text="Required field"
        )

        # Queue for streak counter
        self.streak_queue = deque(maxlen=7)  # Limit to last 7 days
        self.streak_store = JsonStore("streak.json")
        self.load_streak_data()

        # Linked list for recurring expenses
        self.recurring_expenses = RecurringExpensesLinkedList()

        # Main container
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # Streak Counter Display
        self.streak_label = MDLabel(
            text=f"🔥 Streak: {len(self.streak_queue)} days",
            halign="left",
            theme_text_color="Primary",
            size_hint=(None, None),
            pos_hint={"x": 0.05, "y": 0.9},
        )
        main_layout.add_widget(self.streak_label)

        # Update streak logic every time app is launched
        self.update_streak()

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

        # Pick Date button
        pick_date_button = MDRaisedButton(
            text="Pick Date",
            on_press=self.show_date_picker,
            md_bg_color=(0.2, 0.6, 1, 1)
        )

        self.recurring_input = MDTextField(
            hint_text="Is this a recurring expense? (yes/no)",
            mode="fill"
        )

        # Add inputs to input card
        input_card.add_widget(self.budget_input)  # Add budget input
        input_card.add_widget(self.category_input)
        input_card.add_widget(self.item_input)
        input_card.add_widget(self.amount_input)
        input_card.add_widget(self.date_input)
        input_card.add_widget(pick_date_button)
        input_card.add_widget(self.recurring_input)
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
            on_press=self.show_expenses,
            md_bg_color=(0.2, 0.6, 1, 1)
        )
        daily_button = MDRaisedButton(
            text="Daily Expenses",
            on_press=self.show_daily_expenses,
            md_bg_color=(0.2, 0.6, 1, 1)
        )
        monthly_button = MDRaisedButton(
            text="Monthly Expenses",
            on_press=self.show_monthly_expenses,
            md_bg_color=(0.2, 0.6, 1, 1)
        )
        recurring_button = MDRaisedButton(
            text="Show Recurring",
            on_press=self.show_recurring_expenses,
            md_bg_color=(0.2, 0.6, 1, 1)
        )

        button_layout.add_widget(add_button)
        button_layout.add_widget(show_button)
        button_layout.add_widget(daily_button)
        button_layout.add_widget(monthly_button)
        button_layout.add_widget(recurring_button)
        main_layout.add_widget(button_layout)

        self.add_widget(main_layout)

    def load_streak_data(self):
        if self.streak_store.exists("streak"):
            try:
                streak_data = self.streak_store.get("streak")
                self.streak_queue = deque(
                    [datetime.fromisoformat(date).date() for date in streak_data.get("dates", [])],
                    maxlen=7
                )
            except (KeyError, ValueError):
                self.streak_store.put("streak", dates=[])
                self.streak_queue = deque(maxlen=7)

    def save_streak_data(self):
        self.streak_store.put("streak", dates=[date.isoformat() for date in self.streak_queue])

    def update_streak(self):
        today = datetime.now().date()
        if not self.streak_queue or self.streak_queue[-1] != today:
            if self.streak_queue and (today - self.streak_queue[-1]).days > 1:
                self.streak_queue.clear()  # Reset streak if a day is missed
            self.streak_queue.append(today)
        self.save_streak_data()
        self.streak_label.text = f"🔥 Streak: {len(self.streak_queue)} days"

    def add_expense(self, instance):
        category = self.category_input.text
        item = self.item_input.text
        amount = self.amount_input.text
        date = self.date_input.text
        is_recurring = self.recurring_input.text.lower() == "yes"

        if not category or not item or not amount or not date:
            return

        expense = {
            "category": category,
            "item": item,
            "amount": float(amount),
            "date": date,
        }

        self.daily_expenses[date][category] += float(amount)

        if is_recurring:
            self.recurring_expenses.add_expense(expense)

        self.expenses.append(expense)
        self.category_input.text = ""
        self.item_input.text = ""
        self.amount_input.text = ""
        self.date_input.text = ""
        self.recurring_input.text = ""

    def show_expenses(self, instance):
        # Detailed view for show expenses
        expense_text = "\n".join(
            [f"Date: {e['date']}, Item: {e['item']}, Amount: {e['amount']}, Category: {e['category']}" for e in
             self.expenses]
        )
        self.show_popup(expense_text if expense_text else "No expenses recorded.")

    def show_daily_expenses(self, instance):
        today = datetime.now().strftime("%d-%m-%Y")
        daily_expenses_details = []
        for category, amount in self.daily_expenses[today].items():
            detailed_item_text = f"{category}: {amount} on {today}"
            daily_expenses_details.append(detailed_item_text)

        daily_expense_text = "\n".join(daily_expenses_details)
        self.show_popup(daily_expense_text if daily_expense_text else "No expenses for today.")

    def show_monthly_expenses(self, instance):
        month = datetime.now().strftime("%m-%Y")
        monthly_total = 0
        monthly_expense_detail = []

        for date, categories in self.daily_expenses.items():
            if date.endswith(month):
                for category, amount in categories.items():
                    monthly_total += amount
                    monthly_expense_detail.append(f"{date} - {category}: {amount}")

        # Get monthly budget input
        budget = float(self.budget_input.text) if self.budget_input.text else 0.0
        remaining_budget = budget - monthly_total

        # Prepare detailed monthly information
        monthly_detail_text = "\n".join(monthly_expense_detail)

        summary_text = (f"Total Monthly Expenses: {monthly_total}\n"
                        f"Remaining Budget: {remaining_budget}\n\n"
                        f"Details:\n{monthly_detail_text}" if monthly_detail_text else "No monthly expenses recorded.")

        self.show_popup(summary_text)

    def show_recurring_expenses(self, instance):
        expenses = self.recurring_expenses.get_expenses()
        if not expenses:
            self.show_popup("No recurring expenses recorded.")
        else:
            recurring_expense_text = "\n".join(
                [f"{e['date']} - {e['item']} - {e['amount']} ({e['category']})" for e in expenses]
            )
            self.show_popup(recurring_expense_text)

    def show_popup(self, content):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        with popup_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(1, 1, 1, 1)  # White background
            self.rect = Rectangle(size=popup_layout.size, pos=popup_layout.pos)

            popup_layout.bind(size=self.update_rect, pos=self.update_rect)


        content_label = MDLabel(
            text=content,
            theme_text_color="Primary",
            halign="center",
            size_hint_y=None,
            height=dp(200)
        )

        close_button = MDFlatButton(
            text="Close",
            on_press=lambda instance: self.close_popup(popup)  # Pass the popup instance
        )

        popup_layout.add_widget(content_label)
        popup_layout.add_widget(close_button)

        popup = Popup(
            title="Expense Details",
            content=popup_layout,
            size_hint=(0.8, None),
            height=dp(300)
        )

        popup.open()

    def close_popup(self, popup):
        popup.dismiss()  # Dismiss the popup instance

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def show_date_picker(self, instance):
        date_picker = MDDatePicker()  # Removed callback parameter
        date_picker.bind(on_save=self.set_date)  # Bind the save event
        date_picker.open()  # Open the date picker

    def set_date(self, instance, date, date_range):
        self.date_input.text = date.strftime("%d-%m-%Y")


class ExpenseTrackerApp(MDApp):
    def build(self):
        return ExpenseTrackerScreen()


if __name__ == "__main__":
    ExpenseTrackerApp().run()
