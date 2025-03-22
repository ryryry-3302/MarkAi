#!/usr/bin/env python3
"""
PDF Report Generator

This script converts the latest marketing strategy markdown file into a
nicely formatted PDF report with custom styling and branding.
"""

import os
import sys
import argparse
import datetime
from pathlib import Path
import markdown
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import re

def create_css_file(css_path):
    """Create a CSS file with custom styling for the PDF report."""
    css_content = """
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');

    body {
        font-family: 'Open Sans', sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 8.5in;
        margin: 0 auto;
        padding: 0.5in;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif;
        color: #1a365d;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }

    h1 {
        font-size: 24pt;
        color: #1a365d;
        text-align: center;
        margin-top: 0;
        border-bottom: 2px solid #1a365d;
        padding-bottom: 10px;
    }

    h2 {
        font-size: 18pt;
        color: #2a4365;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 5px;
    }

    h3 {
        font-size: 14pt;
        color: #2c5282;
    }

    h4 {
        font-size: 12pt;
        color: #2b6cb0;
    }

    p {
        margin-bottom: 1em;
    }

    ul, ol {
        margin-bottom: 1em;
        padding-left: 2em;
    }

    li {
        margin-bottom: 0.5em;
    }

    strong {
        font-weight: 600;
        color: #2c5282;
    }

    em {
        font-style: italic;
    }

    a {
        color: #3182ce;
        text-decoration: none;
    }

    blockquote {
        border-left: 4px solid #e2e8f0;
        padding-left: 1em;
        margin-left: 0;
        color: #4a5568;
    }

    code {
        font-family: monospace;
        background-color: #f7fafc;
        padding: 2px 4px;
        border-radius: 3px;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 1em;
    }

    th, td {
        border: 1px solid #e2e8f0;
        padding: 8px 12px;
        text-align: left;
    }

    th {
        background-color: #f7fafc;
        font-weight: 600;
    }

    img {
        max-width: 100%;
        height: auto;
    }

    .header {
        text-align: center;
        margin-bottom: 2em;
    }

    .logo {
        max-width: 200px;
        margin: 0 auto;
        display: block;
    }

    .date {
        text-align: center;
        color: #4a5568;
        font-size: 10pt;
        margin-bottom: 2em;
    }

    .footer {
        text-align: center;
        font-size: 9pt;
        color: #4a5568;
        margin-top: 2em;
        border-top: 1px solid #e2e8f0;
        padding-top: 1em;
    }

    .page-break {
        page-break-after: always;
    }

    /* Style for executive summary */
    .executive-summary {
        background-color: #f8f9fa;
        border-left: 4px solid #3182ce;
        padding: 15px;
        margin: 20px 0;
    }

    /* Style for campaign sections */
    .campaign {
        background-color: #f0f4f8;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }

    /* Style for KPIs */
    .kpi {
        font-weight: bold;
        color: #2c5282;
    }

    /* Table of contents styling */
    .toc {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 2em;
    }

    .toc h2 {
        margin-top: 0;
    }

    .toc ul {
        list-style-type: none;
        padding-left: 0;
    }

    .toc li {
        margin-bottom: 0.3em;
    }

    .toc a {
        text-decoration: none;
        color: #3182ce;
    }

    /* Page numbers */
    @page {
        @bottom-right {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 9pt;
            color: #4a5568;
        }
    }
    """
    
    with open(css_path, 'w') as css_file:
        css_file.write(css_content)
    
    return css_path

def create_html_template(template_dir):
    """Create an HTML template for the PDF report."""
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, 'report_template.html')
    template_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p class="date">Generated on {{ date }}</p>
    </div>
    
    <div class="toc">
        <h2>Table of Contents</h2>
        {{ toc }}
    </div>
    
    <div class="content">
        {{ content }}
    </div>
    
    <div class="footer">
        <p>© {{ year }} MarkAi - Corzetti Restaurant Marketing Strategy</p>
    </div>
