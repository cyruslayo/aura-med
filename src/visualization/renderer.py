import html
from IPython.display import HTML
from src.datatypes import TriageResult, TriageStatus

class NotebookRenderer:
    """Renders clinical triage results as beautiful, mobile-style HTML cards."""

    def __init__(self):
        # Using a more robust font loading approach
        self.fonts_url = "https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Roboto:wght@400;500&display=swap"
        
        self.colors = {
            TriageStatus.GREEN: "#2ECC71",
            TriageStatus.YELLOW: "#F1C40F",
            TriageStatus.RED: "#E74C3C",
            TriageStatus.INCONCLUSIVE: "#95A5A6"
        }

    def _get_css(self, status: TriageStatus) -> str:
        color = self.colors.get(status, "#95A5A6")
        
        # Accessibility fix: Use dark text for Yellow background
        header_text_color = "white"
        if status == TriageStatus.YELLOW:
            header_text_color = "#2c3e50"
            
        return f"""
        <link href="{self.fonts_url}" rel="stylesheet">
        <style>
            .aura-card-container {{
                display: flex;
                justify-content: center;
                padding: 20px;
                background-color: #f5f6fa;
                font-family: 'Roboto', sans-serif;
            }}
            .aura-card {{
                width: 100%;
                max-width: 400px; /* AC #4 Fix: Updated to 400px */
                background: white;
                border-radius: 24px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                overflow: hidden;
                border: 1px solid #e1e8ed;
            }}
            .aura-header {{
                background-color: {color};
                padding: 24px;
                color: {header_text_color};
                text-align: center;
            }}
            .aura-header h2 {{
                margin: 0;
                font-family: 'Inter', sans-serif;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
            .aura-content {{
                padding: 24px;
            }}
            .aura-section {{
                margin-bottom: 20px;
            }}
            .aura-label {{
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #7f8c8d;
                margin-bottom: 8px;
                font-weight: 700;
            }}
            .aura-text {{
                font-size: 16px;
                line-height: 1.5;
                color: #2c3e50;
            }}
            .aura-footer {{
                background-color: #f8f9fa;
                padding: 16px 24px;
                border-top: 1px solid #e1e8ed;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .aura-telemetry {{
                font-size: 11px;
                color: #95a5a6;
                font-family: monospace;
            }}
            .aura-badge {{
                background: #ebf5fb;
                color: #2980b9;
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 700;
            }}
        </style>
        """

    def render(self, result: TriageResult) -> HTML:
        """Generates the HTML representation of the triage result."""
        
        css = self._get_css(result.status)
        ram_usage = "N/A"
        if result.usage_stats and 'ram_gb' in result.usage_stats:
            ram_usage = f"{result.usage_stats['ram_gb']:.1f} GB"

        # Security Fix: Use html.escape to prevent XSS/HTML injection
        safe_reasoning = html.escape(result.reasoning)
        
        action_html = ""
        if result.action_recommendation:
            safe_action = html.escape(result.action_recommendation)
            action_html = f"""
            <div class='aura-section'>
                <div class='aura-label'>Action Plan</div>
                <div class='aura-text' style='font-weight: 500'>{safe_action}</div>
            </div>
            """

        html_content = f"""
        {css}
        <div class="aura-card-container">
            <div class="aura-card">
                <div class="aura-header">
                    <div class="aura-label" style="color: inherit; opacity: 0.8">WHO Triage Status</div>
                    <h2>{result.status.value}</h2>
                </div>
                <div class="aura-content">
                    <div class="aura-section">
                        <div class="aura-label">Clinical Reasoning</div>
                        <div class="aura-text">{safe_reasoning}</div>
                    </div>
                    {action_html}
                </div>
                <div class="aura-footer">
                    <div class="aura-telemetry">EDGE SIM: {ram_usage} RAM</div>
                    <div class="aura-badge">CONF: {result.confidence:.0%}</div>
                </div>
            </div>
        </div>
        """
        return HTML(html_content)
