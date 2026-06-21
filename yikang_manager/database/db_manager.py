"""
颐康管家 - 数据库管理器
负责 SQLite 连接管理、建表、以及对敏感字段的透明加密/解密。
所有敏感医疗数据均加密存储于本地，不上传云端。
"""
import sqlite3
from contextlib import contextmanager

from config import DB_PATH, ENCRYPTED_FIELDS
from database.schema import get_schema
from utils.crypto import crypto


class DatabaseManager:
    """SQLite 数据库连接管理器，采用单例模式。"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.execute("PRAGMA journal_mode = WAL")
        self._init_schema()
        self._initialized = True

    def _init_schema(self):
        """初始化数据库表结构。"""
        self._conn.executescript(get_schema())
        self._conn.commit()

    @contextmanager
    def get_cursor(self):
        cursor = self._conn.cursor()
        try:
            yield cursor
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cursor.close()

    def _encrypt_row(self, table: str, data: dict) -> dict:
        """对数据行中的敏感字段进行加密。"""
        fields = ENCRYPTED_FIELDS.get(table, [])
        result = dict(data)
        for field in fields:
            if field in result and result[field] is not None:
                result[field] = crypto.encrypt(result[field])
        return result

    def _decrypt_row(self, table: str, row: sqlite3.Row) -> dict:
        """对查询结果行中的敏感字段进行解密。"""
        fields = ENCRYPTED_FIELDS.get(table, [])
        result = dict(row)
        for field in fields:
            if field in result and result[field] is not None:
                result[field] = crypto.decrypt(result[field])
        return result

    def insert(self, table: str, data: dict) -> int:
        """插入一条记录，自动加密敏感字段，返回新记录ID。"""
        data = self._encrypt_row(table, data)
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        with self.get_cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            return cursor.lastrowid

    def update(self, table: str, record_id: int, data: dict) -> int:
        """更新一条记录，自动加密敏感字段。"""
        data = self._encrypt_row(table, data)
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        params = tuple(data.values()) + (record_id,)
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount

    def delete(self, table: str, record_id: int) -> int:
        """删除一条记录。"""
        sql = f"DELETE FROM {table} WHERE id = ?"
        with self.get_cursor() as cursor:
            cursor.execute(sql, (record_id,))
            return cursor.rowcount

    def fetch_one(self, table: str, record_id: int) -> dict:
        """查询单条记录并解密。"""
        sql = f"SELECT * FROM {table} WHERE id = ?"
        with self.get_cursor() as cursor:
            cursor.execute(sql, (record_id,))
            row = cursor.fetchone()
        return self._decrypt_row(table, row) if row else None

    def fetch_all(self, table: str, where: str = "", params: tuple = ()) -> list:
        """查询多条记录并解密。"""
        sql = f"SELECT * FROM {table}"
        if where:
            sql += f" WHERE {where}"
        sql += " ORDER BY id"
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        return [self._decrypt_row(table, row) for row in rows]

    def fetch_by_query(self, sql: str, params: tuple = (), table: str = None) -> list:
        """执行自定义查询并解密结果。"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        if table:
            return [self._decrypt_row(table, row) for row in rows]
        return [dict(row) for row in rows]

    def execute(self, sql: str, params: tuple = ()) -> int:
        """执行原生 SQL（用于统计等）。"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount

    def close(self):
        if self._conn:
            self._conn.close()


db = DatabaseManager()
