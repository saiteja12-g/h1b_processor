# H1B Pulse: Visa Eligibility Screening System for Recruiters

A comprehensive Streamlit application that helps recruiters efficiently screen candidates based on H1B visa eligibility factors. The system analyzes the match between resumes and job descriptions, evaluates academic qualifications, and provides detailed visa timeline assessments to identify suitable candidates.

![H1B Assessment System](https://img.shields.io/badge/H1B-Assessment-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=OpenAI&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=Python&logoColor=white)

## 🚀 Features

- **Resume-Job Description Match Analysis**: Upload candidate resumes and job descriptions to get a detailed analysis of the match percentage, matching skills, and missing requirements.
- **H1B Eligibility Screening**: Comprehensive evaluation of candidate H1B visa eligibility based on job match, education qualifications, and visa status.
- **Visa Timeline Assessment**: Get insights into key dates, immediate actions required, and potential risks for each candidate's visa journey.
- **Smart Document Processing**: Support for multiple document formats (PDF, DOCX, TXT) with intelligent text extraction.
- **AI-Powered Analysis**: Leveraging OpenAI's GPT models for accurate and detailed candidate assessments.
- **Risk Level Identification**: Clear visual indicators of visa risk levels to help prioritize candidates.

## 📋 Prerequisites

- Python 3.7+
- Streamlit account (for secrets management)
- OpenAI API key

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/h1b-pulse.git
cd h1b-pulse
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# OR
source venv/bin/activate      # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your OpenAI API key in Streamlit secrets:
   - Create a `.streamlit` directory
   - Create a file named `secrets.toml` inside that directory
   - Add your OpenAI API key:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```

## 🚀 Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. In your browser:
   - Upload the candidate's resume and the job description
   - Input the candidate's visa status, education information, and other relevant details
   - Review the comprehensive analysis of their H1B eligibility and potential risks
   - Use the match percentage and risk assessment to make informed hiring decisions

## 🧠 How It Works

1. **Document Analysis**: The system extracts text from uploaded candidate documents using PyPDF2 and docx2txt.
2. **Resume-JD Matching**: OpenAI's GPT models analyze the match between the candidate's resume and the job description.
3. **Eligibility Assessment**: The system evaluates multiple factors to determine H1B sponsorship viability:
   - Job match percentage and skills alignment
   - Academic qualifications and degree relevance
   - Current visa status and timeline constraints
   - STEM degree qualification for extended options
   - Criminal history assessment (if applicable)
4. **Risk Assessment**: Calculation of risk levels (LOW, MEDIUM, HIGH) based on comprehensive analysis.
5. **Results Visualization**: Clear visualization of results with actionable insights for recruiters.

## 🎥 Demo Video

[![H1B Pulse Demo](https://img.youtube.com/vi/YOUTUBE_VIDEO_ID/0.jpg)](https://youtu.be/QnGMddZrj-k)

*Click the image above to watch the demo video of H1B Pulse in action, showcasing the key features and workflow.*

## 🛠️ Technologies Used

- **Streamlit**: For the web interface
- **OpenAI API**: For intelligent analysis of documents and eligibility assessment
- **ChromaDB**: For persistent data storage
- **PyPDF2 & docx2txt**: For document processing
- **Python**: Core programming language

## 🔄 Data Flow

```
User uploads documents → Text extraction → AI analysis → Eligibility calculation → Visual results
```

## 🧩 Project Structure

```
h1b-pulse/
├── .streamlit/            # Streamlit configuration and secrets
├── chroma_db/             # ChromaDB persistence storage
├── app.py                 # Main application file
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## 🚫 Limitations

- The application provides an assessment based on available information and should not be considered legal advice.
- Actual H1B eligibility depends on USCIS evaluation and may be affected by policy changes.
- Document parsing may not be perfect for all document formats or layouts.

## 🔜 Future Improvements

- Add support for more document formats and resume parsing optimization
- Implement batch processing for screening multiple candidates simultaneously
- Develop a comparison tool to rank candidates based on visa eligibility
- Create a dashboard for tracking candidate pipelines and visa statuses
- Add historical data analysis for better prediction of visa approval chances
- Include immigration attorney recommendations based on complex cases
- Integrate with ATS (Applicant Tracking Systems) for seamless workflow

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [OpenAI](https://openai.com/) for providing the GPT API
- [Streamlit](https://streamlit.io/) for the amazing web framework

---

*Note: This application is for informational and hiring decision support purposes only and does not constitute legal advice. Recruiters should consult with qualified immigration attorneys for professional guidance on complex visa matters. The tool is designed to support initial screening and should not replace comprehensive immigration evaluation for final hiring decisions.*