from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import matplotlib.pyplot as plt
import io
import os

class ReportGenerator:
    def __init__(self, report_dir='reports'):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
    
    def create_performance_chart(self, historical_data, student_name):
        plt.figure(figsize=(8, 4))
        
        dates = historical_data['date'].values
        scores = historical_data['probability'].values
        
        plt.plot(dates, scores, marker='o', linewidth=2, markersize=8)
        plt.fill_between(dates, scores, alpha=0.3)
        plt.title(f'Performance Trend - {student_name}')
        plt.xlabel('Date')
        plt.ylabel('Placement Probability (%)')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_path = os.path.join(self.report_dir, f'{student_name}_trend.png')
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path
    
    def create_comparison_chart(self, comparison_data):
        metrics = list(comparison_data.keys())[:6]  # Limit to 6 metrics
        student_values = [comparison_data[m]['student_value'] for m in metrics]
        peer_values = [comparison_data[m]['peer_average'] for m in metrics]
        
        x = range(len(metrics))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar([i - width/2 for i in x], student_values, width, label='You', color='#4CAF50')
        ax.bar([i + width/2 for i in x], peer_values, width, label='Peer Average', color='#FF9800')
        
        ax.set_xlabel('Metrics')
        ax.set_ylabel('Score')
        ax.set_title('You vs Peers Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        chart_path = os.path.join(self.report_dir, 'peer_comparison.png')
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path
    
    def generate_report(self, student_name, prediction_result, probability, 
                       historical_data, comparison_data, recommendations):
        report_path = os.path.join(self.report_dir, f'{student_name}_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        
        doc = SimpleDocTemplate(report_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1e3c72'))
        story.append(Paragraph(f"Placement Prediction Report - {student_name}", title_style))
        story.append(Spacer(1, 12))
        
        # Date
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Prediction Result
        result_style = ParagraphStyle('ResultStyle', parent=styles['Normal'], fontSize=16, 
                                      textColor=colors.green if prediction_result == 1 else colors.red)
        result_text = "✅ HIGH CHANCE OF PLACEMENT" if prediction_result == 1 else "⚠️ LOW CHANCE OF PLACEMENT"
        story.append(Paragraph(f"<b>Prediction Result:</b> {result_text}", result_style))
        story.append(Paragraph(f"<b>Probability:</b> {probability*100:.1f}%", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Performance Trend Chart
        if len(historical_data) > 1:
            chart_path = self.create_performance_chart(historical_data, student_name)
            story.append(Paragraph("<b>Performance Trend:</b>", styles['Heading2']))
            story.append(Image(chart_path, width=6*inch, height=3*inch))
            story.append(Spacer(1, 12))
        
        # Peer Comparison
        if comparison_data:
            chart_path = self.create_comparison_chart(comparison_data)
            story.append(Paragraph("<b>Peer Comparison:</b>", styles['Heading2']))
            story.append(Image(chart_path, width=6*inch, height=3*inch))
            story.append(Spacer(1, 12))
        
        # Detailed Comparison Table
        story.append(Paragraph("<b>Detailed Metrics Comparison:</b>", styles['Heading2']))
        
        table_data = [['Metric', 'Your Score', 'Peer Average', 'Status']]
        for metric, data in list(comparison_data.items())[:8]:
            status = "✅ Above Average" if data['better_than_peers'] else "⚠️ Below Average"
            table_data.append([
                metric.replace('_', ' ').title(),
                f"{data['student_value']:.1f}",
                f"{data['peer_average']:.1f}",
                status
            ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Recommendations
        story.append(Paragraph("<b>Personalized Recommendations:</b>", styles['Heading2']))
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        return report_path