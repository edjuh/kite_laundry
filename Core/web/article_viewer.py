#!/usr/bin/env python3
"""
Web Article Viewer
Provides web interface for viewing generated articles
"""

from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, 
    static_folder='Core/web/static',
    template_folder='Core/web/templates')

@app.route('/article/<project_name>')
def view_article(project_name):
    """Render article page"""
    return render_template('article_template.html', 
                          project_name=project_name)

@app.route('/download/<project_name>/<filename>')
def download_file(project_name, filename):
    """Serve downloadable files"""
    return send_from_directory(
        f'projects/{project_name}/downloads',
        filename
    )

if __name__ == "__main__":
    app.run(debug=True)

