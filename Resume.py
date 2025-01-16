import requests
import streamlit as st
from fpdf import FPDF

api_key = ""  # use you own API key from aimlapi.com

# Main AI block 
def get_skill(role, api_key, model_name="mistralai/Mistral-7B-Instruct-v0.2", debug=False):
    try:
        url = "https://api.aimlapi.com/v1/chat/completions"
        system_prompt = "You are a career advisor. List the key skills required for the role described."
        user_prompt = f"List 10 key skills required for a {role} professional. Provide only concise single words separated by commas."

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 256,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post(url, headers=headers, json=payload)

        if debug:
            print("Debug Information:")
            print("Payload Sent:", payload)
            print("Headers Sent:", headers)
            print("Response Code:", response.status_code)
            print("Response Text:", response.text)

        response.raise_for_status()

        data = response.json()
        if "choices" in data and data["choices"]:
            skills_text = data["choices"][0]["message"]["content"]
            skills = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
            return skills  
        else:
            return ["No recommendations available."]
    except Exception as e:
        if debug:
            print("Error encountered:", str(e))
        return [f"Error: {str(e)}"]
    
# Class Created 
class ResumePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.first_page = True

    def header(self):
        if self.first_page:
            self.set_font("Arial", style="B", size=16)
            self.set_text_color(0, 0, 128)
            self.cell(0, 10, "Resume", border=False, ln=True, align="C")
            self.ln(5)
            self.first_page = False

    def section_title(self, title):
        self.set_font("Arial", style="B", size=14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def section_body(self, text):
        self.set_font("Arial", size=12)
        self.set_text_color(80, 80, 80)
        self.multi_cell(0, 10, text)
        self.ln(5)

    def bullet_list(self, items):
        self.set_font("Arial", size=12)
        self.set_text_color(80, 80, 80)
        for item in items:
            self.cell(10, 10, txt="- ", border=0)
            self.multi_cell(0, 10, item)
        self.ln(5)

    def hyperlink(self, label, url):
        self.set_text_color(0, 0, 255)
        self.set_font("Arial", style="U", size=12)
        self.cell(0, 10, label, ln=True, link=url)
        self.set_text_color(0, 0, 0)  

# Generating PDF by calling the Resume PDF class
def generate(name, email, phone, education, experiences, skills, programming_skills, social_links, projects_workshops):
    pdf = ResumePDF() #object 
    pdf.add_page()

    pdf.section_title("Personal Details")
    pdf.section_body(f"Name: {name}\nEmail: {email}\nPhone: {phone}")

    pdf.section_title("Social Media Links")
    for platform, url in social_links.items():
        if url:
            pdf.hyperlink(platform, url)

    pdf.section_title("Education")
    pdf.section_body(education)

    pdf.section_title("Work Experience")
    pdf.section_body(experiences)

    pdf.section_title("Programming Skills")
    if programming_skills.strip():
        pdf.section_body(programming_skills)
    else:
        pdf.section_body("No programming skills added.")

    pdf.section_title("Skills")
    pdf.bullet_list(skills)

    pdf.section_title("Projects & Workshops")
    pdf.bullet_list(projects_workshops)

    file_name = "resume.pdf"
    pdf.output(file_name, 'F')
    return file_name

# UI using Streamlit
st.title("AI Resume Builder")

st.header("Personal Details")
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")

st.header("Social Media Links")
facebook = st.text_input("Facebook URL")
instagram = st.text_input("Instagram URL")
linkedin = st.text_input("LinkedIn URL")
github = st.text_input("GitHub URL")
social_links = {
    "Facebook": facebook,
    "Instagram": instagram,
    "LinkedIn": linkedin,
    "GitHub": github
}

st.header("Education")
education = st.text_area("Enter your Educational Background (Degree, College/School, Year)")

st.header("Work Experience")
experiences = st.text_area("Describe your Work Experiences")

st.header("Programming Skills")
programming_skills = st.text_area("List your programming skills and proficiency levels (e.g., Python: Level 5, JavaScript: Level 4)")

st.header("Skills")
skills = st.text_input("List your skills (comma-separated)")
role = st.text_input("Enter your targeted job role for AI recommendation")

selected_skills = []
if role:
    recommended_skills = get_skill(role, api_key, debug=True)  
    st.header("AI-Recommended Skills")
    st.write("Select the skills you want to include:")
    for skill in recommended_skills:
        if st.checkbox(skill):
            selected_skills.append(skill)

st.header("Projects & Workshops")
projects_workshops = st.text_area("List your projects or workshops (one per line)").split("\n")


#Button to Generate & Download the Resume
if st.button("Generate Resume"):
    if name and email and phone:
        skill_combined = [s.strip() for s in skills.split(",") if s.strip()] + selected_skills
        file_path = generate(
            name, email, phone, education, experiences, skill_combined, programming_skills, social_links, projects_workshops
        )
        st.success("Resume Generated Successfully!")

        with open(file_path, "rb") as file:
            st.download_button(
                label="Download Resume",
                data=file,
                file_name="resume.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Please fill in all required fields (Name, Email, Phone).")
