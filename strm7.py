
import streamlit as st
import pandas as pd
import time
import requests
import base64
import io
import os
import sys

st.set_page_config(
    layout="wide",
    page_title="Live Status",
    page_icon="📱",
)



def display_data(df, title):
    # Check if the DataFrame has sufficient data
    if df.empty or len(df) < 2:
        st.warning(f"No data available for {title}")
        return

    # Ensure unique index to prevent styling errors
    if not df.index.is_unique:
        df = df[~df.index.duplicated(keep='first')]

    # Reverse the DataFrame so the latest data appears first
    display_df = df[::-1]

    # Get the most recent datetime for display
    dispdate = pd.to_datetime(display_df.index[0]).strftime('%Y-%m-%d %H:%M')

    # Define formatting for specific columns
    format_dict = {
        'CLOSE': '{:.2f}',
        'PCR_VOL': '{:.2f}',
        'PCR_OI': '{:.2f}',
        'PCR_COI': '{:.2f}',
        'ZSCORE': '{:.2f}',
        'RSI': '{:.2f}',
        'SIGNAL': '{}'
    }

    # Define column color style
    def color_columns(col):
        if col.name in ['ZSCORE', 'RSI', 'PCR_COI']:
            return ['color: green' if v > prev_v else 'color: red' for v, prev_v in zip(col, col.shift())]
        return [''] * len(col)
    
    # Highlight the last row (now the first row in reversed order)
    def highlight_last_row(data):
        colors = ['background-color: #1D215E'] + ['background-color: black'] * (len(data) - 1)
        return colors

    # Apply styles with datetime as the index
    df_styled = display_df.style.format(format_dict) \
                                .apply(color_columns) \
                                .apply(highlight_last_row, axis=0) \
                                .set_properties(**{'text-align': 'center'})

    # Display the styled DataFrame with latest data at the top
    st.subheader(f"{title} ({dispdate})")
    st.dataframe(df_styled, use_container_width=True, height=400)




# Create a placeholder for the data
placeholder = st.empty()

# Main loop for continuous updates
while True:
    with placeholder.container():

        repo_owner = os.getenv("DB_USERNAME")
        token      = os.getenv("DB_TOKEN")

        if not token:
            st.write("Token not found. Please check the environment variable.")

        repo_name = "data"
        file_path = "NIFTY.csv"

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        headers = {"Authorization": f"token {token}"}

        response = requests.get(url, headers=headers)
        print(response)
        if response.status_code == 200:
            content = response.json()
            sha = content['sha']
            file_content = base64.b64decode(content['content'])
            df_nifty = pd.read_csv(io.StringIO(file_content.decode('utf-8')), index_col='datetime')
        else :
            df_nifty = pd.DataFrame()
            print(response)


        file_path = "BANKNIFTY.csv"
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            sha = content['sha']
            file_content = base64.b64decode(content['content'])
            df_banknifty = pd.read_csv(io.StringIO(file_content.decode('utf-8')), index_col='datetime')
        else :
            df_banknifty =pd.DataFrame()
            print(response)

        col1, col2 = st.columns(2)
        
        with col1:
            display_data(df_nifty, "NIFTY")
        
        with col2:
            display_data(df_banknifty, "BANKNIFTY")
        
        st.info("Data will automatically refresh")
        st.markdown(
            """
            <div style='text-align: center; color: gray; font-size: 16px;'>
                Copyright © 2024 <span style='color: #1e90ff;'>Ramesh Kabade</span>, Bengaluru, INDIA. All rights reserved. 📞 (+91) 988-642-0005
            </div>
            """,
            unsafe_allow_html=True
        )
    sys.exit(1)
    time.sleep(30)
