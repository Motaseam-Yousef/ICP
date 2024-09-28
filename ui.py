import streamlit as st
import requests
import pandas as pd

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
    and **Satisfaction Level**.
""")

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
    
    # Show loading spinner while fetching data
    with st.spinner('Fetching data...'):
        # Prepare the data for API request
        input_data = {
            "AgeRange": list(age_range),
            "Gender": gender,
            "Cities": cities,
            "Price": price
        }

        # Make POST request to Flask API
        api_url = "http://127.0.0.1:5050/customer_quality"  # Replace with your actual API URL
        response = requests.post(api_url, json=input_data)

    # Check if the request was successful
    if response.status_code == 200:
        # Get JSON response and load it into a DataFrame
        result = response.json()
        df = pd.DataFrame(result)

        # Display the result
        st.success("Top customers have been successfully ranked by their quality score!")
        st.write("The following customers have been ranked based on their **Customer Quality Score**:")

        # Display the sorted customer quality score as an interactive table
        st.dataframe(df.style.background_gradient(cmap="Greens", subset=["Customer Quality Score"]))

    else:
        st.error(f"Error {response.status_code}: Could not fetch data from the API.")
