-- Class survey schema matching the CSVs in this folder.
-- Load order: students, tools, availability_slots, then the two junction tables.

CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    netid TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    school_year TEXT NOT NULL
        CHECK (school_year IN ('First-year', 'Sophomore', 'Junior', 'Senior')),
    intro_programming TEXT NOT NULL
        CHECK (intro_programming IN ('took_it', 'equivalent', 'neither')),
    skill_programming SMALLINT NOT NULL
        CHECK (skill_programming BETWEEN 1 AND 5),
    skill_data_stats SMALLINT NOT NULL
        CHECK (skill_data_stats BETWEEN 1 AND 5),
    skill_frontend_design SMALLINT NOT NULL
        CHECK (skill_frontend_design BETWEEN 1 AND 5),
    skill_business_pitch SMALLINT NOT NULL
        CHECK (skill_business_pitch BETWEEN 1 AND 5),
    working_style TEXT,
    interests TEXT,
    semester_goal TEXT,
    submitted_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE tools (
    tool_id SERIAL PRIMARY KEY,
    tool_name TEXT NOT NULL UNIQUE
);

CREATE TABLE availability_slots (
    slot_id SERIAL PRIMARY KEY,
    slot_name TEXT NOT NULL UNIQUE
);

-- Many-to-many: a student can know many tools; a tool can belong to many students.
CREATE TABLE student_tools (
    student_id INTEGER NOT NULL
        REFERENCES students (student_id) ON DELETE CASCADE,
    tool_id INTEGER NOT NULL
        REFERENCES tools (tool_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, tool_id)
);

-- Many-to-many: a student can be free in many slots; a slot can match many students.
CREATE TABLE student_availability (
    student_id INTEGER NOT NULL
        REFERENCES students (student_id) ON DELETE CASCADE,
    slot_id INTEGER NOT NULL
        REFERENCES availability_slots (slot_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, slot_id)
);
