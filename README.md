# Clinical Protocol Information Extractor

A full-stack application that extracts key information from clinical trial protocols and generates structured documents. Built with Django (backend) and Vue.js (frontend).

## Features

- **Document Processing**: Upload PDF or DOCX clinical trial protocols
- **AI-Powered Extraction**: Uses OpenAI GPT to extract key sections:
  - Purpose of the Study
  - Study Procedures
  - Risks
  - Benefits
- **Structured Output**: Generates clean DOCX documents with extracted information
- **Fallback System**: Graceful handling of API failures with saved responses
- **Environment Configuration**: Production-ready config management

## Tech Stack

### Backend
- **Django 4.2+** - Web framework
- **Django REST Framework** - API endpoints
- **OpenAI API** - AI-powered text extraction
- **python-docx** - DOCX document generation
- **PyMuPDF** - PDF text extraction

### Frontend
- **Vue.js 3** - Frontend framework
- **Vite** - Build tool
- **Axios** - HTTP client

## Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key

## Installation & Setup

### Quick Setup 

```bash
# Clone the repository
git clone <repository-url>
cd clinical-icf-generator

# Run the automated setup script
chmod +x setup.sh
./setup.sh

# Edit the .env file with your API keys
nano backend/.env
```

### Manual Setup

If you prefer to set up manually or the script doesn't work:

#### 1. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your-openai-api-key-here"

# OR create a .env file in the backend directory:
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env

# Run migrations
python manage.py migrate

# Start Django server
python manage.py runserver
```

The backend will be available at `http://127.0.0.1:8000`

#### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

**Frontend Tech Stack:**
- Vue.js 3 with Composition API
- Vite for build tooling
- Axios for API communication
- Environment-based configuration

#### 3. Configuration

Edit `frontend/config.js` to configure API endpoints for different environments:

```javascript
const config = {
  development: {
    API_BASE_URL: 'http://127.0.0.1:8000',
    // ... other settings
  },
  production: {
    API_BASE_URL: 'https://your-production-api.com',
    // ... other settings
  }
}
```

## Usage

1. **Upload Document**: Select a PDF or DOCX clinical trial protocol
2. **Extract Information**: Click "Upload & Extract Information"
3. **Review Results**: View extracted sections in the UI
4. **Download**: Get a formatted DOCX document with the information

## API Endpoints

### `POST /api/generate_icf/`
Upload and process a clinical trial protocol.

**Request:**
- `file`: PDF or DOCX file (multipart/form-data)

**Response:**
```json
{
  "download_url": "/api/download_icf/?file=icf_123456.docx",
  "generated_text": "JSON or markdown text",
  "sections": {
    "Purpose of the Study": "...",
    "Study Procedures": "...",
    "Risks": "...",
    "Benefits": "..."
  },
  "log": [...]
}
```

### `GET /api/download_icf/?file=<filename>`
Download the generated DOCX document.

## Project Structure

```
clinical-icf-generator/
├── backend/
│   ├── docparser/          # Django project settings
│   ├── documents/         # Main app
│   │   ├── views.py       # API endpoints
│   │   ├── utils.py       # PDF/DOCX extraction
│   │   └── templates/     # ICF template (unused)
│   └── manage.py
├── frontend/
│   ├── src/
│   │   └── App.vue        # Main Vue component
│   ├── config.js          # Environment configuration
│   └── package.json
├── requirements.txt       # Python dependencies
└── README.md
```

## Error Handling

The application includes robust error handling:

- **API Failures**: Falls back to saved response data
- **File Processing**: Handles corrupted or unsupported files
- **JSON Parsing**: Graceful fallback to markdown parsing
- **Network Issues**: User-friendly error messages

## Development

### Building for Production

```bash
# Frontend build
cd frontend
npm run build

# Backend deployment
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
```

## Environment Variables

### Backend
Create a `.env` file in the `backend/` directory:

```bash
# Copy the example file
cp backend/env.example backend/.env

# Edit with your actual values
# backend/.env
OPENAI_API_KEY=your-openai-api-key-here
DEBUG=True
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key (get from https://platform.openai.com/api-keys)
- `DEBUG`: Set to False in production

### Frontend
Configure in `frontend/config.js`:
- `API_BASE_URL`: Backend API URL
- `APP_NAME`: Application name
- `DEBUG`: Debug mode flag

**Frontend Features:**
- File upload for PDF/DOCX protocols
- Real-time extraction status
- Structured section display
- DOCX download functionality
- Error handling with fallback
- Responsive design


### Technical Decisions

- **Django REST Framework**: For robust API development
- **Vue.js 3**: Modern reactive frontend framework
- **python-docx**: For document generation without complex templates
- **Environment-based config**: For easy deployment across environments

## Setup Script

The project includes an automated setup script (`setup.sh`) that handles the initial configuration:

```bash
# Make executable and run
chmod +x setup.sh
./setup.sh
```

**After running setup.sh:**
1. Edit `backend/.env` with your OpenAI API key (only required variable)
2. Start backend: `source venv/bin/activate && python manage.py runserver`
3. Start frontend: `cd frontend && npm run dev`

