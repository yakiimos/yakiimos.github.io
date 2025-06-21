from pathlib import Path

# 业务层：main 主要逻辑
from writeHTML import * # 交互层：writeHTML 提供用户界面
from writedb import * # 数据层：writedb 数据存取
from uio import * # 处理层：io 将用户数据转换为格式化数据


def main():
    ROOT_PATH = Path(__file__).parent.parent
    SRC_PATH = ROOT_PATH / "srcs"

    # 创建数据库
    # create_database(SRC_PATH / "sites.db")

    # 处理数据并输出到数据库
    # sites = read_sites_file(SRC_PATH / "sites.md")
    # write_database(SRC_PATH / "sites.db", sites)

    # 读取数据库渲染 HTML
    sites = fetch_data(SRC_PATH / "sites.db")
    replacer = {'content': render_table(sites)}
    generate_html(SRC_PATH / "index.html", replacer, ROOT_PATH / "index.html")
    


if __name__ == "__main__":
    main()
        