</body>
</html>
"""
    
    with open(template_path, 'w') as template_file:
        template_file.write(template_content)
    
    return template_path

def extract_title(markdown_content):
    """Extract the title from the markdown content."""
    match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
    if match:
        return match.group(1)
    return "Marketing Strategy Report"

def generate_toc(markdown_content):
    """Generate a table of contents from the markdown content."""
    toc = "<ul>"
    for line in markdown_content.split('\n'):
        if line.startswith('##'):
            section = line.replace('##', '').strip()
            anchor = section.lower().replace(' ', '-').replace(':', '')
            toc += f'<li><a href="#{anchor}">{section}</a></li>'
    toc += "</ul>"
    return toc

def enhance_markdown(markdown_content):
    """Enhance the markdown content with additional styling classes."""
    # Add class to executive summary
    enhanced_content = markdown_content.replace(
        "**1. Executive Summary:**", 
        '<div class="executive-summary">\n\n**1. Executive Summary:**'
    )
    enhanced_content = enhanced_content.replace(
        "**2. Content Strategy:**", 
        '</div>\n\n**2. Content Strategy:**'
    )
    
    # Add classes to campaign sections
    campaign_pattern = r'(\*\*Campaign \d+:.+?\*\*.*?)(?=\*\*Campaign \d+:|$)'
    enhanced_content = re.sub(
        campaign_pattern,
        r'<div class="campaign">\1</div>',
        enhanced_content,
        flags=re.DOTALL
    )
    
    # Add class to KPIs
    kpi_pattern = r'(\*\*[^*]+:\*\*)'
    enhanced_content = re.sub(
        kpi_pattern,
        r'<span class="kpi">\1</span>',
        enhanced_content
    )
    
    return enhanced_content

def markdown_to_pdf(markdown_path, output_path, template_dir='templates', css_dir='styles'):
    """Convert markdown to PDF with custom styling."""
    # Create directories if they don't exist
    os.makedirs(template_dir, exist_ok=True)
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create CSS file
    css_path = os.path.join(css_dir, 'report_style.css')
    create_css_file(css_path)
    
    # Create HTML template
    template_path = create_html_template(template_dir)
    
    # Read markdown content
    with open(markdown_path, 'r') as md_file:
        markdown_content = md_file.read()
    
    # Extract title
    title = extract_title(markdown_content)
    
    # Generate table of contents
    toc = generate_toc(markdown_content)
    
    # Enhance markdown with styling classes
    enhanced_markdown = enhance_markdown(markdown_content)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(enhanced_markdown, extensions=['extra'])
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('report_template.html')
    
    # Render HTML with template
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    current_year = datetime.datetime.now().year
    html = template.render(
        title=title,
        date=current_date,
        year=current_year,
        toc=toc,
        content=html_content
    )
    
    # Convert HTML to PDF
    css = CSS(filename=css_path)
    HTML(string=html).write_pdf(output_path, stylesheets=[css])
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Generate a PDF report from a markdown file')
    parser.add_argument('--input', type=str, 
                        default='/home/ryan/Workspace/MarkAi/marketing_analytics_backend/output/latest_food_marketing_strategy.md',
                        help='Path to the input markdown file')
    parser.add_argument('--output', type=str, 
                        default='/home/ryan/Workspace/MarkAi/marketing_analytics_backend/output/marketing_strategy_report.pdf',
                        help='Path to the output PDF file')
    parser.add_argument('--template-dir', type=str, default='templates',
                        help='Directory for HTML templates')
    parser.add_argument('--css-dir', type=str, default='styles',
                        help='Directory for CSS files')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        return 1
    
    print(f"Generating PDF report from {args.input}...")
    
    try:
        output_path = markdown_to_pdf(
            args.input, 
            args.output,
            template_dir=args.template_dir,
            css_dir=args.css_dir
        )
        print(f"PDF report generated successfully: {output_path}")
        return 0
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
