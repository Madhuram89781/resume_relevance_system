import re
import os
import PyPDF2
from docx import Document
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
import string

class ResumeParser:
    def __init__(self):
        """Initialize the resume parser with required NLTK components"""
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            # If stopwords not downloaded, use basic English stopwords
            self.stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
                                 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 
                                 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 
                                 'itself', 'they', 'them', 'their', 'theirs', 'themselves'])
        
        # Common skills keywords (you can expand this)
        self.tech_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 
                          'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 
                          'css', 'typescript'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 
                         'nodejs', 'laravel', 'rails', 'bootstrap', 'jquery'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 
                        'cassandra', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'tools': ['git', 'github', 'gitlab', 'jira', 'slack', 'trello', 'figma', 'photoshop']
        }
        
        # Experience indicators
        self.experience_patterns = [
            r'(\d+)[\+\s]*years?\s+(?:of\s+)?experience',
            r'(\d+)[\+\s]*yrs?\s+(?:of\s+)?experience',
            r'experience\s+(?:of\s+)?(\d+)[\+\s]*years?',
            r'(\d+)[\+\s]*years?\s+in\s+',
            r'(\d+)[\+\s]*years?\s+working',
        ]

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")

    def extract_text_from_txt(self, file_path):
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")

    def extract_text(self, file_path):
        """Extract text based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return self.extract_text_from_docx(file_path)
        elif ext == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise Exception(f"Unsupported file format: {ext}")

    def extract_email(self, text):
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        return emails[0] if emails else None

    def extract_phone(self, text):
        """Extract phone numbers from text"""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
            r'\+\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None

    def extract_skills(self, text):
        """Extract technical skills from text"""
        text_lower = text.lower()
        found_skills = []
        
        for category, skills in self.tech_skills.items():
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates

    def extract_education(self, text):
        """Extract education information"""
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 
                            'diploma', 'certification', 'b.sc', 'm.sc', 'b.tech', 'm.tech', 
                            'mba', 'graduate', 'undergraduate']
        
        lines = text.split('\n')
        education_info = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                education_info.append(line.strip())
        
        return education_info[:3]  # Return first 3 education entries

    def extract_experience_years(self, text):
        """Extract years of experience from text"""
        text_lower = text.lower()
        years = []
        
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            years.extend([int(match) for match in matches])
        
        return max(years) if years else 0

    def extract_keywords(self, text):
        """Extract important keywords from text"""
        try:
            # Tokenize and remove stopwords
            tokens = word_tokenize(text.lower())
            tokens = [token for token in tokens if token not in self.stop_words 
                     and token not in string.punctuation and len(token) > 2]
            
            # Get word frequency
            word_freq = {}
            for word in tokens:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Return top keywords
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:20]]
        except:
            # Fallback if NLTK components not available
            words = text.lower().split()
            words = [word.strip(string.punctuation) for word in words if len(word) > 2]
            return list(set(words))[:20]

    def parse_text(self, text):
        """Parse resume text and extract structured information"""
        return {
            'raw_text': text,
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'skills': self.extract_skills(text),
            'education': self.extract_education(text),
            'experience_years': self.extract_experience_years(text),
            'keywords': self.extract_keywords(text)
        }

    def parse_resume(self, file_path):
        """Parse resume file and extract structured information"""
        try:
            # Extract text from file
            text = self.extract_text(file_path)
            
            if not text or len(text.strip()) < 50:
                raise Exception("File appears to be empty or has insufficient content")
            
            return self.parse_text(text)
            
        except Exception as e:
            raise Exception(f"Error parsing resume: {str(e)}")

# Test function
def test_parser():
    """Test the resume parser with sample text"""
    sample_text = """
    John Doe
    Software Developer
    Email: john.doe@email.com
    Phone: (555) 123-4567
    
    EXPERIENCE:
    5+ years of experience in software development
    
    SKILLS:
    Python, JavaScript, React, Django, MySQL, AWS
    
    EDUCATION:
    Bachelor of Science in Computer Science
    University of Technology, 2018
    """
    
    parser = ResumeParser()
    result = parser.parse_text(sample_text)
    print("Test Result:", result)

if __name__ == "__main__":
    test_parser()