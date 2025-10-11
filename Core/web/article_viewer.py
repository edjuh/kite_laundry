# -*- coding: utf-8 -*-
from flask import Blueprint, render_template

# Create article viewer blueprint
article_bp = Blueprint("article", __name__, template_folder="templates")


@article_bp.route("/article/<path:article_name>")
def view_article(article_name):
    """Render an article page"""
    return render_template("article.html", article_name=article_name)


@article_bp.route("/articles")
def list_articles():
    """List all available articles"""
    return render_template("articles.html")


@article_bp.route("/")
def index():
    """Main page"""
    return render_template("index.html")
