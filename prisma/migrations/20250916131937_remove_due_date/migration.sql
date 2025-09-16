/*
  Warnings:

  - You are about to drop the column `dueDate` on the `Project` table. All the data in the column will be lost.

*/
-- RedefineTables
PRAGMA defer_foreign_keys=ON;
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Project" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "notes" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL,
    "isArchived" BOOLEAN NOT NULL DEFAULT false,
    "eventDate" DATETIME NOT NULL,
    "type" TEXT NOT NULL,
    "titleVideo" TEXT,
    "city" TEXT,
    "civilUnionDetails" TEXT,
    "prep" TEXT,
    "church" TEXT,
    "session" TEXT,
    "restaurant" TEXT,
    "detailsExtra" TEXT,
    "editStatus" TEXT NOT NULL DEFAULT 'Pending',
    "editingPreferences" TEXT,
    "userId" TEXT NOT NULL,
    "adminNotifiedOfChanges" BOOLEAN NOT NULL DEFAULT false,
    CONSTRAINT "Project_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_Project" ("adminNotifiedOfChanges", "church", "city", "civilUnionDetails", "createdAt", "detailsExtra", "editStatus", "editingPreferences", "eventDate", "id", "isArchived", "name", "notes", "prep", "restaurant", "session", "status", "titleVideo", "type", "updatedAt", "userId") SELECT "adminNotifiedOfChanges", "church", "city", "civilUnionDetails", "createdAt", "detailsExtra", "editStatus", "editingPreferences", "eventDate", "id", "isArchived", "name", "notes", "prep", "restaurant", "session", "status", "titleVideo", "type", "updatedAt", "userId" FROM "Project";
DROP TABLE "Project";
ALTER TABLE "new_Project" RENAME TO "Project";
PRAGMA foreign_keys=ON;
PRAGMA defer_foreign_keys=OFF;
