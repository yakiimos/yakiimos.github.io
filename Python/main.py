import os

import writeHTML

def md_table_to_json(md_table:str):
    lines = md_table.strip().split("\n")
    headers = [header.strip() for header in lines[0].split("|") if header.strip()]
    rows = [
        [cell.strip() for cell in row.split("|") if cell.strip()]
        for row in lines[2:]  # Skip the header and separator lines
    ]
    # json_data = [dict(zip(headers, row)) for row in rows if row]
    # json_file = json.dumps(json_data, indent=4, ensure_ascii=False)
    return [headers,rows]


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    with open("sites.md", "r", encoding="utf-8") as f:
        md_table = f.read()
    # 转换为JSON
    result = md_table_to_json(md_table)

    dict = {
        'content' : writeHTML.render_table(result),
    }

    with open("./index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    writeHTML.generate_html(html_content,dict,"../Pages/index.html")