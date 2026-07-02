#!/usr/bin/env python3
"""
obsidian-to-mdx.py — 将 Obsidian Markdown 转换为 Astro MDX 并上传图片到阿里云 OSS

功能：
  1. 解析 Obsidian 图片语法 ![[img]] 和 ![[img|width]]
  2. 自动从 Obsidian 附件目录查找图片文件
  3. 上传至阿里云 OSS，返回公开 URL
  4. 替换为标准 Markdown / HTML img 标签
  5. 生成带 frontmatter 的 MDX 文件

用法：
  python obsidian-to-mdx.py \\
    --input  ~/Documents/Obsidian\\ Vault/1-默认/文章.md \\
    --output ~/code/blog/src/content/blog/article.mdx \\
    --attachment-dir ~/Documents/Obsidian\\ Vault/4-附件 \\
    --oss-prefix blog/article/ \\
    --title "文章标题" \\
    --description "文章描述" \\
    --tags 学术,原创,LaTeX

依赖：
  pip install oss2

OSS 配置通过环境变量传入：
  export OSS_ACCESS_KEY_ID=your_key_id
  export OSS_ACCESS_KEY_SECRET=your_key_secret
  export OSS_BUCKET=your_bucket_name
  export OSS_REGION=oss-cn-shenzhen          # 默认值
  export OSS_ENDPOINT=https://oss-cn-shenzhen.aliyuncs.com  # 可选，优先级高于 region
"""

import argparse
import hashlib
import mimetypes
import os
import re
import sys
from datetime import date
from pathlib import Path

# ── Obsidian 图片语法正则 ──────────────────────────────────
# ![[image.png]]          → 纯图片
# ![[image.png|400]]      → 带宽度
# ![[image.png|400x300]]  → 带宽高（Obsidian 也支持但少见）
OBSIDIAN_IMG_RE = re.compile(
    r'!\[\[(?P<filename>[^\]|]+)'           # 文件名（不含 ] 和 |）
    r'(?:\|(?P<size>[^\]]+))?'              # 可选的尺寸参数
    r'\]\]'
)

# ── Frontmatter 模板 ──────────────────────────────────────
FRONTMATTER_TEMPLATE = """\
---
title: "{title}"
{description_line}pubDate: {pub_date}
tags: [{tags}]
---
"""


def parse_obsidian_frontmatter(text: str) -> tuple[str, str]:
    """
    解析 Obsidian 的 YAML frontmatter，返回 (frontmatter_dict, body)。
    仅提取 tags 字段，其余忽略。
    """
    if not text.startswith('---'):
        return {}, text

    end = text.find('---', 3)
    if end == -1:
        return {}, text

    fm_text = text[3:end].strip()
    body = text[end + 3:].lstrip('\n')

    tags = []
    # 解析 tags: 列表（支持 - item 格式和 [a, b] 格式）
    tags_match = re.search(r'^tags:\s*\n((?:\s+-\s+.+\n?)+)', fm_text, re.MULTILINE)
    if tags_match:
        for line in tags_match.group(1).strip().split('\n'):
            tag = re.sub(r'^\s*-\s*', '', line).strip()
            if tag:
                tags.append(tag)
    else:
        tags_inline = re.search(r'^tags:\s*\[(.+)\]', fm_text, re.MULTILINE)
        if tags_inline:
            tags = [t.strip().strip('"').strip("'") for t in tags_inline.group(1).split(',')]

    return {'tags': tags}, body


def find_image_file(filename: str, search_dirs: list[Path]) -> Path | None:
    """在多个目录中查找图片文件。"""
    for d in search_dirs:
        candidate = d / filename
        if candidate.is_file():
            return candidate
    return None


def upload_to_oss(local_path: Path, oss_key: str, client, bucket_name: str, endpoint: str) -> str:
    """上传文件到 OSS，返回公开访问 URL。"""
    content_type = mimetypes.guess_type(str(local_path))[0] or 'application/octet-stream'
    headers = {'Content-Type': content_type}
    client.put_object_from_file(oss_key, str(local_path), headers=headers)

    # 构建公开 URL
    # endpoint 可能是 https://oss-cn-shenzhen.aliyuncs.com 或 oss-cn-shenzhen.aliyuncs.com
    host = endpoint.replace('https://', '').replace('http://', '')
    return f"https://{bucket_name}.{host}/{oss_key}"


def compute_file_hash(path: Path) -> str:
    """计算文件 MD5 前 8 位，用于去重。"""
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()[:8]


