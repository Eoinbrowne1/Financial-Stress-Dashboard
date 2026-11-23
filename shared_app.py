import streamlit as st

from Panels.Crisis_Correlation_Heatmap import show_selected_crisis, crises
from Panels.Crisis_Comparison import (load_prices, load_stress, compare_crises,
                                      plot_comparison, plot_bubbles, CRISES)

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
    st.write("Which financial crisis was most severe, and how did the crises differ")

    chart_type = st.radio("Chart", ["Compare one measure", "Overall severity (bubbles)"],
                          horizontal=True)
    
    chosen_names = st.multiselect("Crises to include", list(CRISES.keys()),
                                  default=list(CRISES.keys()))
    chosen_crises = {}
    for name in chosen_names:
        chosen_crises[name] = CRISES[name]

    if chart_type == "Compare one measure":
        measure = st.selectbox("Measure", ["Max drawdown (%)",
                                                   "Peak yearly volatility (%)",
                                                   "Recovery (years)"])
    else:
        measure = None

    if chart_type == "Overall severity (bubbles)" or measure == "Peak yearly volatility (%)":
        window = st.slider("Volatility window (trading days)",
                           min_value=5, max_value=63, 
value=21,
                           help="21 days is about 1 month. Shorter windows catch sharper spikes.")
    else:
        window = 21  

    if len(chosen_crises) == 0:
        st.warning("Pick at least one crisis.")
    else:
        prices = load_prices()
        stress = load_stress()
        table = compare_crises(prices, stress, chosen_crises, window)

        if chart_type == "Compare one measure":
            st.pyplot(plot_comparison(table, measure))
        else:
            st.pyplot(plot_bubbles(table))

        st.write("**Financial Stress Index peak** (St. Louis Fed, 0 = normal)")
        cols = st.columns(len(chosen_crises))              # one column per crisis
        for i, name in enumerate(chosen_crises):
            crisis_rows = table[table["Crisis"] == name]   # this crisis's rows
            peak = crisis_rows["Stress index peak"].iloc[0]
            cols[i].metric(name, peak)

with tab3:
    st.header("Crisis Correlation")
    selected_crisis = st.selectbox(
        "Select crisis period",
        list(crises.keys())
    )
    fig, average_corr, average_abs_corr, strongest_pair, weakest_pair, strongest_value, weakest_value = show_selected_crisis(selected_crisis)
    st.pyplot(fig)

    st.write("Average Correlation:", round(average_corr, 2))
    st.write("Average Absolute Correlation:", round(average_abs_corr, 2))
    st.write("Highest Positive Correlation:", strongest_pair, round(strongest_value, 2))
    st.write("Most Negative Correlation:", weakest_pair, round(weakest_value, 2))

with tab4:
    st.header("Financial Stress Index")