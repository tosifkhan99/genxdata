"""
HTML file writer implementation for GenXData.

Refactored to use GenericFileWriter to reduce duplication.
"""

import pandas as pd
from typing import Any

from .generic_file_writer import GenericFileWriter


def _html_custom_write_func(
    df: pd.DataFrame, 
    output_path: str, 
    pandas_params: dict[str, Any], 
    custom_params: dict[str, Any], 
    metadata: dict[str, Any] = None
) -> dict[str, Any]:
    """Custom write function for HTML format with Bootstrap styling."""
    # Extract custom options that aren't pandas to_html parameters
    include_bootstrap = custom_params.get("include_bootstrap", True)
    title = custom_params.get("title", "Data Generator Output")
    render_links = custom_params.get("render_links", True)

    # Generate HTML content
    html_content = df.to_html(**pandas_params)

    # Add title and Bootstrap if requested
    if include_bootstrap:
        bootstrap_css = """
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body { padding: 20px; }
            .container { max-width: 100%; }
            .table-responsive { margin-top: 20px; }
            tr { text-align: center; }
        </style>
        """
        final_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {bootstrap_css}
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="table-responsive">
            {html_content}
        </div>
    </div>
</body>
</html>"""
    else:
        final_html = html_content

    # Write the HTML content to the file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    return {
        "title": title,
        "include_bootstrap": include_bootstrap,
    }


def _html_params_extractor(writer_params: dict[str, Any]) -> dict[str, Any]:
    """Extract custom HTML parameters from writer parameters."""
    custom_params = {}
    pandas_params = {}
    
    # Custom HTML parameters
    custom_keys = ["include_bootstrap", "title", "render_links"]
    for key in custom_keys:
        if key in writer_params:
            custom_params[key] = writer_params.pop(key)
    
    # Prepare pandas-compatible parameters for to_html
    pandas_params = {
        "border": writer_params.get("border", 0),
        "index": writer_params.get("index", False),
        "escape": writer_params.get("escape", True),
        "na_rep": writer_params.get("na_rep", "N/A"),
        "classes": writer_params.get("classes", "table table-striped"),
    }
    
    return custom_params


class HtmlFileWriter(GenericFileWriter):
    """
    Writer for HTML file format.

    Handles writing DataFrames to HTML files with Bootstrap styling
    and proper defaults.
    """

    def __init__(self, config: dict[str, Any]):
        # Configure the generic writer for HTML format
        html_config = {
            **config,
            "writer_kind": "html",
            "extensions": [".html", ".htm"],
            "default_params": {
                "title": "Data Generator Output",
                "classes": "table table-striped table-hover",
                "index": False,
                "border": 0,
                "escape": True,
                "na_rep": "N/A",
                "include_bootstrap": True,
                "render_links": True,
            },
            "custom_write_func": _html_custom_write_func,
            "custom_params_extractor": _html_params_extractor,
        }
        super().__init__(html_config)
