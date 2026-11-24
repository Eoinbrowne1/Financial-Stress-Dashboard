import gradio as gr
from Panels.Equity_Market_Stress import build_equity_panel
from Panels.Crisis_Correlation_Heatmap import build_correlation_panel

with gr.Blocks(title="Financial Stress Dashboard") as demo:
    gr.Markdown("# Financial Stress Dashboard")
    with gr.Tab("Equity Market Stress"):
        build_equity_panel()
    with gr.Tab("Crisis Correlation"):
        build_correlation_panel() 
if __name__ == "__main__":
    demo.launch()