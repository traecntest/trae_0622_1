"""
颐康管家 - 数据库表结构定义
定义 SQLite 数据库中所有表的建表语句。
"""

SCHEMA_SQL = """
-- 家庭成员档案表
CREATE TABLE IF NOT EXISTS family_members (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    gender      TEXT,
    birth_date  TEXT,
    id_card     TEXT,
    phone       TEXT,
    relation    TEXT,
    parent_id   INTEGER,
    blood_type  TEXT,
    allergy     TEXT,
    note        TEXT,
    created_at  TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (parent_id) REFERENCES family_members(id)
);

-- 体检报告记录表
CREATE TABLE IF NOT EXISTS health_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id       INTEGER NOT NULL,
    record_date     TEXT NOT NULL,
    category        TEXT,
    indicator_name  TEXT NOT NULL,
    indicator_value TEXT,
    unit            TEXT,
    reference_range TEXT,
    is_abnormal     INTEGER DEFAULT 0,
    report_image    TEXT,
    note            TEXT,
    created_at      TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (member_id) REFERENCES family_members(id) ON DELETE CASCADE
);

-- 用药记录表
CREATE TABLE IF NOT EXISTS medications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id   INTEGER NOT NULL,
    drug_name   TEXT NOT NULL,
    dosage      TEXT,
    frequency   TEXT,
    start_date  TEXT,
    end_date    TEXT,
    note        TEXT,
    created_at  TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (member_id) REFERENCES family_members(id) ON DELETE CASCADE
);

-- 提醒事项表
CREATE TABLE IF NOT EXISTS reminders (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id     INTEGER,
    title         TEXT NOT NULL,
    content       TEXT,
    remind_type   TEXT,
    remind_time   TEXT NOT NULL,
    repeat_rule   TEXT,
    is_done       INTEGER DEFAULT 0,
    created_at    TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (member_id) REFERENCES family_members(id) ON DELETE SET NULL
);

-- 病史记录表
CREATE TABLE IF NOT EXISTS medical_history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id     INTEGER NOT NULL,
    disease_name  TEXT NOT NULL,
    diagnose_date TEXT,
    hospital      TEXT,
    status        TEXT,
    description   TEXT,
    created_at    TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (member_id) REFERENCES family_members(id) ON DELETE CASCADE
);

-- 创建索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_records_member ON health_records(member_id);
CREATE INDEX IF NOT EXISTS idx_records_indicator ON health_records(indicator_name);
CREATE INDEX IF NOT EXISTS idx_records_date ON health_records(record_date);
CREATE INDEX IF NOT EXISTS idx_med_member ON medications(member_id);
CREATE INDEX IF NOT EXISTS idx_reminders_member ON reminders(member_id);
CREATE INDEX IF NOT EXISTS idx_history_member ON medical_history(member_id);
"""


def get_schema():
    return SCHEMA_SQL
