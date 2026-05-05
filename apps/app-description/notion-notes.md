# Notion — Notes & Workspace

Notion is a connected workspace for notes, docs, wikis, and project tracking. This environment covers the **core notes and docs experience** — page creation and editing, nested pages, rich text formatting, databases/tables, templates, sidebar navigation, sharing settings, and workspace management.

## Components to Implement

### Sidebar Navigation (persistent left panel)
- Workspace name and avatar at top (colored square with initial), dropdown to switch workspaces
- Search button (opens search modal)
- Quick actions: New page button, Import button
- Favorites section — starred/pinned pages (draggable to reorder)
- Private section — user's private pages (tree structure with expand/collapse toggles)
  - Each page shows: icon (emoji or default), title, expand arrow if has children
  - Hover reveals: add sub-page button (+), more menu (three dots)
  - Nested pages indent under parent
- Shared section — pages shared with workspace members
- Trash — deleted pages (with restore/permanent delete options)
- Collapse/expand sidebar toggle button

### Page View (main content area)
- Page header:
  - Icon picker button (emoji grid with search, or remove icon)
  - Cover image banner (colored gradient, click to change — preset color options)
  - Page title (large editable heading, placeholder "Untitled")
  - Breadcrumb trail showing page hierarchy (Workspace > Parent > Current)
- Content body:
  - Block-based editing (each line/paragraph is a block)
  - Block types:
    - Text — plain paragraph (default)
    - Heading 1, Heading 2, Heading 3 — different sizes
    - Bulleted list — nested bullets
    - Numbered list — auto-incrementing numbers
    - To-do list — checkboxes with text (toggle complete/incomplete)
    - Quote — indented block with left border
    - Divider — horizontal line separator
    - Callout — colored box with icon + text
    - Code — monospace block with language label
    - Toggle — collapsible content (header + hidden body)
  - Block actions (hover reveals):
    - Drag handle (six dots icon) for reordering
    - Plus (+) button to add block below (opens block type menu)
    - Three-dot menu: Turn into (change block type), Duplicate, Delete, Move to (page picker), Color (text color + background color picker: 8 colors each)
  - Slash command menu — type "/" to open block type picker inline
  - Text formatting toolbar (appears on text selection):
    - Bold, Italic, Underline, Strikethrough, Code (inline), Link, Color

### Page Properties & Settings (top-right or header area)
- Share button — opens sharing modal:
  - Current members with access (name, avatar, permission level)
  - Permission levels: Full access, Can edit, Can view, Can comment
  - Invite people input (email/name) with permission dropdown
  - Copy link button
  - "Anyone with link" toggle with permission level selector
- Favorite/Unfavorite toggle (star icon)
- More menu (three dots):
  - Lock page (prevent editing by others)
  - Page history (list of edit timestamps)
  - Export (Markdown / PDF — label only, no actual export)
  - Move to (page/section picker modal)
  - Duplicate page
  - Delete page (moves to trash)
- Page info: Created by, Created date, Last edited by, Last edited date

### Database / Table View (special page type)
- Table header:
  - Database title (editable)
  - View tabs: Table, Board, List, Calendar (switch layout, at least Table and Board)
  - Filter button (opens filter bar)
  - Sort button (opens sort configurator)
  - New view button
- Table view:
  - Column headers (property names): Title, Status, Priority, Due Date, Assignee, Tags
  - Column types: Text, Select (single dropdown), Multi-select (tags), Date, Person, Checkbox, Number, URL
  - Rows are database entries (each row clickable — opens as a page)
  - Add new row button at bottom ("+ New")
  - Add new column button at right ("+" icon)
  - Column header click: Sort ascending/descending, Filter by this column, Hide column, Edit property (rename, change type)
- Board view (Kanban):
  - Columns grouped by Status property (e.g., Not Started, In Progress, Done)
  - Cards show: title, assignee avatars, priority badge, due date
  - Drag cards between columns to change status
  - Add card button per column
- Filter bar:
  - Add filter rule: Property + Condition + Value (e.g., Status is "In Progress")
  - Multiple filter rules (AND logic)
  - Remove individual filters, Clear all
- Sort configurator:
  - Add sort rule: Property + Direction (ascending/descending)
  - Multiple sort rules with priority order

### Search Modal
- Full-text search input with magnifying glass
- Results: page title, breadcrumb path, snippet of matching content
- Recent pages section (when search is empty)
- Filter by: page type (Page, Database), created by, date range
- Keyboard navigation hint

### Templates
- Template button in new page creation flow
- Template gallery: preset page templates (Meeting Notes, Project Plan, Reading List, Weekly Agenda, Bug Tracker)
- Each template has: name, description, preview of structure
- "Use template" creates a new page pre-filled with the template structure

### Trash / Recently Deleted
- List of deleted pages (title, deleted date, deleted by)
- Restore button — moves page back to original location
- Permanent delete button (with confirmation modal)
- Empty trash button (deletes all, with confirmation)
- Search within trash

### Workspace Settings (separate view)
- Workspace name (editable text input)
- Workspace icon (emoji picker)
- Members list: name, email, role (Admin / Member / Guest)
- Invite member: email input + role dropdown + Send invite button
- Remove member (confirmation modal)
- General settings:
  - Default page font (dropdown: Default, Serif, Mono)
  - Page width (dropdown: Default, Full width)
