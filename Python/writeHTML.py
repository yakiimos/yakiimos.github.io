# 用于生成HTML页面的Python脚本
import re

def replace_template_content(html_content, dict):
    # 正则表达式匹配 {% word %}
    pattern = r"{%\s*(\w+)\s*%}"
    matches = re.findall(pattern, html_content)
    # 替换匹配到的内容
    for match in matches:
        if match in dict:
            html_content = re.sub(pattern, dict[match], html_content)
        else:
            raise ValueError(f"未找到匹配的值: {match}")
    return html_content

def render_table(sites):
    table = "<table>"
    table += "<tr>"
    i = 0
    for site in sites:
        if i == 10:
            table += "</tr><tr>"
            i = 0
        url = site["url"]
        name = site["name"]
        description = site["description"]
        item = '<a href="{url}" target="_blank" title="{description}">{name}</a>'
        item = item.format(url=url, name=name, description=description)
        table += '<td class="cell-width">{item}</td>'.format(item=item)
        i += 1
    table += "</tr></table>"
    return table

def generate_html(template_html_path ,filling_dict:dict, html_dest=None):
    html_content = open(template_html_path, 'r', encoding='utf-8').read()

    if html_dest == None or "":
        html_dest = "./generatedHTML.html"
    html_content = replace_template_content(html_content, filling_dict)

    # 将HTML内容写入文件
    with open(html_dest, "w", encoding="utf-8") as file:
        file.write(html_content)

    print("HTML页面已生成")
    