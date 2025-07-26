import streamlit as st
import streamlit.components.v1 as components

def inject_google_analytics(measurement_id: str):
    components.html(f"""
      <!-- Google tag (gtag.js) -->
      <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
      <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{measurement_id}');
      </script>
    """, height=0, scrolling=False)
