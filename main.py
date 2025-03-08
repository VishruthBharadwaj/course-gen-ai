import json
import os
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langgraph.graph import StateGraph
from pydantic import BaseModel
from typing import Optional, List, Dict

# ------------------------------ Initialize Flask App & OpenAI API ------------------------------
app = Flask(__name__)
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)


# ------------------------------ Define State Schema for LangGraph ------------------------------
class CourseState(BaseModel):
    brief: str
    target_audience: str
    course_duration: str
    research_data: Optional[Dict] = None
    outline_data: Optional[Dict] = None
    expanded_modules: Optional[List[Dict]] = None


# ------------------------------  Research Agent ------------------------------
class ResearchAgent:
    def gather_information(self, state: CourseState) -> CourseState:
        """
        Fetches relevant content from Wikipedia to provide context for course generation.
        """
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(f"https://en.wikipedia.org/wiki/{state.brief.replace(' ', '_')}", headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find('div', {'id': 'mw-content-text'}).text[:500]  # Extract limited content
            state.research_data = {
                "content": content,
                "references": [
                    "World Bank Microfinance Handbook",
                    "Journal of Development Economics",
                    "Microfinance Institutions Network Report"
                ]
            }
        except Exception:
            state.research_data = {"content": "No relevant information found.", "references": []}
        return state


# ------------------------------ 📌 Curriculum Agent ------------------------------
class CurriculumAgent:
    def generate_outline(self, state: CourseState) -> CourseState:
        """
        Creates a structured JSON outline of the course using LangChain LLM.
        """
        messages = [
            SystemMessage(content="You are an expert curriculum planner. Generate a course outline."),
            HumanMessage(content=f"""
            Create a structured JSON course outline.

            Description: {state.brief}
            Audience: {state.target_audience}
            Duration: {state.course_duration}
            Context: {state.research_data['content'][:300]}

            Output format:
            {{
              "course_title": "Course Title",
              "description": "Detailed description.",
              "modules": [
                {{"title": "Module 1: [Title]"}},
                {{"title": "Module 2: [Title]"}},
                {{"title": "Module 3: [Title]"}},
                {{"title": "Module 4: [Title]"}},
                {{"title": "Module 5: [Title]"}}
              ]
            }}
            """)
        ]

        try:
            response = llm.invoke(messages)
            if response is None or not hasattr(response, "content") or not response.content.strip():
                raise ValueError("OpenAI API returned an empty response.")

            print("🔍 OpenAI Response (Outline):", response.content)

            state.outline_data = json.loads(response.content)
        except Exception as e:
            print(f"⚠️ OpenAI API Error: {e}")
            state.outline_data = {
                "course_title": "Fallback Course",
                "description": "This is a fallback course outline due to an API error.",
                "modules": [{"title": f"Module {i}: Placeholder"} for i in range(1, 6)]
            }

        return state


# ------------------------------  Content Agent ------------------------------
class ContentAgent:
    def expand_modules(self, state: CourseState) -> CourseState:
        """
        Expands each module into detailed lessons using LangChain LLM.
        """
        expanded_modules = []
        for module in state.outline_data["modules"]:
            messages = [
                SystemMessage(content="You are an expert course content creator. Expand this module."),
                HumanMessage(content=f"""
                Expand the module '{module['title']}' into structured JSON with lessons.

                Output format:
                {{
                  "title": "{module['title']}",
                  "lessons": [
                    {{
                      "title": "Lesson Title",
                      "content": "Detailed lesson content.",
                      "resources": ["Resource 1", "Resource 2"]
                    }}
                  ]
                }}
                """)
            ]
            try:
                response = llm.invoke(messages)
                if response is None or not hasattr(response, "content") or not response.content.strip():
                    raise ValueError("OpenAI API returned an empty response.")

                print("🔍 OpenAI Response (Module):", response.content)  

                expanded_module = json.loads(response.content)
                expanded_modules.append(expanded_module)
            except Exception as e:
                print(f"⚠️ OpenAI API Error: {e}")
                expanded_modules.append({
                    "title": module["title"],
                    "lessons": [{"title": "Fallback Lesson", "content": "Error in fetching content."}]
                })

        state.expanded_modules = expanded_modules
        return state


# ------------------------------ Course Generator using LangGraph ------------------------------
class CourseGenerator:
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.curriculum_agent = CurriculumAgent()
        self.content_agent = ContentAgent()

        # Define the LangGraph state with the correct schema
        self.graph = StateGraph(CourseState)

        # Add processing nodes with renamed keys to avoid conflicts
        self.graph.add_node("research_step", self.research_agent.gather_information)
        self.graph.add_node("outline_step", self.curriculum_agent.generate_outline)
        self.graph.add_node("content_step", self.content_agent.expand_modules)

        # Define the workflow order
        self.graph.set_entry_point("research_step")
        self.graph.add_edge("research_step", "outline_step")
        self.graph.add_edge("outline_step", "content_step")
        self.graph.set_finish_point("content_step")

        # Compile LangGraph workflow
        self.executor = self.graph.compile()

    def generate_course(self, brief, target_audience, course_duration):
        """
        Executes the LangGraph workflow with structured state data.
        """
        initial_state = CourseState(
            brief=brief,
            target_audience=target_audience,
            course_duration=course_duration
        )

        result = self.executor.invoke(initial_state)

        #  FIX: Use `.get()` instead of dot notation for LangGraph results
        return {
            "course_title": result.get("outline_data", {}).get("course_title", "Unknown Title"),
            "description": result.get("outline_data", {}).get("description", "No description available"),
            "modules": result.get("expanded_modules", []),
            "references": result.get("research_data", {}).get("references", [])
        }


# ------------------------------  Save Course Output to JSON File ------------------------------
def save_course_to_json(course_data):
    """
    Saves the generated course content to a JSON file.
    """
    filename = "generated_course.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(course_data, f, indent=2, ensure_ascii=False)
    print(f"Course saved as {filename}")


# ------------------------------ 🌐 Flask API Route ------------------------------
@app.route('/generate_course', methods=['POST'])
def generate_course_endpoint():
    """
    API Endpoint: Generates a course from user input and saves the output.
    """
    data = request.get_json()
    required_fields = ["brief", "target_audience", "course_duration"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    generator = CourseGenerator()
    course = generator.generate_course(data['brief'], data['target_audience'], data['course_duration'])

 
    save_course_to_json(course)

    return jsonify(course), 200


# ------------------------------ Run Flask Server ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
