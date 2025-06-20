import sqlite3

def create_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            name TEXT,
            description TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT (datetime('now', '+8 hours')),
            updated_at TIMESTAMP DEFAULT (datetime('now', '+8 hours'))
        );
    """)
    cursor.execute("""
        CREATE TRIGGER update_last_modified
        AFTER UPDATE ON sites
        FOR EACH ROW
        BEGIN
            UPDATE sites
            SET updated_at = (datetime('now', '+8 hours'))
            WHERE id = OLD.id;
        END;
    """)
    conn.commit()
    conn.close()
def write_database(db_path, sites: list[dict]):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for site in sites:
        cursor.execute(
            "INSERT INTO sites (url, name, description, tags) VALUES (?, ?, ?, ?)",
            (site.get('url'), site.get('name'), site.get('description'), site.get('tags'))
        )
    
    conn.commit()
    conn.close()

def fetch_data(db_path):
    query = 'SELECT * FROM sites'
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 执行查询
    cursor.execute(query)
    
    # 获取列名
    columns = [desc[0] for desc in cursor.description]
    
    # 将每一条记录转换为字典
    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # 关闭连接
    cursor.close()
    conn.close()
    
    return result