# Linked databases

Source: https://www.notion.so/help/linked-databases

---

A linked database is a view of an existing database placed on a different page. It mirrors the same data but can have its own filters, sorts, and view configuration.

## Create a linked database

1. Navigate to any page where you want to display database entries.
2. Type `/linked` and select **Linked view of database**.
3. Search for the database you want to link to.
4. Select it — a view of that database appears on the current page.

## How linked databases work

- The data is the same — adding, editing, or deleting entries in a linked database affects the source.
- Filters, sorts, and visible properties are independent per linked view.
- You can have multiple linked views of the same database on different pages.
- Changes to the source database schema (new properties, renamed properties) propagate to all linked views.

## Configure a linked view

1. Click **•••** on the linked database.
2. Customize independently:
   - Add/remove **filters** specific to this view.
   - Add/remove **sorts** specific to this view.
   - Toggle **visible properties** for this view.
   - Choose a different **view type** (Table, Board, Gallery, etc.).

## Use cases

- Show "My Tasks" on your personal dashboard (filtered to your name from the team Tasks database).
- Display upcoming deadlines on a project page (filtered to entries with dates this week).
- Show recent entries on a home page (sorted by created time, descending).

## Identify a linked database

- Linked databases show a small **↗** arrow icon next to the database title.
- Clicking the title arrow navigates to the source database.
- The title shows the source database name (you can rename the linked view title without changing the source).

## Copy link to view vs. duplicate

- **Copy link to view**: shares the same underlying data.
- **Duplicate**: creates a completely new, independent database with copied data (not linked).
