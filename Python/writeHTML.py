# 用于生成HTML页面的Python脚本
__all__ = [
    'generate_html',
]

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

def generate_html(html_content:str ,filling_dict:dict, html_dest:str=None):
    if html_dest == None:
        html_dest = "./generatedHTML.html"
    html_content = replace_template_content(html_content, filling_dict)

    # 将HTML内容写入文件
    with open(html_dest, "w", encoding="utf-8") as file:
        file.write(html_content)

    print("HTML页面已生成")

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(__file__))

    # 定义填充字典
    filling_dict = {
        "content": "这是一个示例内容",
    }
    generate_html(filling_dict)