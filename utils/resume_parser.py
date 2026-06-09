import pdfplumber
import docx
import re
from collections import Counter

class ResumeParser:
    def __init__(self):
        # Skill keywords (without spaCy)
        self.skill_keywords = {
            'python': ['python', 'django', 'flask', 'numpy', 'pandas', 'fastapi'],
            'java': ['java', 'spring', 'hibernate', 'j2ee', 'kotlin'],
            'web': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'nodejs'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'firebase'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins'],
            'ml': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'ai']
        }
    
    def extract_text_from_pdf(self, pdf_path):
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        except Exception as e:
            text = f"Error reading PDF: {str(e)}"
        return text
    
    def extract_text_from_docx(self, docx_path):
        text = ""
        try:
            doc = docx.Document(docx_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            text = f"Error reading DOCX: {str(e)}"
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
        exp_patterns = [
            r'(\d+)\+?\s*years?\s+of\s+experience',
            r'experience\s*:\s*(\d+)',
            r'(\d+)\s*years?\s+experience',
            r'(\d+)\+?\s*yrs?\s+exp',
            r'total exp[^:]*:\s*(\d+)'
        ]
        
        experience = 0
        for pattern in exp_patterns:
            match = re.search(pattern, text.lower())
            if match:
                experience = int(match.group(1))
                break
        
        return min(experience, 20)  # Cap at 20 years
    
    def extract_projects(self, text):
        # Look for project section
        project_pattern = r'(?:projects?|portfolio)(.*?)(?:\n\n|\Z)'
        match = re.search(project_pattern, text.lower(), re.DOTALL)
        
        if match:
            project_text = match.group(1)
            # Count bullet points, numbers, or project indicators
            projects = len(re.findall(r'[•●○■▪➢➣→-]|\d+\.|project', project_text))
            return min(projects, 10)
        
        # Also count "Project" word occurrences
        project_count = len(re.findall(r'\bproject\b', text.lower()))
        return min(project_count, 10)
    
    def calculate_communication_score(self, text):
        # Simple scoring without spaCy
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        if sentence_count == 0:
            return 5.0
        
        # Average sentence length
        words = re.findall(r'\b\w+\b', text.lower())
        avg_sentence_length = len(words) / max(sentence_count, 1)
        
        # Vocabulary richness (unique words / total words)
        unique_words = set(words)
        vocab_richness = len(unique_words) / max(len(words), 1)
        
        # Professional language indicators
        professional_words = ['managed', 'developed', 'implemented', 'designed', 
                              'created', 'led', 'achieved', 'spearheaded', 'coordinated']
        professional_count = sum(text.lower().count(word) for word in professional_words)
        
        # Calculate score (1-10)
        score = (
            (min(avg_sentence_length, 25) / 25) * 3 +  # Sentence length (max 3 points)
            (vocab_richness * 10) * 3 +  # Vocabulary richness (max 3 points)
            (min(professional_count, 20) / 20) * 4  # Professional terms (max 4 points)
        )
        
        return round(min(10, max(1, score)), 1)
    
    def parse_resume(self, file_path):
        # Extract text based on file type
        if file_path.endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = self.extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
        
        if not text or len(text.strip()) < 10:
            return {
                'skills': {},
                'experience_years': 0,
                'projects_count': 0,
                'communication_score': 5.0,
                'coding_score': 5.0,
                'aptitude_score': 5.0,
                'resume_text': "Could not extract text from file. Please ensure the file is not corrupted."
            }
        
        # Extract features
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        projects = self.extract_projects(text)
        communication_score = self.calculate_communication_score(text)
        
        # Calculate coding score based on technical skills
        tech_categories = ['python', 'java', 'web', 'database', 'cloud', 'ml']
        coding_score = sum(1 for cat in tech_categories if cat in skills) * 1.5
        coding_score = min(10, max(1, coding_score))
        
        # Calculate aptitude score based on analytical indicators
        analytical_words = ['analyzed', 'optimized', 'solved', 'calculated', 'statistical',
                           'algorithm', 'logic', 'reasoning', 'problem solving', 'debugged']
        analytical_count = sum(text.lower().count(word) for word in analytical_words)
        aptitude_score = min(10, max(1, 3 + (analytical_count / 15) * 7))
        
        return {
            'skills': skills,
            'experience_years': experience,
            'projects_count': projects,
            'communication_score': communication_score,
            'coding_score': round(coding_score, 1),
            'aptitude_score': round(aptitude_score, 1),
            'resume_text': text[:500]  # Store first 500 chars for preview
        }