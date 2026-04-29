"""
京麦商品发布自动化 - 数据库初始化脚本
建表 + 验证连接
"""
from db import DatabaseManager
from settings import get_settings


def init_db():
    """初始化数据库，创建所有表"""
    settings = get_settings()
    db = DatabaseManager(
        mysql_url=settings.MYSQL_URL,
        sqlite_url=settings.SQLITE_URL,
    )
    db.create_tables()
    print(f"[DB] 初始化完成，使用 {db.db_type}")
    return db


if __name__ == "__main__":
    init_db()
