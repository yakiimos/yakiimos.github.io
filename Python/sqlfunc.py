import sqlite3

class Sitedb():
    def connect(self, DATABASE):
        self.conn = sqlite3.connect(DATABASE)
        self.cur = self.conn.cursor()

    def close(self):
        self.conn.close()

    def insert(self, name, weburl, caption):
        try:
            self.cur.execute("INSERT INTO sites (NAME,URL,CAPTION) VALUES (?,?,?)", (name, weburl, caption))
            self.conn.commit()
        except:
            raise Exception('数据库插入数据失败')
        
    def deleteByid(self, id):
        self.cur.execute("DELETE FROM sites WHERE ID=?", (id,))
        self.conn.commit()

class GenerateWeb():
    def generate(self, DATABASE):
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        with open('./templates/index.html','r',encoding='utf-8') as f:
        with open('web.html','w',encoding='utf-8') as f:
            f.write("")