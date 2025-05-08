Video Demonstration: 


https://github.com/user-attachments/assets/9c4b8913-ffb0-43a5-a19f-21a4ebba2c0b


# AI Stock Analysis Tool

This tool provides AI-powered stock analysis, combining technical analysis, news sentiment analysis, and AI-generated insights using the Groq API.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Rian-D/ai-stock-analysis.git
   cd ai-stock-analysis
   ```

2. **Create and Activate a Virtual Environment (Recommended)**
   ```bash
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   GROQ_API_KEY=your_groq_api_key
   NEWS_API_KEY=your_news_api_key
   ```
   
   You'll need to:
   - Get a Groq API key from [Groq's website](https://console.groq.com) (free) 
   - Get a News API key from [NewsAPI's website](https://newsapi.org) (free)

## Running the Application

1. **Start the Streamlit Application**
   ```bash
   streamlit run app.py
   ```

2. **Access the Application**
   - The application will open in your default web browser
   - If it doesn't open automatically, navigate to `http://localhost:8501`

## Features

- Real-time stock data analysis
- News sentiment analysis
- AI-powered insights using Groq
- Interactive charts and visualizations
- Historical data analysis

## Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are correctly installed
2. Verify your API keys are correctly set in the `.env` file
3. Check that you're using Python 3.8 or higher
4. Make sure you're in the correct directory when running the application

## Contributing

Feel free to submit issues and enhancement requests! 




