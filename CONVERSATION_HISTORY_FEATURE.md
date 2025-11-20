# 💬 Conversation History Feature - Implemented!

## ✅ Feature Overview

Your HR AI chatbot now has **persistent conversation history**! Chat sessions are saved to the database and automatically restored when you return.

---

## 🎯 What's New

### Database Models
- **Conversation**: Stores chat sessions with unique session IDs
- **ChatMessage**: Stores individual messages (user/assistant) with metadata

### Backend Features
- ✅ Automatic conversation creation and tracking
- ✅ Persistent message storage in MySQL database
- ✅ Conversation ID returned with each response
- ✅ REST API endpoints for conversation management

### Frontend Features
- ✅ Conversation ID stored in localStorage
- ✅ Chat history automatically loaded on page refresh
- ✅ "New Chat" button to start fresh conversations
- ✅ Session continuity across page reloads

---

## 📊 Database Schema

### Conversations Table
```sql
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE,
    title VARCHAR(200),
    created_at DATETIME,
    updated_at DATETIME
);
```

### Chat Messages Table
```sql
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT,
    role VARCHAR(20),
    content TEXT,
    triggered_analysis BOOLEAN,
    analysis_run_id INT,
    created_at DATETIME,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

---

## 🔌 API Endpoints

### Send Chat Message
```http
POST /api/chatbot/
Content-Type: application/json

{
  "message": "What roles are we missing?",
  "conversation_id": "uuid-here" // optional
}

Response:
{
  "response": "...",
  "conversation_id": "uuid-here",
  "triggered_analysis": false,
  "recommendations_count": 0,
  "analysis_id": null
}
```

### List All Conversations
```http
GET /api/conversations/

Response:
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "session_id": "uuid",
      "title": "What roles are we missing?",
      "message_count": 10,
      "last_message": {...},
      "created_at": "2025-11-18T...",
      "updated_at": "2025-11-18T..."
    }
  ]
}
```

### Get Specific Conversation
```http
GET /api/conversations/{id}/

Response:
{
  "id": 1,
  "session_id": "uuid",
  "title": "What roles are we missing?",
  "message_count": 10,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "What roles are we missing?",
      "triggered_analysis": false,
      "created_at": "2025-11-18T..."
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Let me analyze...",
      "triggered_analysis": true,
      "created_at": "2025-11-18T..."
    }
  ]
}
```

### Get Conversation Messages
```http
GET /api/conversations/{id}/messages/

Response: Array of chat messages
```

### Clear All Conversations
```http
DELETE /api/conversations/clear_all/

Response:
{
  "message": "Deleted 5 conversations",
  "count": 5
}
```

---

## 💻 How It Works

### Backend Flow

1. **User sends message** → `POST /api/chatbot/`
2. **Backend checks** for existing `conversation_id`
3. **If no ID** → Creates new Conversation with UUID
4. **If ID exists** → Retrieves existing Conversation
5. **Stores user message** → ChatMessage with role='user'
6. **Processes request** → LLM generates response
7. **Stores assistant message** → ChatMessage with role='assistant'
8. **Returns response** → Includes conversation_id for frontend

### Frontend Flow

1. **Component mounts** → Checks localStorage for conversation_id
2. **If ID found** → Fetches conversation history from API
3. **Loads messages** → Displays full chat history
4. **User sends message** → Includes conversation_id in request
5. **Receives response** → Updates conversation_id if new
6. **Stores ID** → Saves to localStorage for persistence

### "New Chat" Button

1. User clicks "New Chat"
2. Clears localStorage conversation_id
3. Resets messages to welcome screen
4. Next message creates new conversation

---

## 🎨 UI Features

### Chat Header
- Title: "HR AI Assistant"
- Description of capabilities
- **"+ New Chat"** button (green, top-right)

### Chat History
- Messages persist across page refreshes
- Scrolls to latest message automatically
- Shows user/assistant messages with distinct styling

### Session Management
- Automatic session restoration
- Clean "New Chat" experience
- Error handling for invalid/deleted conversations

---

## 🧪 Testing

### Test Conversation Persistence

1. **Start a conversation**:
```bash
curl -X POST http://localhost:8000/api/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

2. **Note the conversation_id** in response

3. **Continue the conversation**:
```bash
curl -X POST http://localhost:8000/api/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What can you do?", "conversation_id": "UUID-HERE"}'
```

