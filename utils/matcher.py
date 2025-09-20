import re
import math
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

class ResumeMatcher:
    def __init__(self):
        """Initialize the resume matcher"""
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            # Fallback stopwords if NLTK data not available
            self.stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
                                 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 
                                 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 
                                 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                                 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
                                 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                                 'should', 'could', 'can', 'may', 'might', 'must', 'shall'])

    def preprocess_text(self, text):
        """Preprocess text for analysis"""
        if not text:
            return []
        
        try:
            # Tokenize using NLTK
            tokens = word_tokenize(text.lower())
        except:
            # Fallback tokenization
            tokens = text.lower().split()
        
        # Remove stopwords and punctuation
        tokens = [token for token in tokens 
                 if token not in self.stop_words 
                 and token not in string.punctuation 
                 and len(token) > 2
                 and not token.isdigit()]
        
        return tokens

    def extract_job_requirements(self, job_description):
        """Extract key requirements from job description"""
        requirements = {
            'required_skills': [],
            'preferred_skills': [],
            'experience_required': 0,
            'education_keywords': [],
            'all_keywords': []
        }
        
        text = job_description.lower()
        
        # Extract years of experience required
        experience_patterns = [
            r'(\d+)[\+\s]*years?\s+(?:of\s+)?experience',
            r'(\d+)[\+\s]*yrs?\s+(?:of\s+)?experience',
            r'minimum\s+of\s+(\d+)\s+years?',
            r'at\s+least\s+(\d+)\s+years?'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text)
            if matches:
                requirements['experience_required'] = max([int(match) for match in matches])
                break
        
        # Extract skills (look for common patterns)
        skill_patterns = [
            r'(?:experience with|knowledge of|proficient in|skilled in)\s+([^.]+)',
            r'(?:requirements?|qualifications?).*?:\s*([^.]+)',
            r'(?:must have|should have)\s+([^.]+)'
        ]
        
        skills_text = ""
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills_text += " ".join(matches) + " "
        
        # Common technical skills to look for
        tech_skills = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 'django', 
                      'flask', 'spring', 'nodejs', 'sql', 'mysql', 'postgresql', 'mongodb',
                      'aws', 'azure', 'docker', 'kubernetes', 'git', 'html', 'css', 'php',
                      'c++', 'c#', 'ruby', 'go', 'swift', 'kotlin', 'machine learning',
                      'data science', 'artificial intelligence', 'ai', 'ml', 'tensorflow',
                      'pytorch', 'pandas', 'numpy', 'scikit-learn']
        
        for skill in tech_skills:
            if skill in text:
                requirements['required_skills'].append(skill)
        
        # Extract education keywords
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma', 'certification',
                            'computer science', 'engineering', 'mba', 'graduate']
        
        for keyword in education_keywords:
            if keyword in text:
                requirements['education_keywords'].append(keyword)
        
        # Get all important keywords
        requirements['all_keywords'] = self.preprocess_text(job_description)
        
        return requirements

    def calculate_skill_match(self, resume_skills, required_skills):
        """Calculate skill match percentage"""
        if not required_skills:
            return 0.5  # Neutral score if no specific skills mentioned
        
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        matched_skills = set(resume_skills_lower) & set(required_skills_lower)
        
        if not required_skills_lower:
            return 0.5
        
        score = len(matched_skills) / len(required_skills_lower)
        return min(score, 1.0)  # Cap at 100%

    def calculate_experience_match(self, resume_experience, required_experience):
        """Calculate experience match score"""
        if required_experience == 0:
            return 1.0  # If no experience specified, full score
        
        if resume_experience >= required_experience:
            return 1.0
        elif resume_experience >= required_experience * 0.8:
            return 0.8  # 80% if close to required
        elif resume_experience >= required_experience * 0.5:
            return 0.5  # 50% if half the required experience
        else:
            return resume_experience / required_experience  # Proportional score

    def calculate_keyword_similarity(self, resume_keywords, job_keywords):
        """Calculate keyword similarity using TF-IDF-like approach"""
        if not job_keywords or not resume_keywords:
            return 0.0
        
        # Convert to counters
        resume_counter = Counter(resume_keywords)
        job_counter = Counter(job_keywords)
        
        # Find common keywords
        common_keywords = set(resume_counter.keys()) & set(job_counter.keys())
        
        if not common_keywords:
            return 0.0
        
        # Calculate similarity score
        numerator = sum(resume_counter[word] * job_counter[word] for word in common_keywords)
        
        resume_norm = math.sqrt(sum(count ** 2 for count in resume_counter.values()))
        job_norm = math.sqrt(sum(count ** 2 for count in job_counter.values()))
        
        if resume_norm == 0 or job_norm == 0:
            return 0.0
        
        similarity = numerator / (resume_norm * job_norm)
        return min(similarity, 1.0)

    def calculate_education_match(self, resume_education, job_education_keywords):
        """Calculate education match score"""
        if not job_education_keywords:
            return 1.0  # If no education requirements specified
        
        if not resume_education:
            return 0.2  # Low score if no education info found
        
        resume_edu_text = " ".join(resume_education).lower()
        matches = 0
        
        for keyword in job_education_keywords:
            if keyword.lower() in resume_edu_text:
                matches += 1
        
        if not job_education_keywords:
            return 1.0
        
        return matches / len(job_education_keywords)

    def calculate_overall_score(self, skill_score, experience_score, keyword_score, education_score):
        """Calculate weighted overall score"""
        weights = {
            'skills': 0.4,      # 40% weight for skills match
            'experience': 0.25,  # 25% weight for experience
            'keywords': 0.25,    # 25% weight for keyword similarity
            'education': 0.1     # 10% weight for education
        }
        
        overall_score = (
            skill_score * weights['skills'] +
            experience_score * weights['experience'] +
            keyword_score * weights['keywords'] +
            education_score * weights['education']
        )
        
        return round(overall_score * 100, 2)  # Convert to percentage

    def get_match_feedback(self, skill_score, experience_score, keyword_score, education_score, 
                          matched_skills, missing_skills, resume_exp, required_exp):
        """Generate detailed feedback for the match"""
        feedback = []
        
        # Skills feedback
        if skill_score >= 0.8:
            feedback.append("✅ Excellent skills match")
        elif skill_score >= 0.6:
            feedback.append("✅ Good skills match")
        elif skill_score >= 0.4:
            feedback.append("⚠️ Partial skills match")
        else:
            feedback.append("❌ Limited skills match")
        
        if matched_skills:
            feedback.append(f"📋 Matched skills: {', '.join(matched_skills)}")
        
        if missing_skills:
            feedback.append(f"📋 Missing skills: {', '.join(missing_skills[:5])}")  # Show first 5
        
        # Experience feedback
        if experience_score >= 0.8:
            feedback.append("✅ Experience requirements met")
        elif experience_score >= 0.5:
            feedback.append("⚠️ Experience partially meets requirements")
        else:
            feedback.append("❌ Experience below requirements")
        
        feedback.append(f"📈 Experience: {resume_exp} years (Required: {required_exp} years)")
        
        # Overall keyword match feedback
        if keyword_score >= 0.6:
            feedback.append("✅ Strong keyword relevance")
        elif keyword_score >= 0.3:
            feedback.append("⚠️ Moderate keyword relevance")
        else:
            feedback.append("❌ Low keyword relevance")
        
        return feedback

    def match_single_resume(self, resume_data, job_requirements):
        """Match a single resume against job requirements"""
        # Calculate individual scores
        skill_score = self.calculate_skill_match(
            resume_data.get('skills', []), 
            job_requirements['required_skills']
        )
        
        experience_score = self.calculate_experience_match(
            resume_data.get('experience_years', 0),
            job_requirements['experience_required']
        )
        
        keyword_score = self.calculate_keyword_similarity(
            resume_data.get('keywords', []),
            job_requirements['all_keywords']
        )
        
        education_score = self.calculate_education_match(
            resume_data.get('education', []),
            job_requirements['education_keywords']
        )
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(
            skill_score, experience_score, keyword_score, education_score
        )
        
        # Find matched and missing skills
        resume_skills_lower = [skill.lower() for skill in resume_data.get('skills', [])]
        required_skills_lower = [skill.lower() for skill in job_requirements['required_skills']]
        
        matched_skills = list(set(resume_skills_lower) & set(required_skills_lower))
        missing_skills = list(set(required_skills_lower) - set(resume_skills_lower))
        
        # Generate feedback
        feedback = self.get_match_feedback(
            skill_score, experience_score, keyword_score, education_score,
            matched_skills, missing_skills,
            resume_data.get('experience_years', 0),
            job_requirements['experience_required']
        )
        
        return {
            'filename': resume_data.get('filename', 'Unknown'),
            'overall_score': overall_score,
            'skill_score': round(skill_score * 100, 2),
            'experience_score': round(experience_score * 100, 2),
            'keyword_score': round(keyword_score * 100, 2),
            'education_score': round(education_score * 100, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'feedback': feedback,
            'resume_data': resume_data
        }

    def match_resumes(self, resume_list, job_description):
        """Match multiple resumes against job description"""
        # Extract job requirements
        job_requirements = self.extract_job_requirements(job_description)
        
        results = []
        
        # Match each resume
        for resume_data in resume_list:
            match_result = self.match_single_resume(resume_data, job_requirements)
            results.append(match_result)
        
        # Sort by overall score (highest first)
        results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Add ranking
        for i, result in enumerate(results, 1):
            result['rank'] = i
        
        return {
            'matches': results,
            'job_requirements': job_requirements,
            'total_resumes': len(results)
        }

# Test function
def test_matcher():
    """Test the resume matcher with sample data"""
    # Sample resume data
    sample_resume = {
        'filename': 'test_resume.pdf',
        'skills': ['python', 'django', 'javascript', 'sql'],
        'experience_years': 3,
        'education': ['Bachelor of Science in Computer Science'],
        'keywords': ['python', 'web', 'development', 'django', 'database', 'frontend']
    }
    
    # Sample job description
    sample_job = """
    We are looking for a Python Developer with 2+ years of experience.
    Required skills: Python, Django, JavaScript, HTML, CSS
    Experience with SQL databases preferred.
    Bachelor's degree in Computer Science or related field required.
    """
    
    matcher = ResumeMatcher()
    results = matcher.match_resumes([sample_resume], sample_job)
    
    print("Test Results:")
    print(f"Overall Score: {results['matches'][0]['overall_score']}%")
    print(f"Matched Skills: {results['matches'][0]['matched_skills']}")
    print(f"Feedback: {results['matches'][0]['feedback']}")

if __name__ == "__main__":
    test_matcher()