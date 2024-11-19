import streamlit as st
import pandas as pd
import time
import requests
import base64
import io
import os
import sys

DEBUG = 0 

st.set_page_config(
    layout="wide",
    page_title="Live Status",
    page_icon="📱",
)

# Add custom HTML/JavaScript for auto-scrolling that works with Streamlit
st.markdown("""
    <style>
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Make dataframe headers more compact */
        .stDataFrame thead th {
            padding-top: 2px !important;
            padding-bottom: 2px !important;
        }
        
        /* Reduce padding in dataframe cells */
        .stDataFrame tbody td {
            padding-top: 2px !important;
            padding-bottom: 2px !important;
        }
        
        /* Make subheaders more compact and smaller */
        .st-emotion-cache-1wivap2 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Custom class for smaller title */
        .small-title {
            font-size: 18px !important;
            margin: 0 !important;
            padding: 0 !important;
            color: orange !important;
            font-weight: 500 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Add JavaScript for scrolling - using Streamlit's components
js_code = """
    <script>
        function scroll_to_bottom() {
            window.parent.document.querySelector('.main').scrollTo(0, window.parent.document.querySelector('.main').scrollHeight);
        }
        window.addEventListener('load', function() {
            setTimeout(scroll_to_bottom, 100);
            setTimeout(scroll_to_bottom, 500);
            setTimeout(scroll_to_bottom, 1000);
        });
    </script>
"""
st.components.v1.html(js_code, height=0)

def display_data(df, title):
    if df.empty or len(df) < 2:
        st.warning(f"No data available for {title}")
        return

    if not df.index.is_unique:
        df = df[~df.index.duplicated(keep='first')]

    # Keep only the last 4 rows for a more compact view
    display_df = df.tail(3).copy()
    dispdate = pd.to_datetime(display_df.index[0]).strftime('%Y-%m-%d %H:%M')

    format_dict = {
        'CLOSE': '{:.2f}',
        'ATM' : '{:.0f}',
        'PCR_VOL': '{:.2f}',
        'PCR_OI': '{:.2f}',
        'PCR_COI': '{:.2f}',
        'ZSCORE': '{:.2f}',
        'RSI': '{:.2f}',
        'SIGNAL': '{}',
        'SUP' : '{:.0f}',
        'RES' : '{:.0f}'
    }

    def color_columns(col):
        if col.name in ['ZSCORE', 'RSI', 'PCR_COI', 'PCR_OI']:
            styles = []
            for i in range(len(col)):
                if i == 0:
                    styles.append('')
                else:
                    current = col.iloc[i]
                    previous = col.iloc[i-1]
                    
                    if current > previous:
                        styles.append('color: green')
                    elif current < previous:
                        styles.append('color: red')
                    else:
                        styles.append('')
            return styles
        
        return [''] * len(col)

    def highlight_last_row(data):
        return ['background-color: #1D215E' if i == len(data.index) - 1 else 'background-color: black' 
                for i in range(len(data.index))]

    df_styled = display_df.style.format(format_dict) \
                                .apply(color_columns) \
                                .apply(highlight_last_row, axis=0) \
                                .set_properties(**{'text-align': 'center'})

    # Using markdown for smaller title instead of subheader
    #st.markdown(f"<h3 class='small-title'>{title}   ( {dispdate} )</h3>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <h3 class='small-title'>
            {title} <span style='font-size: 12px;'>{dispdate}</span>
        </h3>
        """,
        unsafe_allow_html=True
    )

    
    st.dataframe(df_styled, use_container_width=True, height=140)

def fetch_data(repo_owner, token, repo_name, file_path):
    if DEBUG == 0:
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        headers = {"Authorization": f"token {token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            file_content = base64.b64decode(content['content'])
            return pd.read_csv(io.StringIO(file_content.decode('utf-8')), index_col='datetime')
        else:
            print(f"Error fetching {file_path}: {response.status_code}")
            return pd.DataFrame()
    else:
        print(f".\\data\\{file_path}")
        return pd.read_csv(f".\\data\\{file_path}", index_col='datetime')

# Create a placeholder at the bottom that will help with scrolling
placeholder = st.empty()
bottom_placeholder = st.empty()

while True:
    with placeholder.container():
        repo_owner = os.getenv("DB_USERNAME")
        token = os.getenv("DB_TOKEN")

        if not token and DEBUG == 0:
            st.write("Token not found. Please check the environment variable.")
            sys.exit(1)

        repo_name = "data"
        indices = {
            "NIFTY": "NIFTY.csv",
            "BANKNIFTY": "BANKNIFTY.csv",
            "FINNIFTY": "FINNIFTY.csv",
            "MIDCPNIFTY": "MIDCPNIFTY.csv"
        }
        
        # Fetch data for all indices
        dataframes = {
            index: fetch_data(repo_owner, token, repo_name, file_path)
            for index, file_path in indices.items()
        }

        # Display all indices
        for index, df in dataframes.items():
            display_data(df, index)
            
##        st.info("Data will automatically refresh")

    # Footer always displayed at the bottom
    with bottom_placeholder:
        st.markdown(
            """
            <div style='text-align: center; color: gray; font-size: 16px;'>
                Copyright © 2024 <span style='color: #1e90ff;'>Ramesh Kabade</span>, Bengaluru, INDIA. All rights reserved. 📞 (+91) 988-642-0005
            </div>
            """,
            unsafe_allow_html=True
        )
    time.sleep(30)
