# Slack — Team Messaging

Slack is a workplace communication platform built around channels, direct messages, and threads. This environment covers the **core messaging experience** — channel management, direct messages, threaded conversations, message composition with formatting, reactions, file sharing references, user presence, notifications, and workspace settings.

## Components to Implement

### Sidebar Navigation (persistent left panel)
- Workspace name and icon at top (colored square with letter), dropdown menu (Workspace Settings, Invite People)
- Compose button (opens new message modal)
- Search bar at top
- Sections (each collapsible with expand/collapse arrow):
  - Channels section:
    - List of joined channels with # icon (e.g., #general, #engineering, #design, #random, #product, #announcements, #help, #social)
    - Unread badge (bold name + count) for channels with new messages
    - Muted channels appear dimmed
    - "Add channels" link at bottom (opens channel browser)
  - Direct Messages section:
    - List of recent DM conversations (user avatar circle, name, presence dot: green=online, gray=offline)
    - Group DM entries show multiple avatar circles + combined names
    - Unread badge for DMs with new messages
    - "Add teammates" link at bottom
  - Apps section:
    - Installed app integrations (Jira, GitHub, Google Calendar — icon + name)
- Starred items section (pinned channels/DMs)

### Channel View (main content area)
- Channel header:
  - Channel name (#channel-name) with # icon
  - Channel topic/description (editable — click to edit inline, short text)
  - Member count (clickable — opens member list panel)
  - Star/Unstar toggle
  - Pin icon (shows pinned messages panel)
  - Search icon (search within channel)
  - More menu (three dots): Channel details, Edit channel, Mute channel, Leave channel
- Messages area (scrollable, newest at bottom):
  - Message block: avatar circle, sender name (bold), timestamp, message text
  - Message hover actions bar: React (emoji picker), Reply (opens thread), Share (forward), More (three dots: Edit, Delete, Pin, Mark unread, Copy link)
  - Rich message content:
    - @mentions highlighted in blue background
    - #channel-links highlighted and clickable
    - URLs rendered as clickable links with preview card (title, description, domain)
    - Code blocks (monospace background) — inline `code` and multi-line ```code blocks```
    - Bold, italic, strikethrough text formatting
    - Bulleted and numbered lists
    - Blockquotes (left border + indent)
    - File attachment references (file icon, filename, size — no actual upload)
  - Reactions row below message: emoji + count badges (clickable to add/remove your reaction)
  - "New messages" divider line (red) separating read/unread
  - Date separators between different days ("Today", "Yesterday", "May 3, 2026")
  - System messages: "User joined #channel", "User set the channel topic to..."
- Thread indicator: if a message has replies, show "N replies" link + last replier avatars (clicking opens thread panel)
- Message composer (bottom):
  - Rich text input area with placeholder "Message #channel-name"
  - Formatting toolbar: Bold (B), Italic (I), Strikethrough (S), Code (</> icon), Link, Bulleted list, Numbered list, Blockquote, Code block
  - Action buttons row: Attach file (paperclip icon), Emoji picker (smiley icon), @mention (@ icon), Slash commands (/ icon)
  - Send button (paper plane icon, active when input has text)

### Thread Panel (right sidebar, opens alongside main channel)
- Thread header: "Thread" title, "in #channel-name", close button (X)
- Original message at top (full message block with reactions)
- Reply messages below (same format as channel messages but more compact)
- Reply composer at bottom (same as channel composer but placeholder "Reply...")
- "Also send to #channel-name" checkbox option
- Reply count and participant avatars summary

### Direct Message View
- DM header: user avatar + name (or group names for group DM), presence status (Active/Away), profile link
- Messages area (same format as channel messages)
- Message composer (placeholder "Message @username")
- For group DMs: header shows all member names, member count

### Channel Browser (modal or panel)
- "Browse channels" header
- Search channels input
- Tabs: All Channels, Joined, Archived
- Channel list: # icon, channel name, member count, description snippet, Join button (or "Joined" badge)
- Create channel button: opens modal with Name input, Description textarea, Visibility toggle (Public/Private)

### User Profile Panel (right sidebar, opens when clicking username/avatar)
- Large avatar circle (colored with initials)
- Display name (bold), title/role, pronouns
- Status emoji and text (e.g., "🎯 In a meeting")
- Presence indicator (Active / Away / Do Not Disturb)
- Local time display
- Contact info: email, phone (if set)
- Action buttons: Message, Huddle (audio call icon — visual only), More (three dots)
- "View full profile" link

### Search (modal overlay)
- Search input with magnifying glass, filter options below
- Filter chips: From (user picker), In (channel picker), Date range, Has (file/link/reaction)
- Results list: message snippet with sender, channel, timestamp, highlight matching terms
- Result click navigates to the message in context
- Recent searches (when input empty)

### Emoji Picker (popover)
- Category tabs: Smileys, People, Nature, Food, Activity, Travel, Objects, Symbols
- Search emoji input
- Frequently used section at top
- Grid of emoji icons (click to select)
- Skin tone selector

### Notifications & Preferences
- Notification bell icon in sidebar header with unread count badge
- Notification preferences per channel:
  - All messages / Mentions only / Nothing
  - Mute channel toggle (with duration: 15 min, 1 hr, 8 hrs, 24 hrs, until turned off)
- Global notification settings (separate page):
  - Desktop notifications toggle (on/off)
  - Sound toggle (on/off)
  - Notification schedule: "Allow notifications" time window (start/end time inputs)
  - Do Not Disturb schedule
  - Keywords that trigger notifications (comma-separated text input)

### Workspace Settings (separate page)
- Workspace name (editable)
- Workspace icon/avatar (color picker — 8 preset colors)
- Default channels for new members (multi-select from channel list)
- Permissions:
  - Who can create channels (Everyone / Admins only)
  - Who can post in #general (Everyone / Admins only)
  - Message editing window (dropdown: Any time, 5 min, 30 min, 1 hr, Never)
  - Message deletion permissions (Everyone / Admins only)
- Members management:
  - Member list: avatar, name, email, role (Owner/Admin/Member/Guest), status
  - Invite people button (email input + role dropdown)
  - Change role dropdown
  - Deactivate member button (confirmation modal)

### User Status & Presence
- Status modal (click on workspace name or own avatar):
  - Emoji picker for status icon
  - Status text input (e.g., "In a meeting", "Working remotely", "On vacation")
  - "Clear after" dropdown: Don't clear, 30 min, 1 hr, 4 hrs, Today, This week
  - Preset statuses: In a meeting, Commuting, Out sick, Vacationing, Working remotely
- Set self as Away/Active toggle
- Do Not Disturb toggle with "Until" time picker

### Pinned Messages Panel (right sidebar)
- "Pinned messages" header with count
- List of pinned messages (message block format: sender, timestamp, text)
- Unpin button per message
- "Pin a message" instruction text when empty
