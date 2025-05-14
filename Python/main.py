import json
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

def render_table(table_content):
    thead = table_content[0]
    tbody = table_content[1]
    table = "<table><thead><tr>"
    for i in thead:
        table = table.join(['<th>',i,'</th>'])
    table = table.join("</tr></thead><tbody>")
    for i in tbody:
        table = table.join('<tr>')
        for j in i:
            table = table.join(['<td>',j,'</td>'])
        table = table.join('</tr>')
    table = table.join('</tbody></table>')
    return table

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    with open("sites.md", "r", encoding="utf-8") as f:
        md_table = f.read()
    # 转换为JSON
    result = md_table_to_json(md_table)

    dict = {
        'content' : render_table(result)
    }

    with open("./index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    writeHTML.generate_html(html_content,dict,"../Pages/index.html")