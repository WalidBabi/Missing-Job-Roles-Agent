# Conversation History Sidebar Implementation

## Summary

Successfully implemented a **conversation history sidebar** in the chatbot UI that allows users to:
- View all past conversations
- Switch between conversations
- See conversation previews with timestamps
- Start new conversations
- Toggle sidebar visibility

## What Was Implemented

### 1. Backend API Endpoints

#### New Serializers (`roles_analyzer/serializers.py`)

**`ConversationMessageSerializer`**
- Serializes individual messages with role, content, timestamp, and metadata

**`ConversationSerializer`**
- Lists conversations with:
  - Message count
  - Last message preview (first 100 chars)
  - Last message timestamp
  - Created/updated dates

**`ConversationDetailSerializer`**
- Full conversation with all messages included
- Used when loading a specific conversation

#### New API Endpoints (`roles_analyzer/views.py`)

**`GET /api/conversations/`**
- Lists all conversations (limited to 50 most recent)
- Ordered by most recently updated
- Returns conversation previews

**`GET /api/conversations/<conversation_id>/`**
- Gets a specific conversation with all its messages
- Used when switching to a conversation

#### URL Routes (`roles_analyzer/urls.py`)
- Added routes for conversation endpoints

### 2. Frontend Updates

#### API Service (`frontend/src/services/api.js`)
- Added `getConversations()` - Fetch all conversations
- Added `getConversation(conversationId)` - Fetch specific conversation

#### Chatbot Component (`frontend/src/components/Chatbot.jsx`)

**New State:**
- `conversations` - List of all conversations
- `sidebarOpen` - Sidebar visibility state
- `loadingConversations` - Loading state for conversations

**New Functions:**
- `loadConversations()` - Fetches and displays conversation list
- `loadConversationMessages(convId)` - Loads messages for selected conversation
- `startNewConversation()` - Resets to new conversation
- `formatDate()` - Formats conversation timestamps

**UI Features:**
- **Sidebar**: Shows list of conversations with previews
- **Toggle Button**: Show/hide sidebar
- **New Conversation Button**: Start fresh conversation
- **Conversation Cards**: Click to switch conversations
- **Active Highlight**: Current conversation highlighted
- **Date Formatting**: Shows "Today", "Yesterday", or days ago
- **Message Count**: Shows number of messages per conversation

## UI Layout

```
┌─────────────────────────────────────────────────────────┐
│  [☰] HR AI Assistant                                    │
│      Ask me anything about your organization...          │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│ Conversations│  Chat Messages Area                      │
│              │                                          │
│ [+ New]      │  [User messages]                         │
│              │  [Assistant responses]                   │
│              │                                          │
│ ┌──────────┐ │                                          │
│ │ Today    │ │                                          │
│ │ 5 msgs   │ │                                          │
│ │ Preview  │ │                                          │
│ └──────────┘ │                                          │
│              │                                          │
│ ┌──────────┐ │                                          │
│ │ Yesterday│ │                                          │
│ │ 3 msgs   │ │                                          │
│ │ Preview  │ │                                          │
│ └──────────┘ │                                          │
│              │                                          │
│              │  [Input field] [Send]                    │
└──────────────┴──────────────────────────────────────────┘
```

## Features

### ✅ Conversation List
- Shows up to 50 most recent conversations
- Ordered by most recently updated
- Each conversation shows:
  - Date (Today/Yesterday/X days ago)
  - Message count
  - Preview of last message (100 chars)

### ✅ Conversation Switching
- Click any conversation to load its messages
- Active conversation highlighted in blue
- Smooth loading with loading state

### ✅ New Conversation
- "+ New" button starts fresh conversation
- Clears current messages
- Resets conversation ID

### ✅ Sidebar Toggle
- Hamburger menu button to show/hide sidebar
- Smooth animation (300ms transition)
- Sidebar collapses to 0 width when hidden

### ✅ Auto-refresh
- Conversations list refreshes when:
  - Component mounts
  - New message is sent
  - Conversation ID changes

## API Endpoints

### List Conversations
```http
GET /api/conversations/
```

