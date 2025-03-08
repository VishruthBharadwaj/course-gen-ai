# Course Generation System

## 📌 Overview

This project is a **multi-agent system** designed to generate complete educational courses from a brief description. The system utilizes  **LangGraph** ,  **LangChain** , and **Flask** to research course topics, organize them into modules, and generate structured course content.

## 🚀 Features

* Accepts a  **brief course description** ,  **target audience** , and  **course duration** .
* Uses **Wikipedia** to research relevant sources and enhance content accuracy.
* Generates **5-6 course modules** using LangChain's  **GPT-3.5-turbo** .
* Expands modules into **detailed lessons** with structured content.
* Saves the generated course **as a JSON file** for further use.
* Provides a **Flask API endpoint** to request course generation.

## 🛠️ Tech Stack

* **Python 3.11**
* **Flask** (for API handling)
* **LangChain & LangGraph** (for multi-agent workflow execution)
* **BeautifulSoup** (for web scraping Wikipedia)
* **OpenAI GPT-3.5 Turbo** (for text generation)
* **Pydantic** (for structured state management)

## 📂 Project Structure

```
📦 CourseGenAI
 ┣ 📜 main.py  # Main backend application with Flask API
 ┣ 📜 requirements.txt  # Required dependencies
 ┣ 📜 generated_course.json  # Output JSON file
 ┗ 📜 README.md  # Project documentation
```

## ⚙️ Installation

### 1️⃣ Clone the repository

```sh
git clone https://github.com/VishruthBharadwaj/course-gen-ai.git
cd course-gen-ai
```

### 2️⃣ Create a virtual environment & activate it

```sh
python3 -m venv autogen_env
source autogen_env/bin/activate  # For Linux/macOS
# OR
autogen_env\Scripts\activate  # For Windows
```

### 3️⃣ Install dependencies

```sh
pip install -r requirements.txt
```

### 4️⃣ Set up OpenAI API Key

Create a `.env` file and add your API key:

```
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Running the Application

```sh
python main.py
```

## 🔥 Using the API

The API provides an endpoint to generate course content.

### **Endpoint:** `/generate_course`

**Method:** `POST`
**Request Body (JSON):**

```json
{
  "brief": "Python for Data Science",
  "target_audience": "Beginners with no prior programming experience",
  "course_duration": "8 weeks"
}
```

**Example Request (cURL):**

```sh
curl -X POST "http://127.0.0.1:5000/generate_course" \
     -H "Content-Type: application/json" \
     -d '{
           "brief": "Python for Data Science",
           "target_audience": "Beginners with no prior programming experience",
           "course_duration": "8 weeks"
         }'
```

**Response (JSON):**

```json
{
  "course_title": "Python for Data Science",
  "description": "An introductory course for beginners learning data science with Python.",
  "modules": [...],
  "references": [
    "Python Data Science Handbook",
    "Machine Learning with Python"
  ]
}
```

## 📜 Workflow

1️⃣ **ResearchAgent** → Fetches contextual information from Wikipedia.
2️⃣ **CurriculumAgent** → Generates a structured course outline using OpenAI.
3️⃣ **ContentAgent** → Expands modules into detailed lessons.
4️⃣ **LangGraph Workflow** → Manages the execution of agents.

## 🛠️ Debugging & Logging

* If the OpenAI API request fails, a **fallback course structure** is returned.
* Errors and warnings are printed in the console.
* The generated course is saved as `generated_course.json`.

## 📌 Future Enhancements

✅ Support for **multiple languages**
✅ Improved **course customization** options
✅ Integration with **LMS platforms**
✅ Use of **vector databases** for research

## 📜 License

This project is open-source under the MIT License.

## 👨‍💻 Contributors

* **Vishruth**- Developer & Maintainer
* **Open to Contributors!** Feel free to fork and contribute!
