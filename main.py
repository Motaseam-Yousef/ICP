import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Page Configuration
st.set_page_config(page_title="Customer Quality Scoring App", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
    }
    .stTextInput, .stSelectbox, .stNumberInput {
        font-size: 1.2em;
    }
    h1 {
        color: #4CAF50;
    }
    .stForm {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit UI Title and Description
st.title("📊 Customer Quality Scoring App")
st.write("""
    Welcome to the **Customer Quality Scoring App**. Use the form below to filter customers and 
    get a ranked list of the highest quality customers based on their **Total Spend**, **Membership Type**, 
    and **Items Purchased**.
""")

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

# Load the CSV file into a pandas DataFrame (Upload this file to Streamlit Cloud as well)
@st.cache_data
def load_data():
    file_path = "data/E-commerce Customer.csv"  # Make sure this file is available in your repo
    df = pd.read_csv(file_path)
    
    # Apply mappings
    df['Gender'] = df['Gender'].map(gender_map)
    df['Membership Type'] = df['Membership Type'].map(membership_map)
    df['Satisfaction Level'] = df['Satisfaction Level'].map(satisfaction_map)
    df['Discount Applied'] = df['Discount Applied'].map(discount_map)
    df['City'] = df['City'].map(city_map)
    
    return df

# Load data
df = load_data()

# Define the scoring equation for customer quality
def calculate_customer_quality(filtered_customers):
    # Normalize Total Spend, Membership Type, and Items Purchased
    scaler = MinMaxScaler((0, 100))
    filtered_customers['Total Spend Scaled'] = scaler.fit_transform(filtered_customers[['Total Spend']])
    filtered_customers['Membership Scaled'] = scaler.fit_transform(filtered_customers[['Membership Type']])
    filtered_customers['Items Purchased Scaled'] = scaler.fit_transform(filtered_customers[['Items Purchased']])
    
    # Calculate the quality score
    filtered_customers['Customer Quality Score'] = (
        0.4 * filtered_customers['Total Spend Scaled'] +     # 40% weight to Total Spend (scaled)
        0.25 * filtered_customers['Membership Scaled'] +     # 25% weight to Membership Type (scaled)
        0.3 * filtered_customers['Items Purchased Scaled'] + # 30% weight to Items Purchased (scaled)
        0.05 * filtered_customers['Satisfaction Level']      # 5% weight to Satisfaction Level (optional)
    )
    return filtered_customers

# Sidebar for Form Input
with st.sidebar:
    st.header("🔍 Filter Customers")
    
    # Age Range input
    age_range = st.slider("Select Age Range", 18, 100, (25, 40))

    # Gender input
    gender = st.multiselect(
        "Select Gender",
        options=["Male", "Female"],
        default=["Male", "Female"]
    )

    # City selection
    cities = st.multiselect(
        "Select Cities",
        options=["New York", "Los Angeles", "Chicago", "Miami", "San Francisco", "Houston"],
        default=["New York", "Los Angeles"]
    )

    # Price input
    price = st.number_input("Enter Price (in $)", min_value=0, value=1000)

    # Submit button
    submitted = st.button("Submit")

# Main Content
if submitted:
    st.header("📈 Customer Quality Score Results")
    
    # Filter customers based on user inputs
    filtered_customers = df[
        (df['Gender'].isin([gender_map[g] for g in gender])) &               # One or both genders
        (df['Age'].between(age_range[0], age_range[1])) &                    # Age range
        (df['City'].isin([city_map[city] for city in cities]))               # One or more cities
    ]

    if filtered_customers.empty:
        st.error("No customers found matching the criteria.")
    else:
        # Step 2: Calculate the Customer Quality Score for the filtered customers
        filtered_customers = calculate_customer_quality(filtered_customers)

        # Step 3: Sort the customers by their quality score in descending order
        sorted_customers = filtered_customers.sort_values(by='Customer Quality Score', ascending=False)

        # Prepare the result with Customer ID and the corresponding Quality Score
        result = pd.DataFrame({
            'Customer ID': sorted_customers['Customer ID'],
            'Customer Quality Score': sorted_customers['Customer Quality Score'].round(2)
        })

        # Display the result
        st.success("Top customers have been successfully ranked by their quality score!")
        st.write("The following customers have been ranked based on their **Customer Quality Score**:")

        # Display the sorted customer quality score as an interactive table
        st.dataframe(result.style.background_gradient(cmap="Greens", subset=["Customer Quality Score"]))
        