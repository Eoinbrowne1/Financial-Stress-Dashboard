import matplotlib
matplotlib.use("Agg")

import gradio as gr
from Panels.Equity_Market_Stress import build_equity_panel
from Panels.Crisis_Correlation_Heatmap import build_correlation_panel
from Panels.crisis_comparison_tab import build_crisis_comparison_tab
from Panels.Financial_Stress_Index import build_stress_tab

with gr.Blocks(title="Financial Stress Dashboard", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Financial Stress Dashboard")
    with gr.Tab("Equity Market Stress"):
        build_equity_panel()
    with gr.Tab("Crisis Correlation"):
        build_correlation_panel() 
    with gr.Tab("Crisis Comparison"):
        build_crisis_comparison_tab()
    with gr.Tab("Financial Stress Index"):
        build_stress_tab()

if __name__ == "__main__":
    demo.launch()