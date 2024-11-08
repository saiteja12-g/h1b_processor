import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
import io
import docx2txt
from openai import OpenAI
import json
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

def read_file_content(file) -> Optional[str]:
    """Read content from uploaded file"""
    if file is None:
        return None
        
    try:
        file_type = file.name.split('.')[-1].lower()
        
        if file_type == 'pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            return " ".join(page.extract_text() for page in pdf_reader.pages)
        elif file_type == 'docx':
            return docx2txt.process(io.BytesIO(file.read()))
        elif file_type == 'txt':
            return file.getvalue().decode('utf-8')
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None
            
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def analyze_resume_jd_match(resume_text: str, jd_text: str) -> Dict:
    """Analyze match between resume and job description"""
    prompt = f"""
    Analyze the match between this resume and job description.
    
    Job Description:
    {jd_text}
    
    Resume:
    {resume_text}
    
    Provide a JSON response with:
    1. Match percentage (0-100)
    2. Matching skills and qualifications
    3. Missing requirements
    4. Job title and level match
    5. Required education level from JD
    6. Industry alignment
    
    Format:
    {{
        "match_percentage": number,
        "matching_skills": list,
        "missing_requirements": list,
        "job_title_match": boolean,
        "required_education": string,
        "industry_alignment": string,
        "role_summary": string
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert ATS system analyzer. Please assess the alignment between the skills in my resume and the job description. If specific skills do not directly match the job requirements, evaluate their relevance by checking if they fall under broader, related categories that still align with the role's core competencies. For example, skills in machine learning (ML) may fall under computer science (CS) and thus may be relevant for certain CS roles even if ML isn't specifically mentioned.  Apply a flexible but balanced approach in your analysis, where related skills under larger domains or fields should receive consideration, while still prioritizing direct matches to the job description requirements."},
                {"role": "user", "content": prompt}
            ]
        )
        # st.write(response.choices[0].message.content)
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        st.error(f"Error in resume-JD analysis: {str(e)}")
        return None

def calculate_visa_timeline(visa_status: str, start_date: datetime, end_date: Optional[datetime]) -> Dict:
    """Calculate visa timeline and key dates"""
    today = datetime.now()
    next_h1b_window = datetime(today.year + (1 if today.month >= 4 else 0), 1, 15)  # Jan 15th next year
    h1b_results_date = datetime(next_h1b_window.year, 4, 15)  # April 15th of application year
    
    timeline = {
        "current_status": visa_status,
        "days_remaining": None,
        "needs_immediate_action": False,
        "next_h1b_window": next_h1b_window.strftime("%Y-%m-%d"),
        "results_date": h1b_results_date.strftime("%Y-%m-%d"),
        "recommended_action": "",
        "risk_level": "LOW"
    }
    
    if end_date:
        days_remaining = (end_date - today).days
        timeline["days_remaining"] = days_remaining
        
        # Calculate hiring window consideration
        hiring_window = timedelta(days=30)
        effective_deadline = end_date - hiring_window
        
        if visa_status == "F1 - OPT":
            if days_remaining < 90:
                timeline["risk_level"] = "HIGH"
                timeline["needs_immediate_action"] = True
                timeline["recommended_action"] = "Immediate action required - OPT expiring soon"
        elif visa_status == "STEM OPT":
            if days_remaining < 180:
                timeline["risk_level"] = "MEDIUM"
                timeline["recommended_action"] = "Start preparing for H1B application"
        elif visa_status == "H1B":
            if days_remaining < 365:
                timeline["risk_level"] = "MEDIUM"
                timeline["recommended_action"] = "Consider H1B extension preparation"
    
    return timeline

def analyze_h1b_eligibility(
    transcript_text: str,
    jd_analysis: Dict,
    visa_status: str,
    is_stem_degree: bool,
    visa_start_date: datetime,
    visa_end_date: Optional[datetime],
    criminal_history: Dict
) -> Dict:
    """Enhanced H1B eligibility analysis considering additional factors"""
    
    # Calculate visa timeline
    timeline = calculate_visa_timeline(visa_status, visa_start_date, visa_end_date)
    
    # Extract key information from JD analysis
    match_percentage = jd_analysis.get('match_percentage', 0)
    matching_skills = jd_analysis.get('matching_skills', [])
    missing_requirements = jd_analysis.get('missing_requirements', [])
    required_education = jd_analysis.get('required_education', '')
    industry_alignment = jd_analysis.get('industry_alignment', '')
    
    prompt = """Please analyze the H1B visa eligibility based on the provided information. 
    Consider both the candidate's qualifications and the job match analysis.
    Respond ONLY with a JSON object containing the analysis results. 

    Job Match Analysis Summary:
    - Overall Match: {}%
    - Matching Skills: {}
    - Missing Requirements: {}
    - Required Education: {}
    - Industry Alignment: {}

    Consider these factors in your analysis:
    1. If match percentage is below 65%, this indicates higher risk for H1B approval
    2. Missing requirements could affect specialty occupation qualification
    3. Education alignment is crucial for H1B qualification
    4. Industry alignment affects specialty occupation determination

    Return a JSON object with the following structure:
    {{
        "eligibility_factors": {{
            "education_qualification": {{
                "score": <number 0-100>,
                "analysis": <string explaining education match considering both transcript and job requirements>,
                "risks": [<string>]
            }},
            "job_match_assessment": {{
                "score": {},
                "critical_gaps": [<string>],
                "impact_on_h1b": <string explaining how job match affects H1B chances>
            }},
            "visa_timing": {{
                "score": <number 0-100>,
                "analysis": <string>,
                "key_dates": {{
                    "h1b_window_start": <string date>,
                    "h1b_window_end": <string date>
                }},
                "risks": [<string>]
            }},
            "background_check": {{
                "status": <string>,
                "concerns": [<string>],
                "impact": <string>
            }}
        }},
        "specialty_occupation_assessment": {{
            "qualifies": <boolean>,
            "supporting_factors": [<string>],
            "risk_factors": [<string>],
            "job_skill_alignment": <string explaining how matching/missing skills affect specialty occupation qualification>
        }},
        "stem_qualification": {{
            "eligible_for_stem_opt": <boolean>,
            "benefits": [<string>],
            "recommendations": [<string>]
        }},
        "timeline_assessment": {{
            "immediate_actions": [<string>],
            "upcoming_deadlines": {{
                "next_h1b_filing": <string date>,
                "current_status_expiry": <string date>
            }},
            "contingency_plans": [<string>]
        }},
        "overall_assessment": {{
            "eligible": <boolean>,
            "confidence_score": <number 0-100, heavily weighted by job match percentage>,
            "risk_level": <string: "LOW"|"MEDIUM"|"HIGH">,
            "key_concerns": [<string>],
            "recommendations": [<string>]
        }}
    }}

    Input Information:
    """.format(
        match_percentage,
        ", ".join(matching_skills),
        ", ".join(missing_requirements),
        required_education,
        industry_alignment,
        match_percentage
    )
    
    # Add remaining input information
    prompt += """
    Current Visa Status: """ + visa_status + """
    STEM Degree: """ + ("Yes" if is_stem_degree else "No") + """
    Visa Timeline: """ + json.dumps(timeline) + """
    Criminal History: """ + json.dumps(criminal_history) + """
    Transcript: """ + transcript_text + """
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are an expert H1B visa analyst. 
                Consider both candidate qualifications and job match for H1B eligibility.
                A strong job match (>65%) significantly improves H1B chances.
                Missing job requirements or poor skill match increases H1B denial risk.
                A person with criminal history is mostly likely not going to get H1B. many more supporting would be required to assess the crime.
                Always respond with ONLY a valid JSON object matching the specified structure."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        json_str = response.choices[0].message.content.strip()
        json_str = json_str.replace('```json', '').replace('```', '').strip()
        
        return json.loads(json_str)
        
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON response: {str(e)}")
        st.error("Raw response: " + response.choices[0].message.content)
        return None
    except Exception as e:
        st.error(f"Error in H1B eligibility analysis: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="H1B Eligibility Assessment", layout="wide")
    st.title("H1B Eligibility Assessment System")
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'jd_analysis' not in st.session_state:
        st.session_state.jd_analysis = None
    if 'jd_text' not in st.session_state:
        st.session_state.jd_text = None
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = None
    
    # Step 1: Resume-JD Match Analysis
    if st.session_state.step == 1:
        st.header("Step 1: Resume-Job Description Match Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Job Description")
            jd_file = st.file_uploader("Upload Job Description", type=['pdf', 'docx', 'txt'], key='jd_upload')
            if jd_file:
                jd_text = read_file_content(jd_file)
                st.session_state.jd_text = jd_text
                if jd_text and st.checkbox("Show JD Content"):
                    st.text_area("JD Content", jd_text, height=200)
        
        with col2:
            st.subheader("Resume")
            resume_file = st.file_uploader("Upload Resume", type=['pdf', 'docx', 'txt'], key='resume_upload')
            if resume_file:
                resume_text = read_file_content(resume_file)
                st.session_state.resume_text = resume_text
                if resume_text and st.checkbox("Show Resume Content"):
                    st.text_area("Resume Content", resume_text, height=200)
        
        if st.session_state.jd_text and st.session_state.resume_text:
            if st.button("Analyze Resume-JD Match"):
                with st.spinner("Analyzing resume-job match..."):
                    match_analysis = analyze_resume_jd_match(
                        st.session_state.resume_text, 
                        st.session_state.jd_text
                    )
                    
                    if match_analysis:
                        st.session_state.jd_analysis = match_analysis
                        
                        # Display match results
                        st.subheader("Match Analysis Results")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Overall Match", f"{match_analysis['match_percentage']}%")
                            st.write("### Matching Skills")
                            for skill in match_analysis['matching_skills']:
                                st.write(f"✓ {skill}")
                        
                        with col2:
                            st.write("### Missing Requirements")
                            for req in match_analysis['missing_requirements']:
                                st.write(f"✗ {req}")
                        
                        st.write(f"**Required Education:** {match_analysis['required_education']}")
                        st.write(f"**Industry Alignment:** {match_analysis['industry_alignment']}")
                        
                        # Proceed to next step if match is acceptable
                        if match_analysis['match_percentage'] >= 50:
                            st.success("Match analysis complete! You can proceed to H1B eligibility assessment.")
                            if st.button("Proceed to H1B Assessment"):
                                st.session_state.step = 2
                                st.rerun()
                        else:
                            st.warning("The resume-job match is below 50%. Consider improving the match before proceeding with H1B assessment.")
    
    # Step 2: H1B Eligibility Assessment
    if True:
        st.header("Step 2: H1B Eligibility Assessment")
        
        # Show summary of previous analysis
        if st.session_state.jd_analysis:
            st.subheader("Resume-JD Match Summary")
            st.metric("Match Percentage", f"{st.session_state.jd_analysis['match_percentage']}%")
        
        # Additional H1B qualification information
        col1, col2 = st.columns(2)
        
        with col1:
            visa_status = st.selectbox(
                "Current Visa Status",
                ["F1", "F1 - OPT", "STEM OPT", "H1B"],
                help="Select your current visa status"
            )
            
            is_stem_degree = st.radio(
                "Is your degree STEM accredited?",
                ["Yes", "No"],
                help="STEM degree qualification affects STEM OPT eligibility"
            )
            
        with col2:
            if visa_status != "F1":
                visa_start = st.date_input(
                    "Visa Start Date",
                    help="When did your current visa status begin?"
                )
                visa_end = st.date_input(
                    "Visa End Date",
                    help="When does your current visa status expire?"
                )
            
            has_criminal_history = st.radio(
                "Do you have any criminal history?",
                ["No", "Yes"]
            )
            
            if has_criminal_history == "Yes":
                criminal_details = st.text_area(
                    "Please provide details of criminal history",
                    help="This information is important for visa eligibility assessment"
                )
        
        # Transcript upload
        st.subheader("Academic Transcript")
        transcript_file = st.file_uploader("Upload Transcript", type=['pdf', 'docx', 'txt'])
        
        if transcript_file and st.session_state.jd_analysis:
            transcript_text = read_file_content(transcript_file)
            
            if st.button("Assess H1B Eligibility"):
                with st.spinner("Analyzing H1B eligibility..."):
                    # Prepare criminal history data
                    criminal_history = {
                        "has_history": has_criminal_history == "Yes",
                        "details": criminal_details if has_criminal_history == "Yes" else None
                    }
                    
                    # Convert dates to datetime
                    start_date = datetime.combine(visa_start, datetime.min.time()) if visa_status != "F1" else None
                    end_date = datetime.combine(visa_end, datetime.min.time()) if visa_status != "F1" else None
                    
                    eligibility_analysis = analyze_h1b_eligibility(
                        transcript_text,
                        st.session_state.jd_analysis,
                        visa_status,
                        is_stem_degree == "Yes",
                        start_date,
                        end_date,
                        criminal_history
                    )
                    
                    if eligibility_analysis:
                        # Create tabs for organized display
                        tabs = st.tabs([
                            "Overall Assessment",
                            "Timeline Analysis",
                            "Education & Background",
                            "Action Items"
                        ])
                        
                        with tabs[0]:
                            # Overall Assessment
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(
                                    "H1B Eligibility Confidence",
                                    f"{eligibility_analysis['overall_assessment']['confidence_score']}%"
                                )
                                
                                risk_color = {
                                    "LOW": "green",
                                    "MEDIUM": "yellow",
                                    "HIGH": "red"
                                }.get(eligibility_analysis['overall_assessment']['risk_level'], "gray")
                                
                                st.markdown(f"""
                                    <div style='background-color: {risk_color}; padding: 10px; border-radius: 5px;'>
                                        Risk Level: {eligibility_analysis['overall_assessment']['risk_level']}
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                if eligibility_analysis['overall_assessment']['eligible']:
                                    st.success("Candidate appears eligible for H1B visa")
                                else:
                                    st.error("Candidate may not meet H1B requirements")
                                
                                st.write("### Key Concerns")
                                for concern in eligibility_analysis['overall_assessment']['key_concerns']:
                                    st.warning(f"⚠️ {concern}")
                        
                        with tabs[1]:
                            # Timeline Analysis
                            st.write("### Visa Timeline")
                            timeline = eligibility_analysis['timeline_assessment']
                            
                            for deadline, date in timeline['upcoming_deadlines'].items():
                                st.write(f"**{deadline}:** {date}")
                            
                            st.write("### Immediate Actions Required")
                            for action in timeline['immediate_actions']:
                                st.write(f"• {action}")
                            
                            st.write("### Contingency Plans")
                            for plan in timeline['contingency_plans']:
                                st.write(f"📋 {plan}")
                        
                        with tabs[2]:
                            # Education & Background
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("### Education Qualification")
                                st.metric(
                                    "Education Match Score",
                                    f"{eligibility_analysis['eligibility_factors']['education_qualification']['score']}%"
                                )
                                st.write(eligibility_analysis['eligibility_factors']['education_qualification']['analysis'])
                            
                            with col2:
                                st.write("### STEM Qualification")
                                if eligibility_analysis['stem_qualification']['eligible_for_stem_opt']:
                                    st.success("Eligible for STEM OPT")
                                else:
                                    st.error("Not eligible for STEM OPT")
                                
                                st.write("#### Benefits")
                                for benefit in eligibility_analysis['stem_qualification']['benefits']:
                                    st.write(f"✓ {benefit}")
                        
                        with tabs[3]:
                            # Action Items
                            st.write("### Recommendations")
                            for rec in eligibility_analysis['overall_assessment']['recommendations']:
                                st.write(f"• {rec}")
                            
                            if eligibility_analysis['eligibility_factors']['visa_timing']['risks']:
                                st.write("### Timeline Risks")
                                for risk in eligibility_analysis['eligibility_factors']['visa_timing']['risks']:
                                    st.error(f"⚠️ {risk}")
        
        # Option to go back
        if st.button("Back to Resume-JD Analysis"):
            st.session_state.step = 1
            st.rerun()

if __name__ == "__main__":
    main()