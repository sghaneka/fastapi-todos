// MongoDB initialization script
// Creates a non-root user for the todo_db database

db = db.getSiblingDB("todo_db");

db.createUser({
  user: "todo_user",
  pwd: "todo_password",
  roles: [
    {
      role: "readWrite",
      db: "todo_db",
    },
  ],
});

// Create some sample collections (optional)
db.createCollection("todos");
db.createCollection("users");
db.createCollection("notifications");
