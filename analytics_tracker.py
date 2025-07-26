import streamlit as st

def inject_google_analytics(measurement_id: str):
    """
    Injects Google Analytics tracking code into the Streamlit app.

    Parameters:
    - measurement_id (str): Your Google Analytics Measurement ID (e.g., 'G-XXXXXXX').
    """
    ga_code = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{measurement_id}');
    </script>
    """
    st.markdown(ga_code, unsafe_allow_html=True)

#Added analytics_tracker.py for Google Analytics integration
