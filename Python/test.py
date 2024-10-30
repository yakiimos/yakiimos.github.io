import sqlite3

conn = sqlite3.connect('sites.db')
print('Open database successfully')
cursor = conn.cursor()

# create table
cursor.execute(
    '''CREATE TABLE SITES
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL,
    URL TEXT NOT NULL,
    CAPTION TEXT
    );'''
)
conn.commit()
# conn.close()

# insert data
cursor.execute(
    "INSERT INTO SITES (ID,NAME,URL,CAPTION) \
    VALUES (1,'菜鸟教程','runoob.com','编程相关文字教程')"
)
conn.commit()
conn.close

# # query data
# data = cursor.execute("SELECT id,name,url,caption from SITES")
# for datum in data:
#     print("ID = ", datum[0])
#     print("NAME = ", datum[1])
#     print("URL = ", datum[2])
#     print("CAPTION = ", datum[3], "\n")
# conn.close

# # update data
# cursor.execute("""UPDATE SITES set URL = "www.runoob.com" where ID=1 """)
# conn.commit()

# # delete data
# c.execute("DELETE from COMPANY where ID=2;")
# conn.commit()