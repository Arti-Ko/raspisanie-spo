CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    room TEXT,
    color TEXT
);

CREATE TABLE IF NOT EXISTS teacher_subjects (
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    PRIMARY KEY (teacher_id, subject_id)
);

CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    duration_months INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    program_id INTEGER NOT NULL REFERENCES programs(id) ON DELETE RESTRICT,
    course INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS academic_years (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS calendar_weeks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year_id INTEGER NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    semester INTEGER NOT NULL CHECK (semester IN (1, 2)),
    week_number INTEGER NOT NULL,
    hours INTEGER NOT NULL,
    note TEXT,
    includes_saturday INTEGER NOT NULL DEFAULT 0,
    start_date TEXT,
    UNIQUE (academic_year_id, semester, week_number)
);

CREATE TABLE IF NOT EXISTS curriculum_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    course INTEGER NOT NULL,
    semester INTEGER NOT NULL CHECK (semester IN (1, 2)),
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE RESTRICT,
    hours_theory INTEGER NOT NULL DEFAULT 0,
    hours_practice INTEGER NOT NULL DEFAULT 0,
    hours_exam INTEGER NOT NULL DEFAULT 0,
    lesson_type TEXT NOT NULL DEFAULT 'theory' CHECK (lesson_type IN ('theory', 'practice', 'lab')),
    is_double_pair INTEGER NOT NULL DEFAULT 0,
    UNIQUE (program_id, course, semester, subject_id)
);

CREATE TABLE IF NOT EXISTS bell_schedule_days (
    day_of_week INTEGER PRIMARY KEY CHECK (day_of_week BETWEEN 1 AND 6),
    has_zero_period INTEGER NOT NULL DEFAULT 0,
    zero_period_start TEXT,
    zero_period_end TEXT
);

CREATE TABLE IF NOT EXISTS bell_schedule_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 6),
    pair_number INTEGER NOT NULL CHECK (pair_number BETWEEN 1 AND 4),
    lesson_number INTEGER NOT NULL CHECK (lesson_number IN (1, 2)),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    UNIQUE (day_of_week, pair_number, lesson_number)
);

DROP TABLE IF EXISTS bell_times;

INSERT OR IGNORE INTO bell_schedule_days (day_of_week, has_zero_period, zero_period_start, zero_period_end)
    SELECT d.day, 0, NULL, NULL
    FROM (SELECT 1 AS day UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) d;

INSERT OR IGNORE INTO bell_schedule_lessons (day_of_week, pair_number, lesson_number, start_time, end_time)
    SELECT d.day, p.pair_number, p.lesson_number, p.start_time, p.end_time
    FROM (SELECT 1 AS day UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) d
    CROSS JOIN (
        SELECT 1 AS pair_number, 1 AS lesson_number, '08:10' AS start_time, '08:55' AS end_time UNION ALL
        SELECT 1, 2, '09:00', '09:45' UNION ALL
        SELECT 2, 1, '09:55', '10:40' UNION ALL
        SELECT 2, 2, '10:45', '11:30' UNION ALL
        SELECT 3, 1, '12:00', '12:45' UNION ALL
        SELECT 3, 2, '12:50', '13:35' UNION ALL
        SELECT 4, 1, '13:45', '14:30' UNION ALL
        SELECT 4, 2, '14:35', '15:20'
    ) p;

CREATE TABLE IF NOT EXISTS teacher_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    curriculum_item_id INTEGER NOT NULL REFERENCES curriculum_items(id) ON DELETE CASCADE,
    transferred_hours INTEGER NOT NULL DEFAULT 0,
    UNIQUE (group_id, curriculum_item_id)
);

CREATE TABLE IF NOT EXISTS schedule_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    calendar_week_id INTEGER NOT NULL REFERENCES calendar_weeks(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    assignment_id INTEGER NOT NULL REFERENCES teacher_assignments(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 6),
    pair_number INTEGER NOT NULL CHECK (pair_number BETWEEN 0 AND 4),
    room TEXT,
    substitute_teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
    UNIQUE (group_id, calendar_week_id, day_of_week, pair_number)
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