def convert_image_links(
    body: str,
    search_dirs: list[Path],
    oss_client,
    oss_prefix: str,
    bucket_name: str,
    endpoint: str,
    dry_run: bool = False,
) -> tuple[str, int, int]:
    """
    将 Obsidian 图片语法转换为标准 Markdown/HTML，同时上传图片。
    返回 (转换后的文本, 成功数, 失败数)。
    """
    success_count = 0
    fail_count = 0
    upload_cache: dict[str, str] = {}  # filename → url，避免重复上传

    def replace_match(m: re.Match) -> str:
        nonlocal success_count, fail_count

        filename = m.group('filename').strip()
        size_str = m.group('size')

        # 查找本地文件
        local_path = find_image_file(filename, search_dirs)
        if not local_path:
            print(f"  ⚠️  找不到图片: {filename}")
            fail_count += 1
            return m.group(0)  # 保持原样

        # 检查缓存（同一文件不重复上传）
        if filename in upload_cache:
            url = upload_cache[filename]
        elif dry_run:
            url = f"[DRY-RUN] {oss_prefix}{filename}"
            upload_cache[filename] = url
            success_count += 1
        else:
            oss_key = oss_prefix + filename
            try:
                url = upload_to_oss(local_path, oss_key, oss_client, bucket_name, endpoint)
                upload_cache[filename] = url
                size_kb = local_path.stat().st_size / 1024
                print(f"  ✅ {filename} ({size_kb:.0f}KB) → {url}")
                success_count += 1
            except Exception as e:
                print(f"  ❌ {filename}: {e}")
                fail_count += 1
                return m.group(0)

        # 解析尺寸参数
        width = None
        height = None
        if size_str:
            size_str = size_str.strip()
            if 'x' in size_str:
                parts = size_str.split('x')
                width, height = parts[0].strip(), parts[1].strip()
            elif size_str.isdigit():
                width = size_str

        # 生成替代文本（去掉扩展名和时间戳后缀）
        alt = re.sub(r'-\d{13}$', '', Path(filename).stem)

        # 有宽度限制时用 HTML img 标签
        if width or height:
            attrs = [f'src="{url}"', f'alt="{alt}"']
            if width:
                attrs.append(f'width="{width}"')
            if height:
                attrs.append(f'height="{height}"')
            return f"<img {' '.join(attrs)} />"
        else:
            return f"![{alt}]({url})"

    converted = OBSIDIAN_IMG_RE.sub(replace_match, body)
    return converted, success_count, fail_count


def generate_frontmatter(
    title: str | None,
    description: str | None,
    tags: list[str],
    pub_date: str | None,
    source_tags: list[str],
) -> str:
    """生成 MDX frontmatter。"""
    final_tags = tags if tags else source_tags
    tags_str = ', '.join(f'"{t}"' for t in final_tags)
    desc_line = f'description: "{description}"\n' if description else ''

    return FRONTMATTER_TEMPLATE.format(
        title=title or "未命名文章",
        description_line=desc_line,
        pub_date=pub_date or date.today().isoformat(),
        tags=tags_str,
    )


