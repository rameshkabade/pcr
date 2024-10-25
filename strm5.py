import streamlit as st
import pandas as pd
import time
import requests
import base64
import io
##from datetime import datetime as dt
##from datetime import timedelta as td

#st.set_page_config(layout="wide")
##st.title("Live Status")
# Configure the page with wide layout
st.set_page_config(
    layout="wide",
    page_title="Live Status",
    page_icon="📱",
)


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
        /* Style for all cells including datetime */
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
##        color = 'red' if val < 0 else '#00ff00' if val > 0 else '#ffffff'
        color = 'red' if val < 0 else 'green' if val > 0 else '#ffffff'
        return f'color: {color}'
    return 'color: #ffffff'

##def load_csv(file_name):
##    try:
##        df = pd.read_csv(file_name)
##        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
##        # Sort by datetime in ascending order (oldest first)
##        df = df.sort_values(by='datetime', ascending=True)
##        df = df.round(2)
##        return df
##    except Exception as e:
##        st.error(f"Error loading {file_name}: {str(e)}")
##        return pd.DataFrame()

def display_data(df, title):
    if df.empty:
        st.warning(f"No data available for {title}")
        return

        
    # Take the last rows based on rows_to_display setting
    display_df = df.tail(10).copy()
    dispdate =  pd.to_datetime(display_df.index[-1]).strftime('%Y-%m-%d %H:%M')
    
##    print(display_df['datetime'].iloc[-1])
##    print(display_df)
    
    format_dict = {
        'close': '{:.2f}',
        'PCR_OI': '{:.2f}',
        'PCR_COI': '{:.2f}',
        'PCR_VOL': '{:.2f}',
        'zScore': '{:.2f}',
        'RSI': '{:.2f}'
    }
    
    # Style the dataframe
    df_styled = display_df.style.format(format_dict)
    df_styled = df_styled.map(color_negative_red_positive_green,subset=['PCR_COI', 'RSI', 'zScore'])
    
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
    st.subheader(f"{title} (Latest: {dispdate})")
    st.dataframe(
        df_styled,
        use_container_width=True,
        height=400
    )

    # Display metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Latest PCR_COI", f"{display_df['PCR_COI'].iloc[-1]:.2f}", 
                 f"{display_df['PCR_COI'].iloc[-1] - display_df['PCR_COI'].iloc[-2]:.2f}")
    with col2:
        st.metric("Latest zScore", f"{display_df['zScore'].iloc[-1]:.2f}", 
                 f"{display_df['zScore'].iloc[-1] - display_df['zScore'].iloc[-2]:.2f}")
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
##        df_nifty = load_csv('NIFTY.csv')
##        df_banknifty = load_csv('BANKNIFTY.csv')

        repo_owner = "rameshkabade"
        repo_name = "data"
        file_path = "NIFTY.csv"
        token = "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"  # Replace with your actual GitHub token


        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        headers = {"Authorization": f"token {token}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            sha = content['sha']  # Get the file's SHA for updating
            file_content = base64.b64decode(content['content'])

            df_nifty =  pd.read_csv(io.StringIO(file_content.decode('utf-8')), index_col='datetime')
##            print(df_nifty)
##
##            # Ensure new_data also uses the same index column
##            df_nifty.set_index('datetime', inplace=True)


        file_path = "BANKNIFTY.csv"

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            sha = content['sha']  # Get the file's SHA for updating
            file_content = base64.b64decode(content['content'])

            df_banknifty =  pd.read_csv(io.StringIO(file_content.decode('utf-8')), index_col='datetime')

##            print(df_banknifty)

##            # Ensure new_data also uses the same index column
##            df_banknifty.set_index('datetime', inplace=True)




        
        col1, col2 = st.columns(2)
        
        with col1:
            display_data(df_nifty, "NIFTY")
        
        with col2:
            display_data(df_banknifty, "BANKNIFTY")
        
        st.info(f"Data will automatically refresh")
        st.markdown(
            """
            <div style='text-align: center; color: gray; font-size: 16px;'>
                Copyright © 2024   Ramesh Kabade,  Bengaluru, INDIA.  All rights reserved.   📞 (+91) 988-642-0005
            </div>
            """,
            unsafe_allow_html=True
            )
    time.sleep(30)
