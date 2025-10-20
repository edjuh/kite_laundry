from flask import Flask, render_template, request
import os
import yaml
from Core.applications.article_generator import generate_production_article

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/designs")
def designs():
    designs = []
    project_root = "projects"
    for root, _, files in os.walk(project_root):
        for filename in files:
            if filename.endswith(".yaml"):
                file_path = os.path.join(root, filename)
                with open(file_path, "r") as f:
                    config = yaml.safe_load(f)
                    if config and "name" in config:
                        designs.append({
                            "name": config["name"],
                            "complexity": config.get("complexity", 2),
                            "file_path": file_path
                        })
    return render_template("designs.html", designs=designs)

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        # Handle file upload
        config = yaml.safe_load(request.files["file"])
        article_data = generate_production_article(config)
        return render_template("result.html", **article_data)
    else:
        # Handle GET with design file_path
        design_path = request.args.get("design")
        if design_path:
            with open(design_path, "r") as f:
                config = yaml.safe_load(f)
                article_data = generate_production_article(config)
                return render_template("result.html", **article_data)
        return render_template("generate.html")

@app.route("/design_form")
def design_form():
    return render_template("design_form.html")

# Add other routes as needed (e.g., /material_calculator, /template_generator)
# These are inferred from your templates/ directory

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)