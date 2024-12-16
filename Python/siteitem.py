import sqlfunc
import re

weblist = [[],[],[]]
db = sqlfunc.Sitedb()
db.connect('sites.db')
with open("web.txt",'r',encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        # 删除line中所有空格和换行符
        line = line.replace('\n','')
        line = line.replace(' ','')
        result = re.split(r',',line)
        if len(result) != 3:
            raise Exception(f'Error splited {result}')
        name = result[0]
        siteurl = result[1]
        caption = result[2]
        db.insert(name,siteurl,caption)
db.close()
        
web = sqlfunc.GenerateWeb()
web.generate('sites.db')
