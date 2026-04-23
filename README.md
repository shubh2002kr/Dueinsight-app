🚀 DueInsight — DD Workstation

DueInsight is an advanced Due Diligence & Litigation Research Dashboard built using Streamlit.
It helps users quickly analyze people, companies, legal records, news, and digital footprint from multiple sources in one place.

🌟 Features
🔍 Profile Research
Google-based deep search (Biography, Contacts, LinkedIn, etc.)
⚖️ Litigation & Court Records
Indian Kanoon integration
Quick access to eCourts, High Court, Supreme Court
📰 Media Coverage
Real-time news via Google News RSS
🌐 Digital Footprint
LinkedIn, Twitter (X), Instagram, YouTube search links
🎨 Modern UI
Custom animations
Dark theme dashboard
Interactive cards & layout
🛠️ Tech Stack
Frontend/UI: Streamlit + Custom HTML/CSS
Backend: Python
Libraries:
streamlit
requests
beautifulsoup4
lxml
📂 Project Structure
dueinsight-app/
│── app.py
│── requirements.txt
│── README.md
⚙️ Installation & Run Locally
1️⃣ Clone the Repository
git clone https://github.com/your-username/dueinsight-app.git
cd dueinsight-app
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Run the App
streamlit run app.py

👉 App will open in browser at:

http://localhost:8501
🚀 Deployment

This app is deployed using Streamlit Community Cloud.

Steps:
Push code to GitHub
Go to Streamlit Cloud
Click Deploy new app
Select repo and app.py
Click Deploy
⚠️ Notes
Requires internet connection (uses live scraping)
Data sources:
Google News RSS
Indian Kanoon
Some requests may fail due to rate limits or website restrictions
📌 Future Improvements
🔐 User authentication (login system)
🗄️ Database integration
📊 Advanced analytics dashboard
⚡ Performance optimization (caching)
👨‍💻 Author

Shubh Kumar
Computer Science Engineer

📄 License

This project is for educational and research purposes.
