import os
from typing import Dict, Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import google.generativeai as genai
import json

load_dotenv()

# Load Keys
gemini_api_key = os.getenv("GEMINI_API_KEY")
mongo_uri = os.getenv("MONGO_URI")

# Configure Gemini
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-pro")

# MongoDB Connection
def get_mongo_client():
    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        return client
    except ConnectionFailure as e:
        print("MongoDB connection failed:", e)
        raise

mongo_client = get_mongo_client()
db = mongo_client.todo_db
todos_collection = db.todos

# User Functions
def find_todo(title: str) -> Optional[Dict]:
    """Find a todo by title (case-insensitive)"""
    return todos_collection.find_one({"title": {"$regex": f"^{title}$", "$options": "i"}}, {"_id": 0})

def create_todo(title: str, description: str, status: str) -> Dict:
    """Create a new todo"""
    # Check if todo with same title already exists
    existing = find_todo(title)
    if existing:
        raise ValueError(f"Todo with title '{title}' already exists")
    
    todo_data = {
        "title": title,
        "description": description,
        "status": status
    }
    result = todos_collection.insert_one(todo_data)
    return {**todo_data, "id": str(result.inserted_id)}

def update_todo(title: str, description: Optional[str] = None, status: Optional[str] = None) -> Dict:
    """Update a todo by title"""
    # First check if todo exists
    existing_todo = find_todo(title)
    if not existing_todo:
        raise ValueError(f"Todo with title '{title}' not found")
    
    update_data = {}
    if description is not None and description.strip():
        update_data["description"] = description.strip()
    if status is not None and status.strip():
        update_data["status"] = status.strip()
    
    if not update_data:
        raise ValueError("No valid updates provided")
    
    result = todos_collection.update_one(
        {"title": {"$regex": f"^{title}$", "$options": "i"}},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise ValueError("No changes were made to the todo")
    
    return find_todo(title)

def delete_todo(title: str) -> bool:
    """Delete a todo by title"""
    result = todos_collection.delete_one({"title": {"$regex": f"^{title}$", "$options": "i"}})
    return result.deleted_count > 0

def list_todos(status_filter: Optional[str] = None) -> list:
    """List all todos, optionally filtered by status"""
    query = {}
    if status_filter:
        query["status"] = {"$regex": f"^{status_filter}$", "$options": "i"}
    
    return list(todos_collection.find(query, {"_id": 0}))

# Structured Command Processor
def process_command(command: str) -> str:
    parts = command.split()
    if not parts:
        return "Please enter a command."

    action = parts[0].lower()

    if action == "info" and len(parts) >= 2:
        title = " ".join(parts[1:])
        todo = find_todo(title)
        if not todo:
            return f"Todo with title '{title}' not found."
        return f"Title: {todo['title']}\nDescription: {todo.get('description', 'None')}\nStatus: {todo['status']}"

    elif action == "add" and len(parts) >= 2:
        title = parts[1]
        description = " ".join(parts[2:]) if len(parts) > 2 else ""
        try:
            create_todo(title, description, "pending")
            return f"Added todo: '{title}'"
        except ValueError as e:
            return str(e)

    elif action == "list":
        status_filter = parts[1] if len(parts) > 1 else None
        todos = list_todos(status_filter)
        if not todos:
            filter_text = f" with status '{status_filter}'" if status_filter else ""
            return f"No todos found{filter_text}."
        return "\n".join(
            f"{i+1}. {todo['title']} - {todo.get('description', 'No description')} [{todo['status']}]"
            for i, todo in enumerate(todos)
        )

    elif action == "delete" and len(parts) >= 2:
        title = " ".join(parts[1:])
        if delete_todo(title):
            return f"Successfully deleted todo: '{title}'"
        return f"Todo with title '{title}' not found."

    elif action == "edit" and len(parts) >= 2:
        title = parts[1]
        description = None
        status = None
        
        # Parse remaining arguments
        remaining_parts = parts[2:]
        if remaining_parts:
            # Check if last part is a status
            if remaining_parts[-1].lower() in ["pending", "completed"]:
                status = remaining_parts[-1].lower()
                if len(remaining_parts) > 1:
                    description = " ".join(remaining_parts[:-1])
            else:
                description = " ".join(remaining_parts)
        
        try:
            updated = update_todo(title, description, status)
            result = f"Updated todo: '{updated['title']}'"
            if description is not None:
                result += f"\nDescription: {updated.get('description', 'None')}"
            if status is not None:
                result += f"\nStatus: {updated['status']}"
            return result
        except ValueError as e:
            return str(e)

    elif action == "complete" and len(parts) >= 2:
        title = " ".join(parts[1:])
        try:
            updated = update_todo(title, status="completed")
            return f"Marked todo '{title}' as completed"
        except ValueError as e:
            return str(e)

    else:
        return """Unknown command. Available commands:
- info <title> - Show todo details
- add <title> [description] - Add new todo
- list [status] - Show all todos (optionally filter by status)
- delete <title> - Delete a todo by title
- edit <title> [description] [status] - Update a todo by title
- complete <title> - Mark a todo as completed"""

# Enhanced Natural Language Processing
def process_natural_command(prompt: str) -> str:
    extraction_prompt = f"""
Extract todo information from this command and return ONLY valid JSON:
"{prompt}"

Return JSON with these fields:
- action: "create_todo", "list_todos", "delete_todo", "edit_todo", "complete_todo", or "info_todo"
- title: string (required for all actions except list_todos)
- description: string (optional, only for create_todo and edit_todo)
- status: string ("pending" or "completed", optional for edit_todo)

Examples:
{{"action": "create_todo", "title": "buy groceries", "description": "milk and eggs"}}
{{"action": "edit_todo", "title": "clean room", "status": "completed"}}
{{"action": "delete_todo", "title": "old task"}}
{{"action": "list_todos"}}
{{"action": "complete_todo", "title": "homework"}}
"""
    
    try:
        response = model.generate_content(extraction_prompt)
        response_text = response.text.strip()
        
        # Try to find JSON in the response
        if response_text.startswith('```json'):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith('```'):
            response_text = response_text[3:-3].strip()
        
        try:
            extracted_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback to eval if JSON parsing fails
            extracted_data = eval(response_text)

        action = extracted_data.get("action")
        title = extracted_data.get("title", "").strip()
        
        if not title and action not in ["list_todos"]:
            return "Error: No title provided."

        if action == "create_todo":
            try:
                create_todo(
                    title=title,
                    description=extracted_data.get("description", ""),
                    status=extracted_data.get("status", "pending")
                )
                return f"Created todo: '{title}'"
            except ValueError as e:
                return str(e)

        elif action == "list_todos":
            status_filter = extracted_data.get("status")
            todos = list_todos(status_filter)
            if not todos:
                filter_text = f" with status '{status_filter}'" if status_filter else ""
                return f"No todos found{filter_text}."
            return "\n".join(
                f"{i+1}. {todo['title']} - {todo.get('description', 'No description')} [{todo['status']}]"
                for i, todo in enumerate(todos)
            )

        elif action == "delete_todo":
            if delete_todo(title):
                return f"Successfully deleted todo: '{title}'"
            return f"Todo with title '{title}' not found."

        elif action == "edit_todo":
            try:
                updated = update_todo(
                    title=title,
                    description=extracted_data.get("description"),
                    status=extracted_data.get("status")
                )
                result = f"Updated todo: '{updated['title']}'"
                if extracted_data.get("description"):
                    result += f"\nDescription: {updated.get('description', 'None')}"
                if extracted_data.get("status"):
                    result += f"\nStatus: {updated['status']}"
                return result
            except ValueError as e:
                return str(e)

        elif action == "complete_todo":
            try:
                updated = update_todo(title=title, status="completed")
                return f"Marked todo '{title}' as completed"
            except ValueError as e:
                return str(e)

        elif action == "info_todo":
            todo = find_todo(title)
            if not todo:
                return f"Todo with title '{title}' not found."
            return f"Title: {todo['title']}\nDescription: {todo.get('description', 'None')}\nStatus: {todo['status']}"

        else:
            return f"Unknown action: {action}"

    except Exception as e:
        return f"Error processing command: {str(e)}"

# Main Loop
def main():
    print("Todo CLI Application (Supports natural language)")
    print("Available commands:")
    print("- info <title> - Show todo details")
    print("- add <title> [description] - Add new todo")
    print("- list [status] - Show all todos (optionally filter by status)")
    print("- delete <title> - Delete a todo by title")
    print("- edit <title> [description] [status] - Update a todo by title")
    print("- complete <title> - Mark a todo as completed")
    print("\nOr use natural language like:")
    print("- 'Add buy milk to my todos'")
    print("- 'Delete the homework task'")
    print("- 'Mark grocery shopping as completed'")
    print("- 'Update meeting notes with new description'")
    print("Type 'quit' or 'exit' to end.\n")

    try:
        while True:
            prompt = input(">>> ").strip()
            if prompt.lower() in ['quit', 'exit']:
                break
            if not prompt:
                continue

            # Try structured commands first
            if prompt.split()[0].lower() in ['info', 'add', 'list', 'delete', 'edit', 'complete']:
                response = process_command(prompt)
            else:
                response = process_natural_command(prompt)

            print("\n" + response + "\n")
    finally:
        mongo_client.close()

if __name__ == "__main__":
    main()