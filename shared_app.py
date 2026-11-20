import streamlit as st

from panels.Crisis_Correlation_Heatmap import show_selected_crisis, crises

st.set_page_config(
    page_title="Financial Stress Dashboard",
    layout="wide",
)

st.title("Financial Stress Dashboard")

tab1, tab2, tab3, tab4 = st.tabs([
    "Equity Market Stress",
    "Crisis Comparison", 
    "Crisis Correlation",
    "Financial Stress Index"
])

with tab1:
    st.header("Equity Market Stress")

with tab2:
    st.header("Crisis Comparison")

with tab3:
    st.header("Crisis Correlation")
    selected_crisis = st.selectbox(
        "Select crisis period",
        list(crises.keys())
    )
    fig, average_corr, strongest_pair, weakest_pair, strongest_value, weakest_value = show_selected_crisis(selected_crisis)
    st.pyplot(fig)

    st.write("Average Correlation:", round(average_corr, 2))
    st.write("Highest Positive Correlation:", strongest_pair, round(strongest_value, 2))
    st.write("Most Negative Correlation:", weakest_pair, round(weakest_value, 2))

with tab4:
    st.header("Financial Stress Index")