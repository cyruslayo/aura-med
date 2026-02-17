import time
from typing import List, Dict, Optional
import pandas as pd
from IPython.display import HTML
from src.datatypes import TriageResult

class LatencyTracker:
    """Tracks and reports performance metrics for demo scenarios."""
    
    def __init__(self):
        self.metrics: List[Dict] = []

    def record(self, scenario_name: str, result: TriageResult):
        """Records metrics for a single scenario execution from a TriageResult."""
        latency_sec = result.usage_stats.get('latency_sec', 0.0) if result.usage_stats else 0.0
        ram_gb = result.usage_stats.get('ram_gb', 0.0) if result.usage_stats else 0.0
        
        self.metrics.append({
            "Scenario": scenario_name,
            "Latency (s)": round(latency_sec, 3),
            "RAM Usage (GB)": round(ram_gb, 2),
            "Status": result.status.value,
            "Timestamp": time.strftime("%H:%M:%S")
        })

    def generate_summary_table(self) -> HTML:
        """Generates a beautiful HTML summary table for the notebook."""
        if not self.metrics:
            return HTML("<p>No telemetry data available.</p>")
            
        df = pd.DataFrame(self.metrics)
        
        # Style the dataframe
        styled_df = df.style.set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#2c3e50'), ('color', 'white'), ('font-family', 'Inter, sans-serif'), ('text-align', 'center')]},
            {'selector': 'td', 'props': [('font-family', 'Roboto, sans-serif'), ('text-align', 'center')]},
            {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f8f9fa')]}
        ]).set_properties(**{'border': '1px solid #dee2e6', 'padding': '10px'})
        
        # Conditional formatting for latency (Highlight > 10s as red)
        def color_latency(val):
            color = 'red' if val > 10.0 else 'green' if val < 5.0 else 'black'
            return f'color: {color}'
            
        # Check if "Latency (s)" column exists before applying style
        if "Latency (s)" in df.columns:
            styled_df = styled_df.map(color_latency, subset=['Latency (s)'])

        html_output = f"""
        <div style="margin-top: 30px; border-top: 2px solid #eee; padding-top: 20px;">
            <h3 style="font-family: Inter, sans-serif; color: #2c3e50;">🚀 Performance Telemetry Summary</h3>
            {styled_df.to_html()}
            <p style="font-size: 11px; color: #7f8c8d; margin-top: 8px;">* Thresholds: Latency < 10s, RAM < 4.0GB per Edge configuration.</p>
        </div>
        """
        return HTML(html_output)

    def get_total_runtime(self) -> float:
        """Returns the total execution time across all recorded scenarios."""
        return sum(m["Latency (s)"] for m in self.metrics)
