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
    if df.empty or len(df) < 2:
        st.warning(f"No data available for {title}")
        return

    if not df.index.is_unique:
        df = df[~df.index.duplicated(keep='first')]

    display_df = df.copy() ##df[::-1]
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
        """
        Color formatter for DataFrame columns:
        - For RSI, ZSCORE, PCR_COI columns:
          - Green if current value > previous value
          - Red if current value < previous value
          - No color if equal
        
        Args:
            col: pandas Series (DataFrame column)
        Returns:
            list: List of CSS color styles for each row
        """
        if col.name in ['ZSCORE', 'RSI', 'PCR_COI']:
            styles = []
            for i in range(len(col)):
                if i == 0:  # First row has no previous value
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
                    print(f"Color for {i}, {current},  {previous}", styles)
            return styles
        
        return [''] * len(col)


    def highlight_last_row(data):
        return ['background-color: #1D215E' if i == len(data.index) - 1 else 'background-color: black' 
                for i in range(len(data.index))]

    df_styled = display_df.style.format(format_dict) \
                                .apply(color_columns) \
                                .apply(highlight_last_row, axis=0) \
                                .set_properties(**{'text-align': 'center'})

    st.subheader(f"{title} ({dispdate})")
    st.dataframe(df_styled, use_container_width=True, height=400)



placeholder = st.empty()

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
    time.sleep(60)
