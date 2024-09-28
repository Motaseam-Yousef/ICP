from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Initialize the Flask app
app = Flask(__name__)

# Define the mappings for Gender, Membership Type, Satisfaction Level, Discount Applied, and City
gender_map = {'Female': 1, 'Male': 0}
membership_map = {'Gold': 5, 'Silver': 3, 'Bronze': 1}
satisfaction_map = {'Satisfied': 1, 'Unsatisfied': -1, 'Neutral': 0}
discount_map = {True: 1, False: 0}
city_map = {
    'Houston': 1,
    'Miami': 2,
    'San Francisco': 3,
    'Chicago': 4,
    'Los Angeles': 5,
    'New York': 6
}

# Specify the full file path to the CSV file
file_path = r"C:\Users\Motasem-PC\Desktop\ICP\data\E-commerce Customer.csv"

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(file_path)

# Mapping the categorical columns in the DataFrame
def apply_mappings(df):
    df['Gender'] = df['Gender'].map(gender_map)
    df['Membership Type'] = df['Membership Type'].map(membership_map)
    df['Satisfaction Level'] = df['Satisfaction Level'].map(satisfaction_map)
    df['Discount Applied'] = df['Discount Applied'].map(discount_map)
    df['City'] = df['City'].map(city_map)
    return df

# Apply the mappings once to the dataset
df = apply_mappings(df)

# Define the scoring equation for customer quality
def calculate_customer_quality(df):
    # Initialize scaler and scale the necessary columns
    scaler = MinMaxScaler((0, 100))
    
    # Create a subset of the columns to scale
    df[['Total Spend Scaled', 'Membership Scaled', 'Items Purchased Scaled']] = scaler.fit_transform(
        df[['Total Spend', 'Membership Type', 'Items Purchased']]
    )
    
    # Calculate the quality score
    df['Customer Quality Score'] = (
        0.4 * df['Total Spend Scaled'] +           # 40% weight to Total Spend (scaled)
        0.3 * df['Membership Scaled'] +            # 30% weight to Membership Type (scaled)
        0.3 * df['Items Purchased Scaled']         # 30% weight to Items Purchased (scaled)
    )
    return df

# Route to get customer scores
@app.route('/customer_quality', methods=['POST'])
def customer_quality():
    # Get the user input from the request
    user_input = request.json
    age_range = user_input['AgeRange']  # Expecting something like [20, 40]
    gender = user_input['Gender']       # Can be ['Male'], ['Female'], or ['Male', 'Female']
    cities = user_input['Cities']       # List of cities ['New York', 'Miami', 'Chicago']

    # Step 1: Filter customers based on user inputs
    filtered_customers = df[
        (df['Gender'].isin([gender_map[g] for g in gender])) &               # One or both genders
        (df['Age'].between(age_range[0], age_range[1])) &                    # Age range
        (df['City'].isin([city_map[city] for city in cities]))               # One or more cities
    ]

    if filtered_customers.empty:
        return jsonify({"message": "No customers found matching the criteria."})

    # Step 2: Calculate the Customer Quality Score for the filtered customers
    filtered_customers = calculate_customer_quality(filtered_customers)

    # Step 3: Sort the customers by their quality score in descending order and filter by score > 55
    sorted_customers = filtered_customers.sort_values(by='Customer Quality Score', ascending=False)
    sorted_customers = sorted_customers[sorted_customers['Customer Quality Score'] > 55]

    if sorted_customers.empty:
        return jsonify({"message": "No customers with a score greater than 55."})

    # Prepare the result with Customer ID and the corresponding Quality Score
    result = pd.DataFrame({
        'Customer ID': sorted_customers['Customer ID'],
        'Customer Quality Score': sorted_customers['Customer Quality Score'].round(2)
    })

    # Convert the result to a list of dictionaries and return as JSON
    return jsonify(result.to_dict(orient='records'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5050)
