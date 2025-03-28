# app/utils.py
import os
from pathlib import Path
import markdown
from weasyprint import HTML
import tempfile
from config.config_load import CONFIG

def markdown_to_pdf(markdown_path, output_path=None):
    """
    Convert a markdown file to PDF using WeasyPrint
    
    Args:
        markdown_path (str): Path to the markdown file
        output_path (str, optional): Path for the output PDF file. 
                                    If None, will use the same name with .pdf extension
    
    Returns:
        str: Path to the generated PDF file
    """
    if output_path is None:
        output_path = os.path.splitext(markdown_path)[0] + '.pdf'
    
    # Read markdown content
    with open(markdown_path, 'r') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Add some basic styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ margin: 1cm; }}
            body {{ font-family: Arial, sans-serif; margin: 0; }}
            h1 {{ color: #333366; }}
            h2 {{ color: #333366; border-bottom: 1px solid #cccccc; padding-bottom: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
        temp_html_path = temp.name
        temp.write(styled_html.encode('utf-8'))
    
    try:
        # Convert HTML to PDF
        HTML(filename=temp_html_path).write_pdf(output_path)
        return output_path
    except Exception as e:
        raise RuntimeError(f"PDF conversion failed: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
