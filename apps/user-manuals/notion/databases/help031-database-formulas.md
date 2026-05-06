# Database formulas

Source: https://www.notion.so/help/formulas

---

Formula properties let you compute values dynamically based on other properties in the same database entry.

## Create a formula property

1. Open a database.
2. Click **+** to add a new property.
3. Select **Formula** as the property type.
4. The formula editor opens.
5. Write your formula and click **Done**.

## Formula editor

- The editor shows available properties, constants, operators, and functions.
- Click a property name to insert it (wrapped in `prop("Property Name")`).
- Formulas support nesting — you can use functions inside functions.
- Syntax errors are highlighted in red with an explanation.

## Referencing properties

Use the `prop()` function to reference other properties:
- `prop("Status")` — returns the value of the Status property.
- `prop("Due Date")` — returns the date value.
- `prop("Price")` — returns the number value.

## Common operators

- `+` — addition (numbers) or concatenation (text)
- `-` — subtraction
- `*` — multiplication
- `/` — division
- `==` — equals
- `!=` — not equals
- `>`, `<`, `>=`, `<=` — comparisons
- `and`, `or`, `not` — logical operators

## Useful functions

### Text functions
- `length(text)` — character count
- `contains(text, search)` — true if text contains search
- `replace(text, old, new)` — replace first occurrence
- `replaceAll(text, old, new)` — replace all occurrences
- `lower(text)` / `upper(text)` — case conversion
- `slice(text, start, end)` — extract substring

### Number functions
- `abs(number)` — absolute value
- `round(number)` — round to nearest integer
- `floor(number)` / `ceil(number)` — round down/up
- `min(a, b)` / `max(a, b)` — minimum/maximum
- `toNumber(value)` — convert to number

### Date functions
- `now()` — current date and time
- `dateAdd(date, number, unit)` — add time to a date
- `dateSubtract(date, number, unit)` — subtract time from a date
- `dateBetween(date1, date2, unit)` — difference between dates
- `formatDate(date, format)` — format as text
- `minute(date)`, `hour(date)`, `day(date)`, `month(date)`, `year(date)` — extract parts

### Logical functions
- `if(condition, true_value, false_value)` — conditional logic
- `empty(value)` — true if value is empty

## Example formulas

- Days until due: `dateBetween(prop("Due Date"), now(), "days")`
- Full name: `prop("First Name") + " " + prop("Last Name")`
- Overdue check: `if(prop("Due Date") < now() and prop("Status") != "Done", "⚠️ Overdue", "")`
- Price with tax: `prop("Price") * 1.08`
- Progress label: `if(prop("Complete") == true, "✅ Done", "⏳ Pending")`