4. **View conversation history**:
```bash
curl http://localhost:8000/api/conversations/1/
```

### Test Frontend

1. **Open chatbot**: http://13.62.19.27:5173/chatbot
2. **Send a message**: Type "What roles are missing?"
3. **Refresh page**: History should be restored
4. **Click "New Chat"**: Should clear history and start fresh
5. **Send another message**: Should create new conversation

---

## 📝 Database Queries

### View All Conversations
```sql
USE hr_database;
SELECT * FROM conversations ORDER BY updated_at DESC;
```

### View Chat Messages
```sql
SELECT 
    cm.id, 
    c.session_id, 
    cm.role, 
    LEFT(cm.content, 100) as content,
    cm.created_at
FROM chat_messages cm
JOIN conversations c ON cm.conversation_id = c.id
ORDER BY cm.created_at DESC
LIMIT 20;
```

### Count Messages Per Conversation
```sql
SELECT 
    c.id,
    c.session_id,
    c.title,
    COUNT(cm.id) as message_count
FROM conversations c
LEFT JOIN chat_messages cm ON c.id = cm.conversation_id
GROUP BY c.id
ORDER BY c.updated_at DESC;
```

### Delete Old Conversations
```sql
-- Delete conversations older than 30 days
DELETE FROM conversations 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

---

## 🔧 Configuration

### Backend Settings

In `roles_analyzer/chatbot.py`:
- Conversations are created with UUID session_ids
- Title auto-generated from first user message
- Messages linked to analysis_runs when analysis is triggered

### Frontend Settings

In `frontend/src/components/Chatbot.jsx`:
- localStorage key: `current_conversation_id`
- Auto-loads history on component mount
- Preserves conversation across page refreshes

---

## 🚀 Future Enhancements

### Potential Features
- [ ] Conversation list sidebar (show all past chats)
- [ ] Delete individual conversations
- [ ] Search through conversation history
- [ ] Export conversations as PDF/JSON
- [ ] Conversation folders/categories
- [ ] Share conversation via link
- [ ] Conversation analytics (most asked questions)

### Backend Improvements
- [ ] Add user authentication and ownership
- [ ] Implement conversation archiving
- [ ] Add full-text search on messages
- [ ] Rate limiting per conversation
- [ ] Message edit/delete functionality

---

## 📊 Current Status

### Database
- ✅ Tables created and migrated
- ✅ Conversations storing correctly
- ✅ Messages linking to conversations
- ✅ Indexes for performance

### Backend
- ✅ Conversation creation working
- ✅ Message persistence working
- ✅ API endpoints functional
- ✅ Error handling in place

### Frontend
- ✅ Conversation ID management
- ✅ History loading on mount
- ✅ localStorage integration
- ✅ "New Chat" functionality

---

## 🎉 Example Usage

### Browser Test

1. Open: **http://13.62.19.27:5173/chatbot**

2. **Send first message**:
   - Type: "What roles are we missing in Engineering?"
   - Press Send

3. **Continue conversation**:
   - Type: "Run an analysis"
   - Wait for response

4. **Refresh page** (F5 or Ctrl+R)
   - All messages should reappear!

5. **Click "New Chat"**
   - Should start fresh conversation

---

## 💡 Tips

- **Conversation persists**: Even after closing browser
- **Unique per browser**: Each browser/device has separate chat
- **Clear history**: Click "New Chat" button
- **View all chats**: Visit `/api/conversations/` endpoint

---

## 🛠️ Troubleshooting

### History not loading?

Check browser console for errors:
```javascript
// Open browser dev tools (F12)
// Check Console tab for errors
```

### Conversation not saving?

Check backend logs:
```bash
tail -f /tmp/django.log
```

### Database issues?

Verify tables exist:
```bash
docker exec missing_roles_db mysql -uroot \
  -e "USE hr_database; SHOW TABLES LIKE '%conversation%'; SHOW TABLES LIKE '%chat%';"
```

---

## 📚 Migration Details

### Migration File
`roles_analyzer/migrations/0002_conversation_chatmessage.py`

### Applied
```bash
python manage.py migrate roles_analyzer
```

Output:
```
Operations to perform:
  Apply all migrations: roles_analyzer
Running migrations:
  Applying roles_analyzer.0002_conversation_chatmessage... OK
```

---

**Implemented**: November 18, 2025  
**Status**: ✅ Fully Functional  
**Version**: 1.0

