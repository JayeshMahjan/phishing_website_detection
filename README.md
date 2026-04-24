# 🔐 PhishGuard AI - Phishing Website Detector

A professional-grade phishing website detection application using Machine Learning (Random Forest), Flask, and modern web technologies.

## 📋 Project Overview

This application uses a **Random Forest Classifier** trained on 20,000 balanced URLs to detect phishing websites in real-time. The system extracts 7 key security features from URLs and provides instant analysis with confidence scores.

---

## 🎯 Features

- ✅ **AI-Powered Detection** - Random Forest ML model with 95%+ accuracy
- ⚡ **Real-Time Analysis** - Instant predictions in milliseconds
- 🤖 **OpenAI Chatbot** - AI-powered security assistant for questions
- 🎨 **Modern UI** - Professional dark mode interface with animations
- 📱 **Fully Responsive** - Works on desktop, tablet, and mobile
- 🔒 **Privacy-First** - No data storage or user tracking
- 📊 **Detailed Reports** - Feature breakdown and confidence scores

---

## 📁 Project Structure

```
phishing_detector/
│
├── model/
│   └── phishing_model.pkl          # Trained ML model (generated)
│
├── static/
│   ├── css/
│   │   └── style.css               # Modern UI styles
│   └── js/
│       └── main.js                 # Frontend JavaScript
│
├── templates/
│   └── index.html                  # Main web interface
│
├── train_model.py                  # ML training script
├── app.py                          # Flask backend
├── requirements.txt                # Python dependencies
├── phishing_dataset.csv            # Training dataset (20K rows)
└── README.md                       # Documentation
```

---

## 🚀 Quick Start

### 1️⃣ Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### 2️⃣ Installation

```bash
# Navigate to project directory
cd "phishing web detect"

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Train Model

The dataset is already included. Train the model:

```bash
python train_model.py
```

**Expected Output:**
- Training progress with accuracy metrics
- Confusion matrix
- Feature importance analysis
- Saved model: `model/phishing_model.pkl`


### 5️⃣ Run Application

```bash
python app.py
```

## 🧠 Why Random Forest?

**Random Forest** was chosen for this phishing detection system because:

1. **Non-Linear Patterns** - URLs contain complex, non-linear patterns that Random Forest handles excellently
2. **Overfitting Resistance** - Ensemble of decision trees prevents overfitting
3. **No Scaling Required** - Works with raw feature values (no normalization needed)
4. **Feature Importance** - Provides insights into which features matter most
5. **Fast Predictions** - Critical for real-time web applications
6. **Robust to Noise** - Handles imperfect/inconsistent data well
7. **High Accuracy** - Consistently achieves 95%+ accuracy on this dataset

---

## 🎨 UI Features

### Design Highlights
- **Dark Mode Interface** - Easy on the eyes, modern aesthetic
- **Gradient Animations** - Smooth background effects
- **Responsive Design** - Mobile-first approach
- **Loading States** - Visual feedback during analysis
- **Color-Coded Results** - Green (safe) / Red (phishing)
- **Confidence Bars** - Animated progress indicators
- **Feature Breakdown** - Detailed security analysis

### Technology Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Flask (Python)
- **ML:** scikit-learn (Random Forest)
- **Fonts:** Inter (Google Fonts)

---

## 🔍 How It Works

### Feature Extraction

The system analyzes 7 security features from any URL:

1. **isIp** - Checks if URL uses IP address instead of domain
   - Phishing sites often use IPs to avoid DNS tracking
   
2. **urlLen** - Length of the domain (not full URL)
   - Matches dataset format where urlLen = domain length
   
3. **is@** - Presence of @ symbol
   - Can hide real domain (e.g., `http://google.com@evil.com`)
   
4. **isredirect** - Multiple slashes (//) in path/query (not protocol)
   - Indicates potential redirection attacks in the URL path
   
5. **haveDash** - Dash (-) in domain name
   - Used for brand impersonation (e.g., `paypal-secure.com`)
   
6. **domainLen** - Length of domain
   - Legitimate domains are typically shorter
   
7. **nosOfSubdomain** - Number of subdomains
   - Multiple subdomains can indicate phishing

### Prediction Flow

```
User enters URL → Feature Extraction → ML Model → Prediction → Display Result
```

---

## 📊 API Endpoints

### `GET /`
Returns the main web interface

### `POST /predict`
Analyzes a URL for phishing

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "status": "success",
  "url": "https://example.com",
  "prediction": "safe",
  "confidence": 98.5,
  "features": {
    "isIp": 0,
    "urlLen": 23,
    "is@": 0,
    "isredirect": 0,
    "haveDash": 0,
    "domainLen": 11,
    "nosOfSubdomain": 1
  },
  "details": {
    "legitimacy_score": 98.5,
    "phishing_score": 1.5
  }
}
```

### `POST /chat` (OpenAI-Powered)
Chat with the PhishGuard AI Assistant about security and phishing

**Request:**
```json
{
  "message": "How can I identify phishing websites?"
}
```

**Response:**
```json
{
  "status": "success",
  "response": "Here are some tips to identify phishing websites..."
}
```

**Error Response (if API key not configured):**
```json
{
  "status": "error",
  "message": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
}
```

### `GET /health`
Health check endpoint

---

## 🛠️ Development

### Running in Debug Mode

The Flask app runs in debug mode by default:
- Auto-reload on code changes
- Detailed error messages
- Interactive debugger

### Environment Variables (Optional)

Create `.env` file:
```env
FLASK_ENV=development
FLASK_DEBUG=1
```

---

## 📱 Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## 🔒 Security Notes

- URLs are analyzed locally, not stored
- No user data is collected or tracked
- Model runs server-side for security
- Input validation prevents XSS attacks

---

## 🎓 Educational Purpose

This project demonstrates:
- End-to-end ML pipeline (training → deployment)
- RESTful API design with Flask
- Modern frontend development practices
- Real-world cybersecurity application
- Production-ready code structure

---

## 📈 Model Performance

**Typical Results:**
- Accuracy: 95-97%
- Precision: 94-96%
- Recall: 93-95%
- F1-Score: 94-96%

*Results vary based on your specific dataset*

---

## 🤝 Contributing

This is a learning project. Feel free to:
- Add more features
- Improve the UI
- Optimize the model
- Add more ML algorithms for comparison

---

## 📝 Dataset Notes

If you don't have a dataset, you can:
1. Search for "phishing URL dataset" on Kaggle
2. Use UCI Machine Learning Repository datasets
3. Combine multiple public datasets

**Popular Sources:**
- Kaggle: "Phishing Website Dataset"
- UCI: "Phishing Websites Data Set"
- PhishTank: Real-time phishing database

---

## 🚨 Troubleshooting

### Model file not found
```bash
# Ensure you've trained the model first
python train_model.py
```

### Module not found errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Port already in use
Edit `app.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
to a different port (e.g., 5001)

---

