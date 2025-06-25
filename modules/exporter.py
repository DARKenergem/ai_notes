from jinja2 import Environment, BaseLoader

_MARKDOWN_TEMPLATE = """
# {title}

**Tags:** {tags}

**Workspace:** {workspace}

{content}

---

"""
_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{title}</title></head>
<body>
  <h1>{title}</h1>
  <p><strong>Tags:</strong> {tags}</p>
  <p><strong>Workspace:</strong> {workspace}</p>
  <div>{content}</div>
</body>
</html>
"""
_env = Environment(loader=BaseLoader())
_md_template = _env.from_string(_MARKDOWN_TEMPLATE)
_html_template = _env.from_string(_HTML_TEMPLATE)

def export_notes_to_markdown(notes, output_path=None):
    md_content = ""
    for note in notes:
        md_content += _md_template.render(
            title=note['title'],
            tags=', '.join(note['tags']),
            workspace=note['workspace'],
            content=note['content']
        )
    if output_path:
        with open(output_path, 'w') as f:
            f.write(md_content)
    return md_content

def export_notes_to_html(notes, output_path=None):
    html_content = ""
    for note in notes:
        html_content += _html_template.render(
            title=note['title'],
            tags=', '.join(note['tags']),
            workspace=note['workspace'],
            content=note['content'].replace("\n", "<br>")
        )
    if output_path:
        with open(output_path, 'w') as f:
            f.write(html_content)
    return html_content