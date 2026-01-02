# Data Analysis Agent Frontend

A modern web chatbot interface for interacting with your data analysis agent. Upload files, ask questions, get visualizations, and download reports.

## Features

- **Chat Interface**: Real-time conversation with your data analysis agent
- **File Upload**: Drag-and-drop or click to upload CSV, Excel, TXT, and JSON files
- **Data Visualization**: Automatic chart and graph generation based on analysis
- **Report Generation**: Download PDF reports with insights and visualizations
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Loading States**: Real-time feedback while processing requests
- **Chat History**: View all previous conversations and results

## Quick Start Guide

### 1. Backend Setup (Python)

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create a `.env` file in the `backend` directory and add your Groq API key:
    ```
    GROQ_API_KEY=your_api_key_here
    ```
3.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
4.  Start the backend server:
    ```bash
    python server.py
    ```
    The backend will run on `http://localhost:8000`.

### 2. Frontend Setup (React)

1.  Open a new terminal and navigate to the project root (where `package.json` is):
    ```bash
    cd ..
    ```
    (or just stay in the root if you haven't moved)
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the frontend development server:
    ```bash
    npm run dev
    ```
    The frontend will run on `http://localhost:5173`.

### 3. Usage

1.  Open your browser and go to `http://localhost:5173`.
2.  Upload a data file (CSV, Excel, etc.) using the upload button.
3.  Ask questions about your data!

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Configure the API URL in `.env`:
```
VITE_API_URL=http://localhost:8000
```
Replace with your actual backend API URL.

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Production Build

Build for production:
```bash
npm run build
```

Preview the build:
```bash
npm run preview
```

## Backend Integration

The frontend expects your backend to expose the following endpoints:

### 1. Analyze with File Upload
**POST** `/analyze`
- **Request**: Form data with file and prompt
- **Response**: JSON with analysis response, image paths, and optional PDF path

```typescript
{
  response: string,        // Analysis text response
  image_paths?: string[],  // Array of image file paths
  pdf_path?: string        // Path to generated PDF report
}
```

### 2. Analyze with Existing Data
**POST** `/analyze`
- **Request**: JSON with prompt
- **Response**: Same as above

```json
{
  "prompt": "Your question here"
}
```

### 3. Download Report
**GET** `/download/{filename}`
- **Response**: Binary PDF file

## File Structure

```
src/
├── components/
│   └── Chat.tsx              # Main chat component
├── services/
│   └── api.ts                # API integration layer
├── styles/
│   └── Chat.css              # Component styles
├── App.tsx                    # Root component
└── index.css                  # Global styles
```

## Environment Variables

- `VITE_API_URL`: Backend API base URL (default: http://localhost:8000)

## Features Explained

### File Upload
- Click the upload button or drag files into the zone
- Supported formats: CSV, Excel (.xlsx, .xls), TXT, JSON
- File preview shows before sending
- Remove uploaded file with the X button

### Chat Interface
- Type questions about your data
- Receive instant analysis responses
- Images are embedded in chat history
- Download reports directly from chat

### Loading States
- Animated spinner while processing
- Disabled input while waiting for response
- Real-time timestamp on all messages

## Customization

### Styling

Edit `src/styles/Chat.css` to customize:
- Color scheme (modify CSS variables in `:root`)
- Layout and spacing
- Animations and transitions
- Responsive breakpoints

### Component

Edit `src/components/Chat.tsx` to:
- Modify message format
- Add new functionality
- Change file upload behavior
- Customize error handling

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Optimized for large file uploads
- Lazy loading of images
- Efficient re-rendering with React
- Smooth animations with CSS
- Responsive scrolling

## Troubleshooting

### "Error: Analysis request failed"
- Check that your backend API is running
- Verify `VITE_API_URL` points to the correct address
- Check browser console for detailed errors

### Files not uploading
- Verify file format is supported (CSV, Excel, TXT, JSON)
- Check file size isn't too large
- Ensure backend `/analyze` endpoint is accessible

### Images not displaying
- Check that backend returns correct image paths
- Verify images exist at the returned paths
- Check browser console for CORS errors

## Technical Stack

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **CSS3**: Styling and animations

## API Response Format

Your backend should return responses in this format:

```json
{
  "response": "Analysis findings...",
  "image_paths": [
    "/path/to/chart1.png",
    "/path/to/chart2.png"
  ],
  "pdf_path": "/path/to/report.pdf"
}
```

## License

MIT
