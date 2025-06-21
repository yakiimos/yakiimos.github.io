def read_sites_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 使用两个换行符作为分隔符来分割内容（即按空行分隔）
    groups = content.strip().split('\n\n')
    sites = []
    for group in groups:
        group = group.strip().split('\n')
        site = {'url': group[0]}
        if len(group) >= 2:
            site['name'] = group[1]
        if len(group) >= 3:
            site['description'] = group[2]
        if len(group) >= 4:
            if 'tags' in group[3]:
                site['tags'] = group[3].split(':')[1]
            else:
                raise ValueError(f"无效的标签出现在：\n{group}\n")
        if len(group) >= 5:
            raise ValueError(f"过长的字段出现在：\n{group}\n")
        sites.append(site)
    return sites