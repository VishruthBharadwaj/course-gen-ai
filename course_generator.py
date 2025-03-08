import json
import openai
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import argparse

openai.api_key = os.getenv("OPENAI_API_KEY")

class ResearchAgent:
    def gather_information(self, topic):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}", headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find('div', {'id': 'mw-content-text'}).text[:2000]
            return {"content": content, "references": ["World Bank Microfinance Handbook", "Journal of Development Economics", "Microfinance Institutions Network Report"]}
        except Exception as e:
            return {"content": "", "references": []}

class CurriculumAgent:
    def create_outline(self, description, audience, duration, research_content):
        prompt = f"""
        Generate a structured course outline in JSON based on the description below.

        Description: {description}
        Audience: {audience}
        Duration: {duration}
        Context: {research_content}

        Output format:
        {{
          "course_title": "Introduction to Microfinance: Fundamentals and Applications",
          "description": "A comprehensive introduction to microfinance principles, designed for beginners with no prior financial knowledge.",
          "modules": [
            {{
              "title": "Module 1: [Module Title]"
            }},
            {{
              "title": "Module 2: [Module Title]"
            }},
            {{
              "title": "Module 3: [Module Title]"
            }},
            {{
              "title": "Module 4: [Module Title]"
            }},
            {{
              "title": "Module 4: [Module Title]"
            }},
            {{
              "title": "Module 4: [Module Title]"
            }}
          ]
        }}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)

class ContentAgent:
    def expand_module(self, module):
        prompt = f"""
        Expand the module titled '{module['title']}' into structured JSON with lessons.

        Format:
        {{
          "title": "{module['title']}",
          "lessons": [
            {{
              "title": "Lesson Title",
              "content": "Detailed lesson content...",
              "resources": ["Resource 1", "Resource 2"]
            }}
          ]
        }}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)

class CourseGenerator:
    def __init__(self):
        self.researcher = ResearchAgent()
        self.curriculum = CurriculumAgent()
        self.content = ContentAgent()

    def generate_course(self, brief, target_audience, course_duration):
        research = self.researcher.gather_information(brief)
        outline = self.curriculum.create_outline(brief, target_audience, course_duration, research["content"][:500])

        detailed_modules = []
        for module in outline["modules"]:
            detailed_module = self.content.expand_module(module)
            detailed_modules.append(detailed_module)

        outline["modules"] = detailed_modules
        outline["references"] = research["references"]
        return outline

def save_course(filename, course_data):
    with open(filename, 'w') as f:
        json.dump(course_data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Generate course JSON')
    parser.add_argument('brief', type=str, help='Course brief')
    parser.add_argument('target_audience', type=str, help='Target audience')
    parser.add_argument('course_duration', type=str, help='Course duration')

    args = parser.parse_args()

    generator = CourseGenerator()
    course = generator.generate_course(args.brief, args.target_audience, args.course_duration)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"course_{timestamp}.json"

    save_course(filename, course)
    print(f"Course saved to {filename}")

if __name__ == "__main__":
    main()
