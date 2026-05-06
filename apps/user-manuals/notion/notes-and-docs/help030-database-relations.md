# Database relations and rollups

Source: https://www.notion.so/help/relations-and-rollups

---

Relations connect entries between databases. Rollups compute values from related entries.

## Relations

### Create a relation property

1. Open a database.
2. Click **+** to add a new property.
3. Select **Relation** as the property type.
4. Choose the target database to relate to (can be the same database for self-relations).
5. Name the property (e.g., "Tasks", "Parent Project", "Related Articles").
6. Click **Create relation**.

### Two-way relations

- When you create a relation, Notion asks if you want a two-way relation.
- **Two-way**: A matching relation property appears in the target database automatically.
- **One-way**: Only the current database shows the relation; the target doesn't.
- Example: Projects database has "Tasks" relation → Tasks database automatically gets "Project" relation.

### Add related entries

1. Click the relation property cell for an entry.
2. A search popup appears showing entries from the target database.
3. Click entries to link them.
4. You can link multiple entries to one relation cell.
5. Linked entries appear as clickable pills showing their titles.

### Remove a relation

- Click the relation cell, then click the **X** on a linked entry to unlink it.

## Rollups

### What rollups do

Rollups compute a summary value from a property in related entries. They require an existing relation property.

### Create a rollup property

1. Click **+** to add a new property.
2. Select **Rollup** as the type.
3. Configure three settings:
   - **Relation**: which relation property to pull from.
   - **Property**: which property in the related entries to compute on.
   - **Calculate**: the computation to apply.

### Calculation options

- **Show original** — list all values.
- **Count all** — total number of related entries.
- **Count values** — count of non-empty values.
- **Count unique values** — count of distinct values.
- **Count empty** — count of entries where property is empty.
- **Count not empty** — count of entries where property is filled.
- **Percent empty** / **Percent not empty** — percentage.
- **Sum** — sum of number values.
- **Average** — average of number values.
- **Median** — median of number values.
- **Min** / **Max** — smallest/largest number value.
- **Range** — difference between max and min.
- **Earliest date** / **Latest date** — for date properties.
- **Date range** — span between earliest and latest.
- **Checked** / **Unchecked** — for checkbox properties.

### Example use case

- **Projects** database has relation to **Tasks**.
- Add a rollup on Tasks → Status → Percent not empty where Status = "Done".
- This shows project completion percentage based on done tasks.
