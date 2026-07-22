CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    room TEXT
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
    UNIQUE (program_id, course, semester, subject_id)
);

CREATE TABLE IF NOT EXISTS bell_times (
    pair_number INTEGER PRIMARY KEY,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL
);

INSERT OR IGNORE INTO bell_times (pair_number, start_time, end_time) VALUES
    (1, '08:30', '10:00'),
    (2, '10:10', '11:40'),
    (3, '11:50', '13:20'),
    (4, '13:50', '15:20'),
    (5, '15:30', '17:00');

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
    pair_number INTEGER NOT NULL CHECK (pair_number BETWEEN 1 AND 5),
    room TEXT,
    substitute_teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
    UNIQUE (group_id, calendar_week_id, day_of_week, pair_number)
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
