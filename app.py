from flask import Flask, render_template, request, redirect, flash
import sqlite3
import os

# Create a Flask application
app = Flask(__name__)
app.secret_key = 'jatin_158' 

# SQLite database file name
DB_NAME = 'expenses.db'

# Initialize the database using schema.sql (runs only once)
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        with open('schema.sql') as f:
            conn.executescript(f.read())

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# Route to Add Expense
@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        # Get values from form
        date = request.form['date']
        category = request.form['category']
        amount = float(request.form['amount'])

        # Save to database
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)",
                         (date, category, amount))
            conn.commit()
        flash("Expense added successfully", "success")
        return redirect('/')
    return render_template('add_expense.html')

# Route to Set Budget
@app.route('/budget', methods=['GET', 'POST'])
def set_budget():
    if request.method == 'POST':
        # Get values from form
        month = request.form['month']
        category = request.form['category']
        amount = float(request.form['amount'])

        # Insert or update the budget in the database
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                INSERT INTO budgets (month, category, amount) 
                VALUES (?, ?, ?)
                ON CONFLICT(month, category) DO UPDATE SET amount=excluded.amount
            """, (month, category, amount))
            conn.commit()
        flash("Budget set successfully", "success")
        return redirect('/')
    return render_template('set_budget.html')

# Route to Generate Monthly Report
@app.route('/report', methods=['GET'])
def report():
    month = request.args.get('month')
    report_data = []

    if month:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()

            # Get total expenses by category for the selected month
            cursor.execute("""
                SELECT category, SUM(amount) 
                FROM expenses 
                WHERE strftime('%Y-%m', date) = ?
                GROUP BY category
            """, (month,))
            expenses = dict(cursor.fetchall())

            # Get budgets by category for the selected month
            cursor.execute("""
                SELECT category, amount FROM budgets WHERE month = ?
            """, (month,))
            budgets = dict(cursor.fetchall())

            # Combine both expenses and budgets into one report
            categories = set(expenses.keys()).union(budgets.keys())

            for cat in categories:
                spent = expenses.get(cat, 0)
                budget = budgets.get(cat, 0)
                remaining = budget - spent
                report_data.append((cat, spent, budget, remaining))

                # Alert if only 10% or less of the budget is left
                if budget > 0 and (budget - spent) / budget <= 0.1:
                    flash(f"Only Less than 10% budget left for {cat}!", "warning")

    return render_template('report.html', report_data=report_data)

# Route to View All Expenses
@app.route('/expenses')
def view_expenses():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, category, amount FROM expenses ORDER BY date DESC")
        expenses = cursor.fetchall()
    return render_template('view_expenses.html', expenses=expenses)

# Run the app
if __name__ == '__main__':
    # Create the database only if it doesn't exist
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(debug=True)
