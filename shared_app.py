import streamlit as st

from Panels.Crisis_Correlation_Heatmap import show_selected_crisis, crises
from Panels.Crisis_Comparison import (load_prices, load_stress, compare_crises,
                                      plot_comparison, plot_bubbles, CRISES)
from datetime import date

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

    prices = load_prices()
    last_day = prices.index.max().date()

    chart_type = st.radio("Chart", ["Compare one measure", "Overall severity (bubbles)"],
                          horizontal=True)
    
    chosen_names = st.multiselect("Crises to include", list(CRISES.keys()),
                                  default=list(CRISES.keys()))
    chosen_crises = {}
    for name in chosen_names:
        chosen_crises[name] = CRISES[name]

    if st.checkbox("Add my own period to compare"):
        left, right = st.columns(2)
        custom_start = left.date_input("Start", value=date(2018, 10, 1),
                                       min_value=date(2007, 2, 1), max_value=last_day)
        custom_end = right.date_input("End", value=date(2018, 12, 31),
                                      min_value=date(2007, 2, 1), max_value=last_day)
        if custom_start >= custom_end:
            st.warning("The start date must be before the end date.")
        else:
            chosen_crises["Custom period"] = (str(custom_start), str(custom_end))

    if chart_type == "Compare one measure":
        measure = st.selectbox("Measure", ["Max drawdown (%)",
                                                   "Peak yearly volatility (%)",
                                                   "Recovery (years)"])
    else:
        measure = None

    if chart_type == "Overall severity (bubbles)" or measure == "Peak yearly volatility (%)":
        window = st.slider("Volatility window (trading days)",
                           min_value=5, max_value=63, value=21,
                           help="21 days is about 1 month. Shorter windows catch sharper spikes.")
    else:
        window = 21  

    if len(chosen_crises) == 0:
        st.warning("Pick at least one crisis.")
    else:
        stress = load_stress()
        table = compare_crises(prices, stress, chosen_crises, window)

        if chart_type == "Compare one measure":
            st.pyplot(plot_comparison(table, measure))
        else:
            st.pyplot(plot_bubbles(table))

        st.caption("**Max drawdown:** the worst % fall from a peak to a low during the period. "
                   "**Peak yearly volatility:** how wildly prices swung at the most turbulent point, "
                   "as a yearly figure. **Recovery:** years from the low until the price got back "
                   "to its old peak (or years so far, if it hasn't). "
                   "Oil is measured with the USO fund, which tracks oil futures and loses value "
                   "over time, so it can make oil's recovery look slower than the oil price itself.")


        st.write("**Financial Stress Index peak**: the highest weekly stress reading in each period "
                 "(St. Louis Fed). 0 = normal, above 0 = more stress than normal.")
        cols = st.columns(len(chosen_crises))              # one column per crisis
        for i, name in enumerate(chosen_crises):
            crisis_rows = table[table["Crisis"] == name]   # this crisis's rows
            peak = crisis_rows["Stress index peak"].iloc[0]
            cols[i].metric(name, peak)
        
        st.caption("2008 was by far the most stressful for the financial system as a whole. "
                   "2022 barely rose above normal, even though bonds fell sharply.")

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