def main():
    parser = argparse.ArgumentParser(
        description='Obsidian Markdown → Astro MDX 转换器（含 OSS 图片上传）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法（dry-run 模式，不实际上传）
  python obsidian-to-mdx.py -i article.md -o article.mdx --dry-run

  # 完整用法
  python obsidian-to-mdx.py \\
    -i ~/Documents/Obsidian\\ Vault/1-默认/文章.md \\
    -o ~/code/blog/src/content/blog/article.mdx \\
    -a ~/Documents/Obsidian\\ Vault/4-附件 \\
    --oss-prefix blog/article/ \\
    --title "文章标题" --tags 学术,原创
        """,
    )

    parser.add_argument('-i', '--input', required=True, help='输入的 Obsidian Markdown 文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出的 MDX 文件路径')
    parser.add_argument(
        '-a', '--attachment-dir',
        help='Obsidian 附件文件夹路径（默认: 输入文件同级目录）',
    )
    parser.add_argument('--oss-prefix', default='blog/', help='OSS 上传路径前缀（默认: blog/）')
    parser.add_argument('--title', help='文章标题（默认从 frontmatter 或文件名推断）')
    parser.add_argument('--description', help='文章描述')
    parser.add_argument('--tags', help='标签，逗号分隔（默认使用源文件中的 tags）')
    parser.add_argument('--pub-date', help='发布日期 YYYY-MM-DD（默认今天）')
    parser.add_argument('--dry-run', action='store_true', help='试运行，不实际上传到 OSS')

    # OSS 配置（优先使用命令行参数，其次环境变量）
    oss_group = parser.add_argument_group('OSS 配置（也可通过环境变量设置）')
    oss_group.add_argument('--oss-key-id', default=os.environ.get('OSS_ACCESS_KEY_ID'), help='OSS Access Key ID')
    oss_group.add_argument('--oss-key-secret', default=os.environ.get('OSS_ACCESS_KEY_SECRET'), help='OSS Access Key Secret')
    oss_group.add_argument('--oss-bucket', default=os.environ.get('OSS_BUCKET'), help='OSS Bucket 名称')
    oss_group.add_argument('--oss-region', default=os.environ.get('OSS_REGION', 'oss-cn-shenzhen'), help='OSS Region')
    oss_group.add_argument('--oss-endpoint', default=os.environ.get('OSS_ENDPOINT'), help='OSS Endpoint（优先级高于 region）')

    args = parser.parse_args()

    # ── 验证输入 ──────────────────────────────────────────
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not input_path.is_file():
        print(f"❌ 输入文件不存在: {input_path}")
        sys.exit(1)

    # ── 构建搜索目录 ──────────────────────────────────────
    search_dirs = []
    if args.attachment_dir:
        search_dirs.append(Path(args.attachment_dir).expanduser().resolve())
    search_dirs.append(input_path.parent)

    print(f"📄 输入: {input_path}")
    print(f"📄 输出: {output_path}")
    print(f"📁 图片搜索目录: {', '.join(str(d) for d in search_dirs)}")

    # ── 读取源文件 ────────────────────────────────────────
    text = input_path.read_text(encoding='utf-8')
    source_fm, body = parse_obsidian_frontmatter(text)
    source_tags = source_fm.get('tags', [])
    if source_tags:
        print(f"🏷️  源文件标签: {', '.join(source_tags)}")

    # 统计图片数量
    img_matches = OBSIDIAN_IMG_RE.findall(body)
    print(f"🖼️  发现 {len(img_matches)} 个图片引用")

    if len(img_matches) == 0 and not args.dry_run:
        # 没有图片，跳过上传，只做格式转换
        print("ℹ️  无图片引用，跳过 OSS 上传")
        oss_client = None
    else:
        # ── 初始化 OSS 客户端 ─────────────────────────────
        if args.dry_run:
            oss_client = None
            print("🔍 Dry-run 模式，不会实际上传")
        else:
            if not args.oss_key_id or not args.oss_key_secret or not args.oss_bucket:
                print("❌ 缺少 OSS 配置。请通过参数或环境变量提供：")
                print("   --oss-key-id / OSS_ACCESS_KEY_ID")
                print("   --oss-key-secret / OSS_ACCESS_KEY_SECRET")
                print("   --oss-bucket / OSS_BUCKET")
                sys.exit(1)

            try:
                import oss2
            except ImportError:
                print("❌ 缺少 oss2 库，请运行: pip install oss2")
                sys.exit(1)

            endpoint = args.oss_endpoint or f"https://{args.oss_region}.aliyuncs.com"
            auth = oss2.Auth(args.oss_key_id, args.oss_key_secret)
            oss_client = oss2.Bucket(auth, endpoint, args.oss_bucket)
            print(f"🪣 OSS: {args.oss_bucket} / {args.oss_prefix}")

    # ── 转换图片链接 ──────────────────────────────────────
    if img_matches:
        endpoint = args.oss_endpoint or f"https://{args.oss_region}.aliyuncs.com"
        converted_body, ok, fail = convert_image_links(
            body=body,
            search_dirs=search_dirs,
            oss_client=oss_client,
            oss_prefix=args.oss_prefix,
            bucket_name=args.oss_bucket or '[unknown]',
            endpoint=endpoint,
            dry_run=args.dry_run,
        )
        print(f"\n📊 上传结果: {ok} 成功, {fail} 失败")
    else:
        converted_body = body

    # ── 生成 frontmatter ──────────────────────────────────
    tags_list = args.tags.split(',') if args.tags else []
    title = args.title
    if not title:
        # 从源 frontmatter 或文件名推断
        title = input_path.stem

    frontmatter = generate_frontmatter(
        title=title,
        description=args.description,
        tags=tags_list,
        pub_date=args.pub_date,
        source_tags=source_tags,
    )

    # ── 写入输出文件 ──────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_content = frontmatter + '\n' + converted_body
    output_path.write_text(final_content, encoding='utf-8')
    print(f"\n✅ 已写入: {output_path}")


if __name__ == '__main__':
    main()