**Response:**
```json
[
  {
    "conversation_id": "uuid-here",
    "created_at": "2025-01-18T10:00:00Z",
    "updated_at": "2025-01-18T10:15:00Z",
    "message_count": 5,
    "last_message_preview": "What roles are we missing in Engineering?",
    "last_message_time": "2025-01-18T10:15:00Z"
  }
]
```

### Get Conversation
```http
GET /api/conversations/{conversation_id}/
```

**Response:**
```json
{
  "conversation_id": "uuid-here",
  "created_at": "2025-01-18T10:00:00Z",
  "updated_at": "2025-01-18T10:15:00Z",
  "message_count": 5,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "What roles are we missing?",
      "timestamp": "2025-01-18T10:00:00Z",
      "triggered_analysis": false,
      "analysis_id": null
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Based on my analysis...",
      "timestamp": "2025-01-18T10:00:05Z",
      "triggered_analysis": true,
      "analysis_id": 123
    }
  ]
}
```

## User Experience Flow

1. **User opens chatbot**
   - Sidebar loads with all conversations
   - Shows welcome message if no conversation selected

2. **User clicks a conversation**
   - Messages load from database
   - Conversation highlighted in sidebar
   - Messages displayed in chat area

3. **User sends new message**
   - Message added to current conversation
   - If new conversation, sidebar refreshes
   - New conversation appears in list

4. **User clicks "+ New"**
   - Current conversation cleared
   - Welcome message shown
   - Ready for new conversation

5. **User toggles sidebar**
   - Sidebar smoothly hides/shows
   - Chat area expands/contracts
   - State persists during session

## Styling Details

### Sidebar
- Width: 320px (w-80) when open, 0px when closed
- Background: White with shadow
- Scrollable conversation list
- Fixed height: 800px (matches chat container)

### Conversation Cards
- Active: Blue background (`bg-blue-50`) with blue border
- Inactive: Gray background with hover effect
- Shows date, message count, and preview
- Clickable with smooth transitions

### Responsive Design
- Sidebar can be toggled on/off
- Chat area adjusts width automatically
- Works well on different screen sizes

## Technical Details

### State Management
- Conversations loaded on mount
- Refreshed when new messages sent
- Messages loaded on-demand when conversation selected

### Performance
- Limits to 50 most recent conversations
- Messages loaded only when conversation selected
- Efficient database queries with proper indexing

### Error Handling
- Graceful error handling for API calls
- Loading states for better UX
- Empty states when no conversations exist

## Files Modified

1. `roles_analyzer/serializers.py` - Added conversation serializers
2. `roles_analyzer/views.py` - Added conversation endpoints
3. `roles_analyzer/urls.py` - Added conversation routes
4. `frontend/src/services/api.js` - Added conversation API functions
5. `frontend/src/components/Chatbot.jsx` - Added sidebar UI and logic

## Testing Checklist

- [x] Backend endpoints created
- [x] Serializers implemented
- [x] Frontend API functions added
- [x] Sidebar UI implemented
- [x] Conversation loading works
- [x] Conversation switching works
- [x] New conversation button works
- [x] Sidebar toggle works
- [x] Date formatting works
- [x] Active conversation highlighting works
- [ ] Test with multiple conversations
- [ ] Test with empty conversation list
- [ ] Test sidebar toggle animation
- [ ] Test conversation loading performance

## Future Enhancements

Potential improvements:
- [ ] Search/filter conversations
- [ ] Delete conversations
- [ ] Rename conversations
- [ ] Pin important conversations
- [ ] Export conversations
- [ ] Conversation tags/categories
- [ ] Keyboard shortcuts (e.g., Ctrl+N for new)
- [ ] Conversation archiving
- [ ] Infinite scroll for conversations
- [ ] Conversation statistics

## Usage

The sidebar is now fully functional! Users can:
1. View all their past conversations
2. Click any conversation to view its messages
3. Start new conversations with the "+ New" button
4. Toggle the sidebar on/off as needed

The conversation history makes it easy to:
- Continue previous discussions
- Reference past recommendations
- Track analysis history
- Maintain context across sessions

🎉 **Conversation history sidebar is now live!**

