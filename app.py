from flask import Flask, render_template, request, redirect, jsonify
from sqlalchemy import func
from models import db, Expense
from datetime import datetime
import os
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create Database if it doesn't exist
with app.app_context():
    if not os.path.exists('instance/expenses.db'):
        db.create_all()

# ROUTE 1: The Dashboard (Read Data)
@app.route('/')
def home():
    # Fetch all expenses from DB, sorted by newest first
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('index.html', expenses=expenses)

# ROUTE 2: Add Expense (Create Data)
@app.route('/add', methods=['POST'])
def add():
    # Get data from the HTML form
    date_str = request.form['date']
    category = request.form['category']
    amount = request.form['amount']
    
    # Convert date string to Python date object
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Create a new Expense record
    new_expense = Expense(date=date_obj, category=category, amount=int(amount))

    # Save to Database
    db.session.add(new_expense)
    db.session.commit()

    # Go back to the dashboard
    return redirect('/')

# ROUTE 3: Data for Chart (Analysis)
@app.route('/expense_data')
def expense_data():
    # Query: SELECT category, SUM(amount) FROM expense GROUP BY category
    data = db.session.query(Expense.category, func.sum(Expense.amount))\
                     .group_by(Expense.category).all()
    
    # Format data for JavaScript: { "Food": 500, "Travel": 200 }
    category_data = {row[0]: row[1] for row in data}
    return jsonify(category_data)

if __name__ == "__main__":
    app.run(debug=True)