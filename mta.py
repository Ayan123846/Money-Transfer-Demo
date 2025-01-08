import streamlit as st
import json

USER_DATA_FILE = "user_data.json"

# Function to load user data
def load_user_data():
    try:
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Function to save user data
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Ensure 'transaction_log' exists in user data
def ensure_transaction_log():
    if "transaction_log" not in users:
        users["transaction_log"] = []  # Create an empty transaction log if it doesn't exist
    for user in users:
        if user != "transaction_log" and "transaction_log" not in users[user]:
            users[user]["transaction_log"] = []  # Initialize an empty transaction log for each user if it's missing

# Load user data and ensure transaction log exists
users = load_user_data()
ensure_transaction_log()  # Ensure the transaction log is initialized

currency_symbols = {
    "India": "INR",  # India
    "UK": "GBP",     # United Kingdom
    "Saudi": "SAR",   # Saudi Arabia
    "Canada": "CAD",  # Canada
    "US": "USD"       # United States
}

# Exchange rates based on the provided rates
exchange_rates = {
    "SAR": {"INR": 22.43, "GBP": 0.67, "USD": 0.27, "CAD": 0.38},
    "INR": {"SAR": 0.044, "GBP": 0.030, "USD": 0.012, "CAD": 0.017},
    "GBP": {"SAR": 1.49, "INR": 33.33, "USD": 1.50, "CAD": 1.88},
    "USD": {"SAR": 3.75, "INR": 83.33, "GBP": 0.67, "CAD": 1.35},
    "CAD": {"SAR": 2.63, "INR": 58.82, "GBP": 0.53, "USD": 0.74}
}

# Transaction fees per country in their respective currencies
transaction_fees = {
    "India": 128.79,
    "UK": 0.99,
    "US": 1.5,
    "Canada": 1.99,
    "Saudi": 5.6
}

# Initialize session state for logged-in user
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# App Title
st.title("Money Transfer App")

# Function to format the balance with the correct currency
def format_balance(amount, country):
    currency = currency_symbols[country]
    if currency == "INR":
        return f"₹{amount}"
    elif currency == "USD":
        return f"${amount}"
    elif currency == "SAR":
        return f"SAR {amount}"
    elif currency == "GBP":
        return f"£{amount}"
    elif currency == "CAD":
        return f"C${amount}"
    return f"{amount} {currency}"  # Default case

# Go Back to Home Screen Button
def go_back_home():
    if st.button("Go Back to Home Screen"):
        st.session_state["logged_in_user"] = None
        st.session_state["is_admin"] = False
        st.experimental_rerun()

# Admin Login and User Login
if st.session_state["logged_in_user"] is None and not st.session_state["is_admin"]:
    tab = st.radio("Choose an option:", ["Login", "Sign-Up", "Admin"])

    if tab == "Sign-Up":
        st.header("Create a New Account")
        username = st.text_input("Enter your username")
        country = st.selectbox("Select your country", ["India", "UK", "US", "Canada", "Saudi"])
        password = st.text_input("Enter your password", type="password")

        if st.button("Sign Up"):
            if username in users:
                st.error("Username already exists! Please choose another.")
            else:
                users[username] = {"password": password, "country": country, "balance": 100000}
                save_user_data(users)
                st.success("Account created successfully!")

    elif tab == "Login":
        st.header("Log In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state["logged_in_user"] = username
                st.success("Login successful!")

    elif tab == "Admin":
        st.header("Admin Login")
        admin_username = "admin01"
        admin_password = "987654321"

        admin_username_input = st.text_input("Admin Username")
        admin_password_input = st.text_input("Admin Password", type="password")

        if st.button("Admin Login"):
            if admin_username_input == admin_username and admin_password_input == admin_password:
                st.session_state["is_admin"] = True
                st.success("Admin login successful!")
            else:
                st.error("Invalid Admin credentials!")

elif st.session_state["is_admin"]:
    # Admin View
    st.subheader("Admin Dashboard")

    # Displaying all transactions with app fees
    total_app_earnings = 0

    # Show the transactions
    for user, details in users.items():
        if user != "transaction_log":  # Skip admin transaction log
            if details['transaction_log']:
                for transaction in details['transaction_log']:
                    total_app_earnings += transaction_fees[details['country']]  # Accumulate app fees
                    st.write(f"User: {user} - From {transaction['from']} to {transaction['to']} - Amount: {transaction['amount']} {transaction['currency']} - Fee: {transaction['transaction_fee']} {transaction['currency']}")
            else:
                st.write(f"User: {user} - No transactions yet.")
    
    st.write(f"App Earnings from Transaction Fees: ₹{total_app_earnings:.2f}")

    # Show button to toggle user data view
    if st.button("Show User Data"):
        for user, details in users.items():
            if user != "transaction_log":  # Skip admin transaction log
                st.write(f"User: {user} - {details['country']} - Balance: {format_balance(details['balance'], details['country'])}")
                if details['transaction_log']:
                    st.write("Transaction Log:")
                    for transaction in details['transaction_log']:
                        st.write(f"From {transaction['from']} to {transaction['to']} - Amount: {transaction['amount']} {transaction['currency']} - Fee: {transaction['transaction_fee']} {transaction['currency']}")
                else:
                    st.write("No transactions yet.")

    # Go back to home screen button
    go_back_home()

else:  # User Dashboard
    logged_in_user = st.session_state["logged_in_user"]
    user_data = users[logged_in_user]

    st.header(f"Welcome, {logged_in_user}!")
    st.write(f"Country: {user_data['country']}")
    st.write(f"Balance: {format_balance(user_data['balance'], user_data['country'])}")

    # Transfer Money
    st.header("Transfer Money")
    recipient_country = st.selectbox("Select recipient's country", ["India", "UK", "US", "Canada", "Saudi"])
    sender_country = user_data["country"]
    transaction_fee = transaction_fees[sender_country]

    # Ensure transaction log exists
    ensure_transaction_log()

    # Exclude 'transaction_log' from the user list when selecting recipient
    recipient = st.selectbox("Select recipient", [user for user in users.keys() if user != "transaction_log"])

    amount = st.number_input(f"Enter amount to transfer ({sender_country})", min_value=1, step=1)

    total_deduction = 0  # Initialize variable to avoid undefined errors

    if st.button("Calculate"):
        if recipient_country != sender_country:
            converted_amount = amount * exchange_rates[currency_symbols[sender_country]][currency_symbols[recipient_country]]
        else:
            converted_amount = amount

        total_deduction = amount + transaction_fee  # Calculate total deduction here

        st.write(f"Converted Amount: {converted_amount:.2f} {currency_symbols[recipient_country]}")
        st.write(f"Transaction Fee: {transaction_fee} {currency_symbols[sender_country]}")
        st.write(f"Total Deduction: {total_deduction:.2f} {currency_symbols[sender_country]}")

    if st.button("Transfer"):
        # Ensure total_deduction is calculated
        if user_data["balance"] >= total_deduction:
            user_data["balance"] -= total_deduction
            users[logged_in_user] = user_data
            transaction = {
                "from": sender_country,
                "to": recipient_country,
                "amount": amount,
                "currency": currency_symbols[sender_country],
                "transaction_fee": transaction_fee
            }
            users[logged_in_user]["transaction_log"].append(transaction)
            save_user_data(users)

            st.success(f"Successfully transferred {amount} {currency_symbols[sender_country]} to {recipient}")
        else:
            st.error("Insufficient balance!")
    
    # Go back to home screen button
    go_back_home()
