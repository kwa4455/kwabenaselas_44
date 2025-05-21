import streamlit as st

def inject_global_css():
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background: url("https://images.unsplash.com/photo-1558981285-6f0c94958bb6") no-repeat center center fixed;
            background-size: cover;
            color: #fff;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #4CAF50; /* Green */
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)