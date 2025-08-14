# TreeCare Backend

A Django REST API backend for tree disease detection using YOLO (You Only Look Once) machine learning model.

## Features

- **Image Upload**: Upload tree images for analysis
- **AI Analysis**: Automatic species and disease detection using YOLO model
- **REST API**: Clean REST endpoints for integration
- **Media Handling**: Proper file upload and storage management

## API Endpoints

### Upload Image
- **POST** `/tree/upload/`
- **Body**: `image` (multipart/form-data)
- **Response**: Tree analysis results with species and disease detection

### Get Tree Result
- **GET** `/tree/result/<tree_id>/`
- **Response**: Tree analysis results by ID

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 3. Run Development Server
```bash
python3 manage.py runserver
```

## Project Structure

```
treecare/
├── best.pt                 # YOLO model file
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── treecare/             # Django project settings
│   ├── settings.py       # Project configuration
│   ├── urls.py          # Main URL routing
│   └── wsgi.py          # WSGI configuration
├── treecare_app/         # Main application
│   ├── models.py         # Database models
│   ├── views.py          # API views
│   ├── serializer.py     # DRF serializers
│   └── urls.py          # App URL routing
├── media/                # User uploaded files
└── tree_images/          # Tree image storage
```

## Recent Fixes Applied

### 1. **Hardcoded Path Issue** ✅
- **Problem**: YOLO model path was hardcoded with absolute path
- **Solution**: Used relative path from Django BASE_DIR setting
- **File**: `treecare_app/views.py`

### 2. **Unicode Characters** ✅
- **Problem**: Invisible unicode characters in response dictionaries
- **Solution**: Removed unicode characters from `tree.id` references
- **File**: `treecare_app/views.py`

### 3. **Media Configuration** ✅
- **Problem**: Missing media file handling configuration
- **Solution**: Added MEDIA_URL and MEDIA_ROOT to settings
- **File**: `treecare/settings.py`

### 4. **URL Configuration** ✅
- **Problem**: Media files not served in development
- **Solution**: Added media URL patterns for development
- **File**: `treecare/urls.py`

### 5. **Error Handling** ✅
- **Problem**: Insufficient error handling in API views
- **Solution**: Added comprehensive try-catch blocks and error responses
- **File**: `treecare_app/views.py`

### 6. **Model Field Usage** ✅
- **Problem**: Result field not being utilized properly
- **Solution**: Updated views to properly set and return Result field
- **File**: `treecare_app/views.py`

## Model Information

The YOLO model supports detection of:
- **68 different classes** including various tree species and diseases
- **Species**: Apple, Banana, Bell Pepper, Cassava, Cherry, Coffee, Corn, Grape, Peach, Potato, Rice, Strawberry, Sugarcane, Tomato
- **Diseases**: Various leaf spots, blights, rusts, and other plant diseases

## Development Notes

- The project uses Django 5.1.9 and Django REST Framework
- YOLO model is loaded once at startup for performance
- Media files are served statically in development mode
- Database uses SQLite for development (can be changed for production)

## Production Considerations

- Change `DEBUG = False` in settings
- Use proper database (PostgreSQL, MySQL)
- Configure static file serving (nginx, CDN)
- Set up proper media file storage (AWS S3, etc.)
- Use environment variables for sensitive settings
