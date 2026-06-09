import pdfplumber
import docx
import re
import spacy
import nltk
from nltk.corpus import stopwords
from collections import Counter

nltk.download('stopwords', quiet=True)

class ResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        self.stop_words = set(stopwords.words('english'))
        
        # Skill keywords
        self.skill_keywords = {
            'python': ['python', 'django', 'flask', 'numpy', 'pandas'],
            'java': ['java', 'spring', 'hibernate', 'j2ee'],
            'web': ['html', 'css', 'javascript', 'react', 'angular', 'vue'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'ml': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn']
        }
    
    def extract_text_from_pdf(self, pdf_path):
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    
    def extract_text_from_docx(self, docx_path):
        doc = docx.Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    def extract_skills(self, text):
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self.skill_keywords.items():
            found = []
            for skill in skills:
                if skill in text_lower:
                    found.append(skill)
            if found:
                found_skills[category] = found
        
        return found_skills
    
    def extract_experience(self, text):
        # Look for years of experience
        exp_patterns = [
            r'(\d+)\+?\s*years?\s+of\s+experience',
            r'experience\s*:\s*(\d+)',
            r'(\d+)\s*years?\s+experience'
        ]
        
        experience = 0
        for pattern in exp_patterns:
            match = re.search(pattern, text.lower())
            if match:
                experience = int(match.group(1))
                break
        
        return experience
    
    def extract_projects(self, text):
        # Look for project section
        project_pattern = r'(?:projects?|portfolio)(.*?)(?:\n\n|\Z)'
        match = re.search(project_pattern, text.lower(), re.DOTALL)
        
        if match:
            project_text = match.group(1)
            # Count bullet points or numbered items
            projects = len(re.findall(r'[•●○■▪➢➣→-]|\d+\.', project_text))
            return min(projects, 10)  # Cap at 10
        
        return 0
    
    def calculate_communication_score(self, text):
        # Metrics for communication score
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        # Vocabulary richness
        words = re.findall(r'\b\w+\b', text.lower())
        unique_words = set(words)
        vocab_richness = len(unique_words) / max(len(words), 1)
        
        # Professional language indicators
        professional_words = ['managed', 'developed', 'implemented', 'designed', 'created', 'led', 'achieved']
        professional_count = sum(text.lower().count(word) for word in professional_words)
        
        score = min(10, (avg_sentence_length / 20) * 3 + (vocab_richness * 10) + (professional_count / 5))
        return round(score, 1)
    
    def parse_resume(self, file_path):
        # Extract text based on file type
        if file_path.endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = self.extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
        
        # Extract features
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        projects = self.extract_projects(text)
        communication_score = self.calculate_communication_score(text)
        
        # Calculate coding score based on technical skills
        tech_categories = ['python', 'java', 'web', 'database', 'cloud', 'ml']
        coding_score = sum(1 for cat in tech_categories if cat in skills) * 2
        coding_score = min(10, coding_score)
        
        # Calculate aptitude score (based on analytical indicators)
        analytical_words = ['analyzed', 'optimized', 'solved', 'calculated', 'statistical']
        analytical_count = sum(text.lower().count(word) for word in analytical_words)
        aptitude_score = min(10, 5 + analytical_count / 10)
        
        return {
            'skills': skills,
            'experience_years': experience,
            'projects_count': projects,
            'communication_score': communication_score,
            'coding_score': coding_score,
            'aptitude_score': round(aptitude_score, 1),
            'resume_text': text[:500]  # Store first 500 chars for preview
        }