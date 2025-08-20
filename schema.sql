CREATE TABLE IF NOT EXISTS "users" (
    "id"    INTEGER NOT NULL UNIQUE,
    "username" TEXT NOT NULL UNIQUE,
    "hash"  TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "teams" (
    "id"    INTEGER NOT NULL UNIQUE,
    "code"  TEXT NOT NULL,
    "name"  TEXT NOT NULL UNIQUE,
    "description" TEXT,
    "access_type" TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "team_members" (
    "team_id"   INTEGER NOT NULL,
    "user_id"   INTEGER NOT NULL,
    "privilege" TEXT,
    CONSTRAINT "fk_team_members_team_id" FOREIGN KEY("team_id") REFERENCES "teams"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_team_members_user_id" FOREIGN KEY("user_id") REFERENCES "users"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "notes" (
    "id"      INTEGER NOT NULL UNIQUE,
    "content" TEXT NOT NULL,
    "due_by"  INTEGER,
    "type"    TEXT NOT NULL,
    "status"  TEXT NOT NULL,
    "topic_id" INTEGER NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("topic_id") REFERENCES "topics"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "topics" (
    "id"    INTEGER NOT NULL UNIQUE,
    "name"  TEXT NOT NULL,
    "team_id" INTEGER NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("team_id") REFERENCES "teams"("id") ON DELETE CASCADE
);