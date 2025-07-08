Here's a complete **`README.md`** for your AI-powered CLI Todo App using Python, MongoDB, and Gemini:

---

````markdown
# 📝 AI-Powered Todo CLI App

This is a command-line Todo application built with **Python**, powered by **MongoDB** for data storage and **Gemini AI** for natural language command interpretation.

---

## 🚀 Features

- ✅ Add, edit, delete, and view todos using structured or natural commands
- 🤖 Natural Language Processing powered by **Google Generative AI (Gemini)**
- 📦 Persistent data storage using **MongoDB**
- 🔍 Case-insensitive search and filtering by status
- 🧠 Intelligent parsing of commands like:
  - “Add buy milk to my todos”
  - “Mark homework as completed”
  - “Delete the gym task”

---

## 🛠️ Tech Stack

| Layer         | Technology                |
|---------------|---------------------------|
| Language      | Python                    |
| AI/NLP        | Google Generative AI (Gemini) |
| Database      | MongoDB                   |
| Driver        | pymongo                   |
| Env Config    | python-dotenv             |
| Interface     | Command Line (CLI)        |

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-todo-cli.git
cd ai-todo-cli
````

### 2. Create a `.env` file

```env
GEMINI_API_KEY=your_gemini_api_key
MONGO_URI=your_mongodb_uri
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Tip**: If `requirements.txt` doesn't exist, install manually:

```bash
pip install pymongo python-dotenv google-generativeai
```

---

## 🧑‍💻 Usage

### Start the App

```bash
python app.py
```

### Available Structured Commands

```
add <title> [description]        - Add a new todo
info <title>                     - Show details of a todo
list [status]                    - List todos (filter by 'pending' or 'completed')
edit <title> [desc] [status]     - Edit description and/or status
delete <title>                   - Delete a todo
complete <title>                 - Mark as completed
```

### Example

```bash
>>> add homework Finish math exercises
>>> complete homework
>>> list completed
```

---

### Natural Language Examples

You can also use free-form English:

```
>>> Add “Buy groceries” to my todo list
>>> Mark meeting as completed
>>> Update gym task with new description
>>> Delete the laundry task
```

---

## 📁 Project Structure

```
.
├── app.py              # Main CLI logic
├── .env                # Environment variables
├── README.md           # Documentation
└── requirements.txt    # Dependencies (optional)
```

---

## ✅ Future Improvements

* Add deadline and priority fields
* Voice command support
* Web UI using Flask or FastAPI
* Authentication for multiple users

---

## 📄 License

MIT License. Free to use and modify.

---

## ✨ Author

Made by \[Bilal Rafique] – [@yourusername](https://github.com/bilal-157)

```
