## Extended Domain Design: Users, Todos, and Notifications

To make the service layer meaningful and worth testing, we extend the simple todos example into a richer domain with real business rules and cross-service coordination.

---

### UserService

**Responsibilities:**

- Manages users.
- Each user has a role:
  - `"user"`
  - `"admin"`

**Key Concepts:**

- Users own todos.
- Admin users have elevated permissions over all todos.

---

### TodoService

**Domain Rules & Responsibilities:**

- Todos belong to a specific user via `owner_id`.
- A user may have **at most `MAX_OPEN_TODOS`** incomplete todos at any time.
- Only:

  - The **owner** of a todo, or
  - An **admin**

  can update or delete a todo.

- When a user completes their **last open todo**, a notification event is triggered.

**Enforced Business Rules:**

- Open todo limit per user.
- Ownership and role-based authorization.
- Cross-service interaction with `NotificationService`.

---

### NotificationService

**Responsibilities:**

- Records domain events for users.
- Stores events such as:

  - `"ALL_TODOS_COMPLETED"`

**Used For:**

- Auditing
- User activity tracking
- Future integrations (email, push notifications, analytics, etc.)

---

## Why This Makes the Service Layer Valuable

With this design, the service layer now has real responsibilities:

- ✅ **Apply business rules**

  - Enforce todo limits
  - Enforce permissions

- ✅ **Coordinate multiple models and services**

  - User ↔ Todo ↔ Notification

- ✅ **Raise domain errors**
  - These are translated into HTTP responses by the API layer

This turns the service layer into the **core of your domain logic**, not just a thin wrapper over the database.
