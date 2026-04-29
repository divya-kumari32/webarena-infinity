# Spotify — Music Streaming

Spotify is a digital music streaming service. This environment covers the **core music experience** — library management, playback controls, playlist curation, artist/album browsing, search and discovery, queue management, and user profile settings.

## Components to Implement

### Home / Dashboard
- Greeting banner based on time of day ("Good morning", "Good afternoon", "Good evening")
- Recently played section — horizontal scrollable row of album/playlist cards (artwork placeholder, title, subtitle)
- Made for You section — personalized playlist cards (Daily Mix 1-6, Discover Weekly, Release Radar)
- New releases section — recently released album cards
- Jump back in section — quick-access cards for frequently visited playlists/albums

### Search & Discovery
- Search bar (text input with clear button, magnifying glass icon)
- Browse all categories grid when no query active:
  - Genre cards (Pop, Rock, Electronic, Hip-Hop, R&B, Indie, Jazz, Classical, Latin, Country, Metal, Folk) with colored backgrounds
  - Mood cards (Chill, Workout, Focus, Party, Sleep, Travel)
- Search results when query is active:
  - Top result card (best match — song, artist, or playlist)
  - Songs section — list of matching songs (title, artist, album, duration)
  - Artists section — matching artist cards (circular avatar, name, "Artist" label)
  - Albums section — matching album cards (cover, name, artist, year)
  - Playlists section — matching playlist cards (cover, name, owner)
- Filter chips (All, Songs, Artists, Albums, Playlists) to narrow results

### Your Library
- Tab bar: Playlists, Artists, Albums
- Playlists tab:
  - Liked Songs shortcut card (with heart icon, song count)
  - User-created and followed playlists as a vertical list (cover, name, type label, owner)
  - Sort by: recently added, alphabetical, creator, custom order
  - Search within library (filter by name)
- Artists tab:
  - Grid of followed artists (circular avatar, name)
  - Sort by: recently added, alphabetical
- Albums tab:
  - Grid of saved albums (cover, name, artist)
  - Sort by: recently added, alphabetical

### Playlist Detail View
- Playlist header:
  - Cover image placeholder (colored square with gradient)
  - Playlist name (editable via click — opens edit modal)
  - Description (editable via click — opens edit modal)
  - Owner name, like count, total duration, song count
  - Collaborative badge (if collaborative)
- Action buttons: Play, Shuffle, Like/Unlike playlist, More options dropdown (Edit details, Delete playlist, Make collaborative/Remove collaborative, Share)
- Song list table:
  - Columns: # (track number / play icon on hover), Title + Artist, Album, Date Added, Duration
  - Row hover: play button replaces track number, like heart appears
  - Right-click / three-dot menu per song: Add to queue, Add to playlist (submenu of user playlists), Remove from this playlist, Go to artist, Go to album, Like/Unlike
- Drag-and-drop reorder (move songs within playlist)
- "Find something new" search bar at bottom of playlist (search songs to add)

### Album Detail View
- Album header:
  - Cover placeholder (colored square)
  - Album name, artist name (clickable link to artist page), release year, genre, song count, total duration
- Track list:
  - Columns: # (track number), Title, Duration
  - Row hover: play icon, like heart, add-to-playlist icon
- "More from [Artist]" section at bottom — other album cards by the same artist

### Artist Page
- Artist header:
  - Large avatar placeholder (circular, colored)
  - Artist name, monthly listener count, genre label
  - Follow / Unfollow button
- Popular songs section (top 5 songs by the artist, expandable to show all)
  - Columns: #, Title, Album, Duration
- Discography section:
  - Album cards (cover, name, year, type label: Album / Single / EP)
  - Filter: Albums, Singles, Compilations
- Related artists section — horizontal row of artist cards
- About section — artist bio text, follower count

### Now Playing Bar (persistent bottom bar)
- Left section: current song info (cover placeholder, song title, artist name, like heart button)
- Center section:
  - Shuffle button (toggle, green when active)
  - Previous track button
  - Play/Pause button (circular, larger)
  - Next track button
  - Repeat button (cycles: off, repeat all, repeat one — icon changes per mode, green when active)
  - Progress bar (clickable to seek, shows elapsed/remaining time labels)
- Right section:
  - Now Playing / Queue button (navigates to queue view)
  - Volume icon (mute toggle) + volume slider (horizontal bar, clickable/draggable)
  - Full-screen toggle icon (visual only)

### Queue View
- Now Playing section — currently playing song card
- Next in Queue section — manually queued songs with remove button per item
- Next From section — upcoming songs from current playlist/album context
- Clear queue button
- Drag-and-drop reorder within the manual queue

### Liked Songs
- Header: "Liked Songs" with heart icon, song count, total duration
- Play and Shuffle buttons
- Song list table (same columns as playlist: #, Title + Artist, Album, Date Added, Duration)
- Sort by: recently added, title, artist, album, duration
- Search within liked songs

### User Profile
- Profile header:
  - Avatar (colored circle with initials)
  - Display name (editable — click to open modal)
  - Email (read-only display)
  - Subscription plan badge (Free / Premium)
  - Follower count, following count
- Edit profile section:
  - Change display name (text input modal)
  - Change bio / about text (textarea modal)
  - Avatar color selection (preset color palette: 8 colors)
- Public playlists section — list of user's non-private playlists
- Recently played artists section

### Playback & Audio Controls
- Play/Pause toggle — updates playback state globally
- Next/Previous track — advances or goes back in current context (queue, playlist, album)
- Shuffle toggle — randomizes playback order (on/off)
- Repeat mode — cycles through: off, repeat all (loop playlist), repeat one (loop current song)
- Volume — slider from 0 to 100, mute button sets to 0
- Progress/Seek — slider from 0 to track duration, clickable to jump
- No actual audio playback — all state-only (isPlaying, currentTrackId, progress, volume, shuffle, repeatMode)

### Notifications & Settings
- Playback settings:
  - Crossfade toggle (on/off)
  - Autoplay toggle (play similar songs when queue ends)
  - Audio quality dropdown (Low, Normal, High, Very High)
  - Normalize volume toggle
- Social settings:
  - Private session toggle (hide listening activity)
  - Show recently played artists on profile toggle
  - Share listening activity with followers toggle
- Display settings:
  - Language dropdown (English, Spanish, French, German, Japanese, Portuguese, Korean)
  - Compact library layout toggle
  - Show desktop notifications toggle
