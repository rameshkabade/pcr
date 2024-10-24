import streamlit as st
import pandas as pd
import time

st.set_page_config(layout="wide")
##st.title("Live Status")
st.markdown("<h1 style='font-size: 24px;'>Live Status</h1>", unsafe_allow_html=True)
##st.write("This is the main content of your app.")

# Add custom CSS for dark theme
st.markdown("""
    <style>
        /* Dark theme styles */
        .stDataFrame {
            background-color: #0e1117;
        }
        .stDataFrame [data-testid="stDataFrame"] {
            background-color: #0e1117;
        }
        /* Style for all cells including DateTime */
        .stDataFrame [data-testid="stDataFrame"] td {
            background-color: #0e1117 !important;
            color: #ffffff !important;
        }
        /* Style for headers */
        .stDataFrame [data-testid="stDataFrame"] th {
            background-color: #1e2130 !important;
            color: #ffffff !important;
        }
        /* Hide index column */
        .stDataFrame [data-testid="stDataFrame"] td:first-child {
            display: none;
        }
        .stDataFrame [data-testid="stDataFrame"] th:first-child {
            display: none;
        }
        /* Override any white backgrounds */
        [data-testid="stAppViewContainer"] {
            background-color: #0e1117;
        }
    </style>
""", unsafe_allow_html=True)

def color_negative_red_positive_green(val):
    if isinstance(val, (int, float)):
        color = 'red' if val < 0 else '#00ff00' if val > 0 else '#ffffff'
        return f'color: {color}'
    return 'color: #ffffff'

def load_csv(file_name):
    try:
        df = pd.read_csv(file_name)
        df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
        # Sort by DateTime in ascending order (oldest first)
        df = df.sort_values(by='DateTime', ascending=True)
        df = df.round(2)
        return df
    except Exception as e:
        st.error(f"Error loading {file_name}: {str(e)}")
        return pd.DataFrame()

def display_data(df, title):
    if df.empty:
        st.warning(f"No data available for {title}")
        return
        
    # Take the last rows based on rows_to_display setting
    display_df = df.tail(10).copy()
    display_df['DateTime'] = display_df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    format_dict = {
        'PCR1': '{:.2f}',
        'PCR2': '{:.2f}',
        'PCR3': '{:.2f}',
        'ZSCORE': '{:.2f}',
        'RSI': '{:.2f}',
        'PE_M2M': '{:.2f}'
    }
    
    # Style the dataframe
    df_styled = display_df.style.format(format_dict)
    df_styled = df_styled.map(color_negative_red_positive_green)
    
    # Apply background color to all cells
    df_styled = df_styled.set_properties(**{
        'background-color': '#0e1117',
        'color': '#ffffff'
    })
    
    # Highlight the latest row
    def highlight_last_row(x):
        return ['background-color: #1e2130' if i == len(x) - 1 else 'background-color: #0e1117' 
                for i in range(len(x))]
    
    df_styled = df_styled.apply(highlight_last_row, axis=0)
    
    # Display the data
    st.subheader(f"{title} (Latest: {display_df['DateTime'].iloc[-1]})")
    st.dataframe(
        df_styled,
        use_container_width=True,
        height=400
    )

    # Display metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Latest PCR1", f"{display_df['PCR1'].iloc[-1]:.2f}", 
                 f"{display_df['PCR1'].iloc[-1] - display_df['PCR1'].iloc[-2]:.2f}")
    with col2:
        st.metric("Latest ZSCORE", f"{display_df['ZSCORE'].iloc[-1]:.2f}", 
                 f"{display_df['ZSCORE'].iloc[-1] - display_df['ZSCORE'].iloc[-2]:.2f}")
    with col3:
        st.metric("Latest RSI", f"{display_df['RSI'].iloc[-1]:.2f}", 
                 f"{display_df['RSI'].iloc[-1] - display_df['RSI'].iloc[-2]:.2f}")

# Sidebar configuration
##with st.sidebar:
####    st.title("Dashboard Settings")
####    refresh_rate = st.slider("Refresh Rate (seconds)", 
####                           min_value=5, 
####                           max_value=60, 
####                           value=30)
##    rows_to_display = st.slider("Number of Rows to Display", 
##                              min_value=10, 
##                              max_value=100, 
##                              value=50)

# Create a placeholder for the data
placeholder = st.empty()

# Main loop for continuous updates
while True:
    with placeholder.container():
        df_nifty = load_csv('NIFTY.csv')
        df_banknifty = load_csv('BANKNIFTY.csv')
        
        col1, col2 = st.columns(2)
        
        with col1:
            display_data(df_nifty, "NIFTY")
        
        with col2:
            display_data(df_banknifty, "BANKNIFTY")
        
##        st.info(f"Data will automatically refresh")
        st.markdown(
            """
            <div style='text-align: center; color: gray; font-size: 16px;'>
                Copyright © 2024   Ramesh Kabade,  Bengaluru, INDIA.  All rights reserved.   📞 (+91) 988-642-0005
            </div>
            """,
            unsafe_allow_html=True
            )
    time.sleep(30)
