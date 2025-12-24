# Matching System - Complete Guide

This guide covers the complete matching system design, database schema, visual diagrams, and API implementation.

---

## Table of Contents

1. [Database Design Overview](#database-design-overview)
2. [Visual Diagrams](#visual-diagrams)
3. [Database Schema Details](#database-schema-details)
4. [API Endpoints (Phase 1)](#api-endpoints-phase-1)
5. [Implementation Details](#implementation-details)
6. [Testing Guide](#testing-guide)

---

## Database Design Overview

### The Problem We're Solving

Your app matches **groups** of people, not individuals. The flow is:
1. Brad (from Group A) likes Group B (Becca & Chelsea)
2. Becca approves ✓
3. Chelsea approves ✓
4. David (Brad's group mate) approves ✓
5. Match is made! 🎉

### Core Principles

1. **Normalization**: Store data once, reference it
2. **Denormalization**: Store pre-calculated values for performance
3. **Constraints**: Use database constraints to enforce rules
4. **Indexes**: Optimize common queries
5. **Soft Deletes**: Preserve history with `is_active` flags

### Tables Overview

#### 1. **Groups Table**
- Represents a collection of users who want to match together
- Example: "Brad & David's Crew" is a group with 2 members
- **What it stores:** Information about each group
- **Why separate table?**
  - Groups are real entities (not just "a list of users")
  - Groups can have metadata (name, description, photos)
  - Groups can exist independently of users
  - Makes it easy to query "all groups" or "groups a user is in"

**Key columns:**
- `id`: Unique identifier
- `name`: Optional group name
- `created_by_id`: Who created it (for permissions later)
- `is_active`: Is this group still active?

**Example data:**
```
id | name              | created_by_id | is_active
1  | "Weekend Crew"    | uuid1         | true
2  | "Becca & Chelsea" | uuid2         | true
```

#### 2. **Group Members Table (Junction Table)**
- Links users to groups (many-to-many relationship)
- **What it stores:** The connection between users and groups
- **Why junction table?**
  - One user can be in multiple groups (Brad is in Group A and Group C)
  - One group has multiple users (Group A has Brad and David)
  - This is called a **many-to-many relationship**
  - Junction tables are the standard way to handle this

**Key columns:**
- `group_id`: Which group
- `user_id`: Which user
- `is_active`: Did they leave the group? (soft delete)
- `role`: Could be 'creator', 'admin', 'member' (for future features)

**UNIQUE constraint:** `(group_id, user_id)` - Can't add the same user to the same group twice

**Example data:**
```
id | group_id | user_id | role   | is_active
1  | 1        | uuid1   | member | true    (Brad in Group 1)
2  | 1        | uuid2   | member | true    (David in Group 1)
3  | 2        | uuid3   | member | true    (Becca in Group 2)
4  | 2        | uuid4   | member | true    (Chelsea in Group 2)
```

**Why not just add `group_id` to users table?**
- Because users can be in MULTIPLE groups!
- If we put `group_id` in users table, each user could only be in one group
- Junction table allows many-to-many

**Key Constraints:**
- `UNIQUE(group_id, user_id)` - Prevents adding same user to group twice
- Indexes on `user_id` and `group_id` for fast lookups

#### 3. **Likes Table**
- Tracks when one group likes another group
- **The Heart of Matching**: Contains approval tracking logic
- **What it stores:** Group-to-group likes and approval tracking

**Key columns:**
- `liker_group_id`: The group doing the liking
- `likee_group_id`: The group being liked
- `initiator_user_id`: Who started the like (Brad)
- `status`: Where we are in the approval process

**DENORMALIZED columns (the smart part):**
- `group_b_approvals_count`: How many people in Group B said yes (currently 2)
- `group_b_required_count`: How many people in Group B need to approve (2)
- `group_a_approvals_count`: How many people in Group A said yes (currently 1)
- `group_a_required_count`: How many people in Group A need to approve (2)

**Why Denormalize?**
Instead of counting every time (slow), we store the counts:
- **Normalized way:** Count approvals from `like_approvals` table every time → 3 queries
- **Denormalized way:** Read the stored count → 1 query, instant!

**Example data:**
```
id | liker | likee | initiator | group_b_approved | group_b_needed | group_a_approved | group_a_needed | status
1  | 1     | 2     | uuid1     | 2                | 2              | 1                | 2              | pending_group_a
```

This tells us:
- Group 1 likes Group 2
- User uuid1 initiated it
- Both people in Group 2 approved ✓
- 1 of 2 people in Group 1 approved (waiting for David)
- Status: waiting for Group A to finish approving

**UNIQUE constraint:** `(liker_group_id, likee_group_id)` - Can't like the same group twice

**Key Features:**
- **Denormalized Approval Counts**: `group_b_approvals_count` and `group_a_approvals_count` are stored (not calculated)
- **Status Tracking**: `pending_group_b` → `pending_group_a` → `matched` or `rejected`
- **Required Counts**: Calculated when like is created based on group sizes

**Why Denormalize?**
- **Performance**: No need to COUNT() every time we check approvals
- **Simplicity**: Fast reads, simple updates
- **Trade-off**: Must update counts when approvals happen (but this is rare compared to reads)

#### 4. **Matches Table**
- Finalized matches between groups
- **What it stores:** Successful matches between groups
- **Why separate from likes?**
  - Clean separation: likes are "pending", matches are "finalized"
  - Easier to query "all my matches"
  - Can add match-specific features later (group chat, events, etc.)

**Key columns:**
- `group1_id`: First group (always smaller ID)
- `group2_id`: Second group (always larger ID)
- `matched_at`: When the match was finalized
- `last_message_at`: For sorting by recent activity
- `is_active`: For "unmatching" (soft delete)

**CHECK constraint:** `group1_id < group2_id`
- This ensures we always store (1, 2) never (2, 1)
- Prevents duplicate matches
- Makes queries simpler (always know group1 < group2)

**Example data:**
```
id | group1_id | group2_id | matched_at           | is_active
1  | 1         | 2         | 2024-01-15 10:30:00  | true
```

**Key Constraints:**
- `CHECK(group1_id < group2_id)` - Ensures consistent ordering (prevents duplicates)
- `UNIQUE(group1_id, group2_id)` - Prevents duplicate matches

---

## Visual Diagrams

### Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ GroupMember : "belongs to"
    User ||--o{ Group : "creates"
    Group ||--o{ GroupMember : "has"
    Group ||--o{ Like : "liker"
    Group ||--o{ Like : "likee"
    Group ||--o{ Match : "group1"
    Group ||--o{ Match : "group2"
    User ||--o{ Like : "initiates"
    Like ||--|| Match : "creates"

    User {
        uuid id PK
        string name
        string email UK
        string phone_number UK
        array interests
        string location
        array pictures
        json prompts
    }

    Group {
        int id PK
        string name
        string description
        uuid created_by_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    GroupMember {
        int id PK
        int group_id FK
        uuid user_id FK
        string role
        boolean is_active
        datetime joined_at
    }

    Like {
        int id PK
        int liker_group_id FK
        int likee_group_id FK
        uuid initiator_user_id FK
        int group_b_approvals_count "DENORMALIZED"
        int group_b_required_count
        int group_a_approvals_count "DENORMALIZED"
        int group_a_required_count
        string status "pending_group_b, pending_group_a, matched, rejected"
        datetime matched_at
        datetime created_at
        datetime updated_at
    }

    Match {
        int id PK
        int group1_id FK "CHECK: group1_id < group2_id"
        int group2_id FK
        datetime matched_at
        datetime last_message_at
        boolean is_active
        datetime created_at
        datetime updated_at
    }
```

### Approval Flow Diagram

```mermaid
flowchart TD
    Start([Brad likes Group B]) --> CreateLike[Create Like Record<br/>status: pending_group_b<br/>group_b_required: 2<br/>group_a_required: 2]
    
    CreateLike --> WaitB[Waiting for Group B<br/>approvals]
    
    WaitB --> BeccaApproves[Becca Approves<br/>group_b_approvals: 1]
    BeccaApproves --> CheckB{All Group B<br/>approved?}
    
    CheckB -->|No| WaitB
    CheckB -->|Yes| UpdateStatus[Update Status<br/>status: pending_group_a]
    
    UpdateStatus --> WaitA[Waiting for Group A<br/>approvals]
    
    WaitA --> DavidApproves[David Approves<br/>group_a_approvals: 2]
    DavidApproves --> CheckA{All Group A<br/>approved?}
    
    CheckA -->|No| WaitA
    CheckA -->|Yes| CreateMatch[Create Match Record<br/>status: matched]
    
    CreateMatch --> End([Match Created!])
    
    style CreateLike fill:#e1f5ff
    style CreateMatch fill:#d4edda
    style End fill:#d4edda
    style CheckB fill:#fff3cd
    style CheckA fill:#fff3cd
```

### Table Relationships - Detailed View

```mermaid
graph TB
    subgraph "User Domain"
        U[User<br/>id, name, email]
    end
    
    subgraph "Group Domain"
        G[Group<br/>id, name, created_by_id]
        GM[GroupMember<br/>group_id, user_id<br/>UNIQUE: group_id, user_id]
    end
    
    subgraph "Matching Domain"
        L[Like<br/>liker_group_id, likee_group_id<br/>DENORMALIZED: approval counts<br/>UNIQUE: liker, likee]
        M[Match<br/>group1_id, group2_id<br/>CHECK: group1 < group2<br/>UNIQUE: group1, group2]
    end
    
    U -->|creates| G
    U -->|member of| GM
    G -->|has| GM
    G -->|likes| L
    G -->|liked by| L
    U -->|initiates| L
    L -->|creates| M
    G -->|group1| M
    G -->|group2| M
    
    style U fill:#e3f2fd
    style G fill:#f3e5f5
    style GM fill:#f3e5f5
    style L fill:#fff3e0
    style M fill:#e8f5e9
```

### Approval State Machine

```mermaid
stateDiagram-v2
    [*] --> pending_group_b: Like Created
    pending_group_b --> pending_group_b: Group B member approves<br/>(count < required)
    pending_group_b --> pending_group_a: All Group B approved<br/>(count >= required)
    pending_group_a --> pending_group_a: Group A member approves<br/>(count < required)
    pending_group_a --> matched: All Group A approved<br/>(count >= required)
    pending_group_b --> rejected: Someone rejects
    pending_group_a --> rejected: Someone rejects
    matched --> [*]: Match created
    rejected --> [*]: Process ends
```

### Data Flow - Approval Tracking

```mermaid
sequenceDiagram
    participant Brad as Brad (User)
    participant GroupA as Group A
    participant Like as Like Record
    participant GroupB as Group B
    participant Becca as Becca
    participant Chelsea as Chelsea
    participant David as David
    participant Match as Match Record

    Brad->>Like: Create like<br/>liker: Group A<br/>likee: Group B<br/>status: pending_group_b<br/>group_b_required: 2
    
    Becca->>Like: Approve<br/>group_b_approvals: 1
    Chelsea->>Like: Approve<br/>group_b_approvals: 2
    
    Like->>Like: Check: 2 >= 2?<br/>Update status: pending_group_a
    
    David->>Like: Approve<br/>group_a_approvals: 2
    
    Like->>Like: Check: 2 >= 2?<br/>Update status: matched
    
    Like->>Match: Create match<br/>group1: A, group2: B
```

### Database Schema Overview

```mermaid
graph LR
    subgraph "Core Tables"
        U[User]
        G[Group]
    end
    
    subgraph "Relationships"
        GM[GroupMember<br/>Junction Table]
    end
    
    subgraph "Matching"
        L[Like<br/>Approval Tracking]
        M[Match<br/>Final Matches]
    end
    
    U --> GM
    G --> GM
    G --> L
    L --> M
    G --> M
    
    style U fill:#bbdefb
    style G fill:#ce93d8
    style GM fill:#ffcc80
    style L fill:#c5e1a5
    style M fill:#81c784
```

---

## How the Flow Works in the Database

### Step 1: Brad likes Group B
```sql
INSERT INTO likes (
    liker_group_id, 
    likee_group_id, 
    initiator_user_id,
    group_b_required_count,  -- Count members in Group B (2)
    group_a_required_count,   -- Count members in Group A (2)
    status
) VALUES (1, 2, 'uuid1', 2, 2, 'pending_group_b');
```

### Step 2: Becca approves
```sql
UPDATE likes 
SET group_b_approvals_count = 1,
    updated_at = NOW()
WHERE id = 1;
```

### Step 3: Chelsea approves
```sql
UPDATE likes 
SET group_b_approvals_count = 2,
    status = 'pending_group_a',  -- Move to next phase
    updated_at = NOW()
WHERE id = 1;
```

### Step 4: David approves
```sql
UPDATE likes 
SET group_a_approvals_count = 2,
    status = 'matched',
    matched_at = NOW(),
    updated_at = NOW()
WHERE id = 1;

-- Then create the match
INSERT INTO matches (group1_id, group2_id, matched_at)
VALUES (1, 2, NOW());
```

---

## Database Schema Details

### Normalization vs Denormalization

#### Normalized (Stored Once)
- **User data**: Name, email, etc. stored in `users` table
- **Group data**: Name, description stored in `groups` table
- **Relationships**: User-Group relationships in `group_members` table

#### Denormalized (Pre-calculated)
- **Approval counts**: `group_b_approvals_count` and `group_a_approvals_count` in `likes` table
  - **Why?** Performance - no need to COUNT() every time
  - **Trade-off**: Must update when approvals happen (but reads >> writes)

### Key Constraints

1. **UNIQUE Constraints**:
   - `group_members(group_id, user_id)` - Can't add same user to group twice
   - `likes(liker_group_id, likee_group_id)` - Can't like same group twice
   - `matches(group1_id, group2_id)` - Can't match same groups twice

2. **CHECK Constraints**:
   - `matches.group1_id < group2_id` - Ensures consistent ordering

3. **Foreign Keys**:
   - All foreign keys have `ondelete` actions (CASCADE or SET NULL)
   - Ensures data integrity

### Indexes

- **Primary keys**: All tables have indexed primary keys
- **Foreign keys**: All foreign keys are indexed
- **Composite indexes**: 
  - `likes(liker_group_id, status)` - Fast "who did this group like?"
  - `likes(likee_group_id, status)` - Fast "who liked this group?"
  - `matches(group1_id, matched_at)` - Fast "all matches for group 1"
  - `matches(group2_id, matched_at)` - Fast "all matches for group 2"

### Common Queries Explained

#### "Get all groups a user is in"
```sql
SELECT g.* 
FROM groups g
JOIN group_members gm ON g.id = gm.group_id
WHERE gm.user_id = ? AND gm.is_active = true;
```
**Why it works:** Join through the junction table

#### "Get all pending likes for a group"
```sql
SELECT * FROM likes
WHERE likee_group_id = ? AND status = 'pending_group_b';
```
**Why it's fast:** Index on `(likee_group_id, status)`

#### "Check if everyone approved"
```sql
SELECT * FROM likes
WHERE id = ?
  AND group_b_approvals_count >= group_b_required_count
  AND group_a_approvals_count >= group_a_required_count;
```
**Why it's fast:** No counting needed, just compare stored numbers!

#### "Get all matches for a group"
```sql
SELECT * FROM matches
WHERE (group1_id = ? OR group2_id = ?) AND is_active = true
ORDER BY matched_at DESC;
```
**Why it works:** Check both columns since we don't know which position the group is in

---

## API Endpoints (Phase 1)

### ✅ Completed Endpoints

#### 1. **POST /groups** - Create Group
Creates a new group with optional name/description. Automatically adds creator as a member and adds all specified member_ids to the group.

**Requires authentication**

**Request:**
```json
{
  "name": "Brad & David's Crew",
  "description": "Weekend warriors",
  "member_ids": ["uuid1", "uuid2"]
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Brad & David's Crew",
  "description": "Weekend warriors",
  "created_by_id": "uuid1",
  "is_active": true,
  "members": [
    {
      "id": 1,
      "user_id": "uuid1",
      "user_name": "Brad",
      "role": "member",
      "joined_at": "2024-01-15T10:00:00Z"
    }
  ],
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

---

#### 2. **POST /groups/{group_id}/members** - Add Member
Adds a user to an existing group. Current user must be a member of the group.

**Requires authentication**

**Request:**
```json
{
  "user_id": "uuid3",
  "role": "member"
}
```

**Response:**
```json
{
  "id": 2,
  "user_id": "uuid3",
  "user_name": "David",
  "role": "member",
  "joined_at": "2024-01-15T10:05:00Z"
}
```

---

#### 3. **POST /matching/likes** - Create Like
One group likes another group. Automatically calculates required approval counts and sets status to "pending_group_b".

**Requires authentication**  
**User must be a member of the liker group**

**Request:**
```json
{
  "liker_group_id": 1,
  "likee_group_id": 2
}
```

**Response:**
```json
{
  "id": 1,
  "liker_group_id": 1,
  "likee_group_id": 2,
  "initiator_user_id": "uuid1",
  "group_b_approvals_count": 0,
  "group_b_required_count": 2,
  "group_a_approvals_count": 0,
  "group_a_required_count": 2,
  "status": "pending_group_b",
  "matched_at": null,
  "created_at": "2024-01-15T10:10:00Z",
  "updated_at": "2024-01-15T10:10:00Z"
}
```

---

#### 4. **POST /matching/likes/{like_id}/approve** - Approve Like
User approves a like. Automatically increments approval count, checks if all approvals complete, and creates match if everyone approved.

**Requires authentication**  
**User must be a member of one of the groups**

**Request:**
```
POST /matching/likes/1/approve
(no body needed - user_id from token)
```

**Response (if match created):**
```json
{
  "like": {
    "id": 1,
    "status": "matched",
    "group_b_approvals_count": 2,
    "group_a_approvals_count": 2,
    ...
  },
  "match": {
    "id": 1,
    "group1_id": 1,
    "group2_id": 2,
    "matched_at": "2024-01-15T10:15:00Z",
    "is_active": true,
    ...
  },
  "message": "Match created!"
}
```

**Response (if still pending):**
```json
{
  "like": {
    "id": 1,
    "status": "pending_group_a",
    "group_b_approvals_count": 2,
    "group_a_approvals_count": 1,
    ...
  },
  "match": null,
  "message": "Like approved"
}
```

---

#### 5. **GET /matching/groups/{group_id}/matches** - Get Matches
Returns all active matches for a group.

**Requires authentication**

**Response:**
```json
{
  "matches": [
    {
      "id": 1,
      "group1_id": 1,
      "group2_id": 2,
      "matched_at": "2024-01-15T10:15:00Z",
      "last_message_at": null,
      "is_active": true,
      "created_at": "2024-01-15T10:15:00Z",
      "updated_at": "2024-01-15T10:15:00Z"
    }
  ]
}
```

---

## Implementation Details

### Files Created

1. **`app/core/dependencies.py`** - Authentication dependency (`get_current_user`)
2. **`app/schemas/matching.py`** - Request/response schemas
3. **`app/services/matching.py`** - Business logic service layer
4. **`app/api/routes/groups.py`** - Group management routes
5. **`app/api/routes/matching.py`** - Likes and matches routes

### Files Modified

1. **`app/main.py`** - Registered new routes and added CORS middleware
2. **`app/models/matching.py`** - Database models for groups, likes, matches
3. **`app/models/user.py`** - Updated to use UUID for user IDs

### How It Works

#### Approval Flow Example:

1. **Brad creates like:**
   ```
   POST /matching/likes
   { "liker_group_id": 1, "likee_group_id": 2 }
   → Creates like with status "pending_group_b"
   → Sets required counts: group_b=2, group_a=2
   ```

2. **Becca approves:**
   ```
   POST /matching/likes/1/approve
   → Increments group_b_approvals_count: 0 → 1
   → Status still "pending_group_b"
   ```

3. **Chelsea approves:**
   ```
   POST /matching/likes/1/approve
   → Increments group_b_approvals_count: 1 → 2
   → Checks: 2 >= 2? Yes!
   → Updates status to "pending_group_a"
   ```

4. **David approves:**
   ```
   POST /matching/likes/1/approve
   → Increments group_a_approvals_count: 1 → 2
   → Checks: 2 >= 2? Yes!
   → Checks group_b: 2 >= 2? Yes!
   → Creates match!
   → Updates status to "matched"
   ```

### Key Implementation Notes

- **All endpoints require authentication** (Bearer token)
- **Approval counts are denormalized** (stored, not calculated)
- **Matches are created automatically** when all approvals complete
- **Group membership is validated** before allowing operations
- **UUIDs are used for user IDs** to match database schema

---

## Testing Guide

### Using Swagger UI:

1. Start server: `poetry run uvicorn app.main:app --reload`
2. Go to: http://localhost:8080/docs
3. Authorize with a token from `/auth/login`
4. Test endpoints in order:
   - Create group
   - Add members
   - Create like
   - Approve likes
   - Get matches

### Quick Start with curl

#### Step 1: Sign Up and Get Token

```bash
# Sign up a new user
curl -X POST "http://localhost:8080/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "brad@example.com",
    "password": "password123",
    "name": "Brad"
  }'

# Response will include tokens.access_token - save this!
# Example response:
# {
#   "tokens": {
#     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#     "refresh_token": "..."
#   },
#   "user": { ... }
# }
```

**One-liner to sign up and create a group:**
```bash
TOKEN=$(curl -s -X POST "http://localhost:8080/auth/signup" -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"password123","name":"Test User"}' | jq -r '.tokens.access_token') && curl -X POST "http://localhost:8080/groups" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"name":"My Group","member_ids":[]}'
```

#### Step 2: Create Groups

```bash
# Create Group A (Brad's group)
curl -X POST "http://localhost:8080/groups" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Brad & David Crew",
    "description": "Weekend warriors",
    "member_ids": []
  }'

# Response:
# {
#   "id": 1,
#   "name": "Brad & David Crew",
#   "members": [
#     {
#       "id": 1,
#       "user_id": "uuid-of-brad",
#       "user_name": "Brad",
#       "role": "member",
#       "joined_at": "2024-01-15T10:00:00Z"
#     }
#   ],
#   ...
# }
```

**Note:** The creator is automatically added as a member. The `member_ids` array can be empty or contain additional user IDs.

#### Step 3: Add Members to Group

```bash
# Add David to Group A
curl -X POST "http://localhost:8080/groups/1/members" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "user_id": "uuid-of-david",
    "role": "member"
  }'
```

#### Step 4: Create a Like

```bash
# Group A likes Group B
curl -X POST "http://localhost:8080/matching/likes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "liker_group_id": 1,
    "likee_group_id": 2
  }'

# Response:
# {
#   "id": 1,
#   "liker_group_id": 1,
#   "likee_group_id": 2,
#   "status": "pending_group_b",
#   "group_b_approvals_count": 0,
#   "group_b_required_count": 2,
#   "group_a_approvals_count": 0,
#   "group_a_required_count": 2,
#   ...
# }
```

#### Step 5: Approve Likes

```bash
# Becca approves (member of Group B)
curl -X POST "http://localhost:8080/matching/likes/1/approve" \
  -H "Authorization: Bearer BECCA_ACCESS_TOKEN"

# Response (still pending):
# {
#   "like": {
#     "id": 1,
#     "status": "pending_group_b",
#     "group_b_approvals_count": 1,
#     ...
#   },
#   "match": null,
#   "message": "Like approved"
# }

# Chelsea approves (member of Group B)
curl -X POST "http://localhost:8080/matching/likes/1/approve" \
  -H "Authorization: Bearer CHELSEA_ACCESS_TOKEN"

# Response (moved to next phase):
# {
#   "like": {
#     "id": 1,
#     "status": "pending_group_a",
#     "group_b_approvals_count": 2,
#     ...
#   },
#   "match": null,
#   "message": "Like approved"
# }

# David approves (member of Group A)
curl -X POST "http://localhost:8080/matching/likes/1/approve" \
  -H "Authorization: Bearer DAVID_ACCESS_TOKEN"

# Response (match created!):
# {
#   "like": {
#     "id": 1,
#     "status": "matched",
#     "group_a_approvals_count": 2,
#     ...
#   },
#   "match": {
#     "id": 1,
#     "group1_id": 1,
#     "group2_id": 2,
#     "matched_at": "2024-01-15T10:15:00Z",
#     ...
#   },
#   "message": "Match created!"
# }
```

#### Step 6: Get Matches

```bash
# Get all matches for a group
curl -X GET "http://localhost:8080/matching/groups/1/matches" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
# {
#   "matches": [
#     {
#       "id": 1,
#       "group1_id": 1,
#       "group2_id": 2,
#       "matched_at": "2024-01-15T10:15:00Z",
#       "is_active": true,
#       ...
#     }
#   ]
# }
```

### Complete Example Flow

Here's a complete example that creates two groups, has one like the other, and completes the approval process:

```bash
# 1. Sign up users
TOKEN_BRAD=$(curl -s -X POST "http://localhost:8080/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"brad@example.com","password":"password123","name":"Brad"}' \
  | jq -r '.tokens.access_token')

TOKEN_DAVID=$(curl -s -X POST "http://localhost:8080/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"david@example.com","password":"password123","name":"David"}' \
  | jq -r '.tokens.access_token')

TOKEN_BECCA=$(curl -s -X POST "http://localhost:8080/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"becca@example.com","password":"password123","name":"Becca"}' \
  | jq -r '.tokens.access_token')

TOKEN_CHELSEA=$(curl -s -X POST "http://localhost:8080/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"chelsea@example.com","password":"password123","name":"Chelsea"}' \
  | jq -r '.tokens.access_token')

# 2. Get user IDs (you'll need to extract these from the signup response or create a /me endpoint)
# For now, assume we know the UUIDs

# 3. Create Group A
GROUP_A=$(curl -s -X POST "http://localhost:8080/groups" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_BRAD" \
  -d '{"name":"Brad & David Crew","member_ids":[]}' \
  | jq -r '.id')

# 4. Add David to Group A
curl -X POST "http://localhost:8080/groups/$GROUP_A/members" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_BRAD" \
  -d "{\"user_id\":\"DAVID_UUID\",\"role\":\"member\"}"

# 5. Create Group B
GROUP_B=$(curl -s -X POST "http://localhost:8080/groups" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_BECCA" \
  -d '{"name":"Becca & Chelsea","member_ids":[]}' \
  | jq -r '.id')

# 6. Add Chelsea to Group B
curl -X POST "http://localhost:8080/groups/$GROUP_B/members" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_BECCA" \
  -d "{\"user_id\":\"CHELSEA_UUID\",\"role\":\"member\"}"

# 7. Group A likes Group B
LIKE_ID=$(curl -s -X POST "http://localhost:8080/matching/likes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_BRAD" \
  -d "{\"liker_group_id\":$GROUP_A,\"likee_group_id\":$GROUP_B}" \
  | jq -r '.id')

# 8. Becca approves
curl -X POST "http://localhost:8080/matching/likes/$LIKE_ID/approve" \
  -H "Authorization: Bearer $TOKEN_BECCA"

# 9. Chelsea approves (should move to pending_group_a)
curl -X POST "http://localhost:8080/matching/likes/$LIKE_ID/approve" \
  -H "Authorization: Bearer $TOKEN_CHELSEA"

# 10. David approves (should create match!)
curl -X POST "http://localhost:8080/matching/likes/$LIKE_ID/approve" \
  -H "Authorization: Bearer $TOKEN_DAVID"

# 11. Get matches
curl -X GET "http://localhost:8080/matching/groups/$GROUP_A/matches" \
  -H "Authorization: Bearer $TOKEN_BRAD"
```

### Test Flow Summary:

1. **Create two groups** with different members
2. **Create a like** from Group A to Group B
3. **Approve from Group B members** (wait for status to change to `pending_group_a`)
4. **Approve from Group A members** (match should be created)
5. **Get matches** to verify match was created

### Using Python (Direct Model Access)

If you're working directly with the database models (e.g., in scripts or tests), here are examples:

#### 1. Create a Group

```python
from app.models.matching import Group, GroupMember
from app.models.user import User

# Create a group
group = Group(
    name="Brad & David's Crew",
    created_by_id=brad_user_id,
    is_active=True
)
db.add(group)
db.commit()

# Add members to the group
member1 = GroupMember(
    group_id=group.id,
    user_id=brad_user_id,
    role='member',
    is_active=True
)
member2 = GroupMember(
    group_id=group.id,
    user_id=david_user_id,
    role='member',
    is_active=True
)
db.add_all([member1, member2])
db.commit()
```

#### 2. One Group Likes Another

```python
from app.models.matching import Like

# Count how many members in each group (for required counts)
group_a_member_count = db.query(GroupMember).filter(
    GroupMember.group_id == group_a_id,
    GroupMember.is_active == True
).count()

group_b_member_count = db.query(GroupMember).filter(
    GroupMember.group_id == group_b_id,
    GroupMember.is_active == True
).count()

# Create the like
like = Like(
    liker_group_id=group_a_id,
    likee_group_id=group_b_id,
    initiator_user_id=brad_user_id,
    group_b_required_count=group_b_member_count,  # How many need to approve
    group_a_required_count=group_a_member_count,   # How many need to approve
    status='pending_group_b'  # Start by waiting for Group B
)
db.add(like)
db.commit()
```

#### 3. Someone Approves

```python
# Becca approves (she's in Group B)
like = db.query(Like).filter(Like.id == like_id).first()

# Increment the approval count
like.group_b_approvals_count += 1

# Check if everyone in Group B approved
if like.group_b_approvals_count >= like.group_b_required_count:
    # Move to next phase: wait for Group A
    like.status = 'pending_group_a'

db.commit()
```

#### 4. Check if Match Should Be Created

```python
# After David approves (last person in Group A)
like.group_a_approvals_count += 1

if (like.group_a_approvals_count >= like.group_a_required_count and
    like.group_b_approvals_count >= like.group_b_required_count):
    
    # Update like status
    like.status = 'matched'
    like.matched_at = func.now()
    
    # Create the match
    from app.models.matching import Match
    
    # Ensure group1_id < group2_id (CHECK constraint requirement)
    group1_id = min(like.liker_group_id, like.likee_group_id)
    group2_id = max(like.liker_group_id, like.likee_group_id)
    
    match = Match(
        group1_id=group1_id,
        group2_id=group2_id,
        matched_at=func.now(),
        is_active=True
    )
    db.add(match)
    db.commit()
```

#### 5. Query Examples

**Get all groups a user is in:**
```python
groups = db.query(Group).join(GroupMember).filter(
    GroupMember.user_id == user_id,
    GroupMember.is_active == True
).all()
```

**Get all pending likes for a group:**
```python
pending_likes = db.query(Like).filter(
    Like.likee_group_id == group_id,
    Like.status == 'pending_group_b'
).all()
```

**Get all matches for a group:**
```python
matches = db.query(Match).filter(
    ((Match.group1_id == group_id) | (Match.group2_id == group_id)),
    Match.is_active == True
).order_by(Match.matched_at.desc()).all()
```

**Check approval status (fast!):**
```python
like = db.query(Like).filter(Like.id == like_id).first()

if like.group_b_approvals_count >= like.group_b_required_count:
    print("Group B fully approved!")
else:
    remaining = like.group_b_required_count - like.group_b_approvals_count
    print(f"Waiting for {remaining} more approvals from Group B")
```

#### Key Points to Remember

1. **Always set required counts** when creating a like (count active members)
2. **Increment approval counts** when someone approves
3. **Check both counts** before creating a match
4. **Use group1_id < group2_id** when creating matches (CHECK constraint)
5. **Use denormalized counts** for fast queries (don't count every time!)

---

## Next Steps (Phase 2)

- Get pending approvals for user
- Get likes sent/received by group
- Reject like endpoint
- Get group details
- Get group members
- Unmatch endpoint

---

## Future Extensibility

This design makes it easy to add:

1. **Group chat:** Add `match_id` to messages table
2. **Group events:** Add `group_id` to events table
3. **Approval history:** Add `like_approvals` table for detailed tracking (if needed)
4. **Group photos:** Add `group_id` to photos table
5. **Group settings:** Add columns to groups table

The design is **flexible** - we can add features without major restructuring!

---

## Summary

This matching system uses:
- **Junction tables** for many-to-many relationships
- **Denormalized approval counts** for performance
- **Database constraints** for data integrity
- **Soft deletes** for preserving history
- **Multi-step approval flow** for group-based matching

The design is optimized for:
- **Fast reads** (denormalized counts, indexes)
- **Data integrity** (constraints, foreign keys)
- **Scalability** (efficient queries, proper indexing)
- **Maintainability** (clear separation of concerns)

**Key takeaway:** Denormalization (storing counts) makes queries fast, and junction tables handle many-to-many relationships properly.

