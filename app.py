import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Silver Analytics Hub", layout="wide")

@st.cache_data
def load_data():
    
    prices_df = pd.read_csv('historical_silver_price.csv')
    sales_df = pd.read_csv('state_wise_silver_purchased_kg.csv')
    
    prices_df['Date'] = pd.to_datetime(prices_df['Month'] + ' ' + prices_df['Year'].astype(str))
    return prices_df, sales_df

prices_df, sales_df = load_data()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Silver Price Calculator", "Silver Sales Dashboard"])

if page == "Silver Price Calculator":
    st.title("Silver Price Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Enter Weight", min_value=0.0, value=1.0)
        unit = st.selectbox("Unit", ["Grams", "Kilograms"])
        price_per_gram = st.number_input("Current Price per Gram (INR)", min_value=0.0, value=95.0)
    
    total_grams = weight if unit == "Grams" else weight * 1000
    total_cost_inr = total_grams * price_per_gram
    
    with col2:
        st.subheader("Calculation Result")
        currency = st.selectbox("Currency Selection", ["INR", "USD"])
        rate = 0.012 
        final_val = total_cost_inr if currency == "INR" else total_cost_inr * rate
        st.metric(label=f"Total Cost ({currency})", value=f"{final_val:,.2f}")

    st.markdown("---")
    st.subheader("Historical Price Trends")
    
    price_filter = st.selectbox("Filter by Price Range (INR per kg):", 
                                ["Show All", "≤ 20,000", "20,000 - 30,000", "≥ 30,000"])
    
    filtered_df = prices_df.copy()
    if price_filter == "≤ 20,000":
        filtered_df = prices_df[prices_df['Silver_Price_INR_per_kg'] <= 20000]
    elif price_filter == "20,000 - 30,000":
        filtered_df = prices_df[(prices_df['Silver_Price_INR_per_kg'] > 20000) & (prices_df['Silver_Price_INR_per_kg'] < 30000)]
    elif price_filter == "≥ 30,000":
        filtered_df = prices_df[prices_df['Silver_Price_INR_per_kg'] >= 30000]

    st.line_chart(filtered_df.set_index('Date')['Silver_Price_INR_per_kg'])

else:
    st.title("Silver Sales Insights")

    st.subheader("India State-wise Sales (Choropleth)")
    try:
        india_geo = gpd.read_file("india_state_geo.json")
        merged = india_geo.merge(sales_df, left_on="ST_NM", right_on="State")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        merged.plot(column='Silver_Purchased_kg', cmap='Blues', legend=True, 
                    edgecolor='black', linewidth=0.3, ax=ax)
        plt.axis('off')
        st.pyplot(fig)
    except:
        st.error("Error")

    st.subheader("Top 5 States (Highest Sales)")
    top_5 = sales_df.sort_values(by='Silver_Purchased_kg', ascending=False).head(5)
    st.bar_chart(top_5.set_index('State')['Silver_Purchased_kg'])

    st.subheader("January Month Silver Sales")
    jan_df = prices_df[prices_df['Month'] == 'Jan']
    
    st.dataframe(jan_df[['Year', 'Month', 'Silver_Price_INR_per_kg']])
    
    st.line_chart(jan_df.set_index('Year')['Silver_Price_INR_per_kg'])