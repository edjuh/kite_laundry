from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
import yaml
from Core.applications.article_generator import generate_article

app = Flask(__name__, template_folder='Core/web/templates')
PROJECTS_DIR = Path("projects")

def get_yaml_designs():
    designs = []
    for yaml_file in PROJECTS_DIR.rglob("*.yaml"):
        try:
            with open(yaml_file, "r") as f:
                config = yaml.safe_load(f)
                if config and isinstance(config, dict) and "name" in config:
                    designs.append({
                        "name": config["name"],
                        "path": str(yaml_file.relative_to(PROJECTS_DIR)),
                        "full_path": str(yaml_file)
                    })
        except yaml.YAMLError as e:
            print(f"YAML error in {yaml_file}: {e}")
        except ValueError as e:
            print(f"Value error in {yaml_file}: {e}")
        except FileNotFoundError as e:
            print(f"File not found {yaml_file}: {e}")
    return designs

@app.route("/")
def home():
    return redirect(url_for("designs"))

@app.route("/designs")
def designs():
    yaml_designs = get_yaml_designs()
    print(f"Template folder: {app.template_folder}")
    print(f"Looking for designs.html in: {Path(app.template_folder) / 'designs.html'}")
    return render_template("designs.html", designs=yaml_designs)

@app.route("/generate")
def generate():
    file_path = request.args.get("path")
    if not file_path:
        return render_template("generate.html", error="No design selected")
    try:
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
        article_path = generate_article(file_path)
        if article_path:
            with open(article_path, "r") as f:
                article_data = {"content": f.read()}
            return render_template("result.html", **article_data)
        return render_template("generate.html", error="Article generation failed")
    except yaml.YAMLError as e:
        return render_template("generate.html", error=f"YAML error in {file_path}: {e}")
    except ValueError as e:
        return render_template("generate.html", error=f"Value error in {file_path}: {e}")
    except FileNotFoundError as e:
        return render_template("generate.html", error=f"File not found {file_path}: {e}")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
