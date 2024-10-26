import streamlit as st
import pandas as pd
import time
import requests
import base64
import io

st.set_page_config(
    layout="wide",
    page_title="Live Status",
    page_icon="📱",
)


def display_data(df, title):
    if df.empty:
        st.warning(f"No data available for {title}")
        return

    display_df = df.tail(10).copy()
    dispdate = pd.to_datetime(display_df.index[-1]).strftime('%Y-%m-%d %H:%M')
    
    format_dict = {
        'close': '{:.2f}',
        'PCR_VOL': '{:.2f}',
        'PCR_OI': '{:.2f}',
        'PCR_COI': '{:.2f}',
        'ZSCORE': '{:.2f}',
        'RSI': '{:.2f}'
    }
    
    df_styled = display_df.style.format(format_dict)
    df_styled = df_styled.map(lambda x: 'color: green' if x > 0 else 'color: red', subset=['ZSCORE', 'RSI', 'PCR_COI'])
    df_styled = df_styled.set_properties(        **{ 'text-align': 'center'})


    
    # Highlight the latest row
    def highlight_last_row(x):
        return ['background-color: #1D215E' if i == len(x) - 1 else 'background-color: black' 
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
    col1, col2, col3 , col4 = st.columns(4)
    with col1:
        st.metric("Latest PCR_COI", f"{display_df['PCR_COI'].iloc[-1]:.2f}", 
                 f"{display_df['PCR_COI'].iloc[-1] - display_df['PCR_COI'].iloc[-2]:.2f}")
    with col2:
        st.metric("Latest RSI", f"{display_df['RSI'].iloc[-1]:.2f}", 
                 f"{display_df['RSI'].iloc[-1] - display_df['RSI'].iloc[-2]:.2f}")
    with col3:
        st.metric("Latest ZSCORE", f"{display_df['ZSCORE'].iloc[-1]:.2f}", 
                 f"{display_df['ZSCORE'].iloc[-1] - display_df['ZSCORE'].iloc[-2]:.2f}")

# Create a placeholder for the data
placeholder = st.empty()

# Main loop for continuous updates
while True:
    with placeholder.container():
        repo_owner = "rameshkabade"
        repo_name = "data"
        file_path = "NIFTY.csv"
        token = "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"

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        print(url)
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

    time.sleep(30)
