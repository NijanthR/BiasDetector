# Frontend Setup & Configuration

Complete frontend setup guide for the Multi-Agent Dataset Analysis Platform.

## Prerequisites

- Node.js 16.0.0 or higher
- npm 7.0.0 or higher (or yarn)
- Git

## Installation Steps

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

This installs:
- React 19.2 - UI library
- React Router DOM 6.20 - Routing
- Axios 1.6 - HTTP client
- Chart.js 4.4 - Charts
- React ChartJS 2 5.2 - React wrapper for Chart.js
- Plotly.js - Interactive visualizations

### 3. Configure Environment

Create `.env` file in frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Dataset Analysis Platform
VITE_APP_VERSION=1.0.0
```

### 4. Start Development Server

```bash
npm run dev
```

Frontend runs on `http://localhost:5173`

## Available Scripts

### Development
```bash
npm run dev          # Start development server
npm run dev --host   # Expose on network
```

### Build
```bash
npm run build        # Build for production
npm run preview      # Preview production build
```

### Lint
```bash
npm run lint         # Check code quality
npm run lint --fix   # Auto-fix issues
```

## Project Structure

```
frontend/
├── package.json                # Dependencies
├── vite.config.js             # Vite configuration
├── index.html                 # HTML entry point
├── src/
│   ├── main.jsx               # App entry point
│   ├── App.jsx                # Root component
│   ├── App.css                # Global styles
│   ├── index.css              # Base styles
│   ├── pages/                 # Page components
│   │   ├── Dashboard.jsx      # Home page
│   │   ├── Upload.jsx         # Upload interface
│   │   ├── History.jsx        # Dataset history
│   │   └── ReportViewer.jsx   # Report display
│   ├── components/            # Reusable components
│   │   ├── StatCard.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── RecentAnalysisCard.jsx
│   │   ├── QualityScoreGauge.jsx
│   │   └── BiasChart.jsx
│   ├── services/              # API services
│   │   └── api.js
│   └── utils/                 # Utilities
│       └── helpers.js
└── public/                    # Static assets
```

## Key Components

### Pages

#### Dashboard.jsx
Main dashboard with statistics and recent analyses.

**Features:**
- Statistical cards (total datasets, completed, success rate, avg quality)
- Recent analyses grid
- Analysis in progress counter

**API Calls:**
- `GET /api/dashboard/stats/`
- `GET /api/dashboard/overview/`

#### Upload.jsx
File upload interface with validation.

**Features:**
- Drag-drop support
- File type validation (CSV, XLSX, JSON)
- File size validation (max 100MB)
- Upload progress indication
- Error handling

**API Calls:**
- `POST /api/datasets/upload/`

#### History.jsx
Dataset history and management.

**Features:**
- Table view of datasets
- Status badges (completed, processing, failed, pending)
- View report links
- Delete functionality

**API Calls:**
- `GET /api/datasets/history/`

#### ReportViewer.jsx
Detailed analysis report display.

**Features:**
- Tabbed interface (Overview, Quality, Bias, Recommendations)
- Quality/Bias score gauges
- Recommendations list
- Export options

**API Calls:**
- `GET /api/datasets/{id}/`
- `GET /api/datasets/{id}/results/`
- `GET /api/reports/{id}/`

### Components

#### StatCard.jsx
Reusable statistics display.

```jsx
<StatCard
  title="Total Datasets"
  value={42}
  icon="📊"
  color="blue"
/>
```

#### LoadingSpinner.jsx
Loading state indicator.

```jsx
<LoadingSpinner />
```

#### RecentAnalysisCard.jsx
Recent dataset card display.

```jsx
<RecentAnalysisCard analysis={analysis} />
```

#### QualityScoreGauge.jsx
Circular gauge visualization.

```jsx
<QualityScoreGauge score={85} color="blue" />
```

#### BiasChart.jsx
Bar chart for bias distribution.

```jsx
<BiasChart data={biasData} />
```

## API Service

Location: `src/services/api.js`

### Axios Instance Configuration

```javascript
const api = axios.create({
  baseURL: process.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});
```

### Available Methods

```javascript
// Datasets
datasetAPI.upload(file, name)
datasetAPI.getHistory()
datasetAPI.getDetails(id)
datasetAPI.analyze(id)
datasetAPI.delete(id)

// Reports
reportAPI.getLatest()
reportAPI.getOne(id)
reportAPI.export(id, format)

// Dashboard
dashboardAPI.getStats()
dashboardAPI.getOverview()
```

## Styling

### Global Styles (App.css)

- Layout: Flexbox and CSS Grid
- Colors: Purple gradient theme (#667eea, #764ba2)
- Responsive: 768px mobile breakpoint
- Status colors: Green (success), Yellow (processing), Red (failed)

### CSS Classes

```css
.app                /* Main app container */
.navbar             /* Navigation bar */
.main-content       /* Page content */
.dashboard-grid     /* Responsive grid */
.stat-card          /* Statistics card */
.btn-primary        /* Primary button */
.upload-page        /* Upload page */
.history-table      /* History table */
.report-viewer      /* Report display */
.loading-spinner    /* Loading animation */
.status-badge       /* Status indicator */
```

## Forms & Validation

### Dataset Upload Validation

```javascript
const validateFile = (file) => {
  const maxSize = 100 * 1024 * 1024; // 100MB
  const allowedTypes = ['text/csv', 'application/json'];
  
  if (!file) return 'File is required';
  if (file.size > maxSize) return 'File exceeds 100MB limit';
  if (!allowedTypes.includes(file.type)) return 'Invalid file type';
  
  return null;
};
```

## Error Handling

### API Error Response Format

```javascript
{
  error: "Error message",
  status: 400,
  details: "Additional details"
}
```

### Error Handling Pattern

```javascript
try {
  const response = await api.get('/endpoint');
  setData(response.data);
} catch (error) {
  setError(error.response?.data?.error || 'An error occurred');
} finally {
  setLoading(false);
}
```

## State Management

Using React Hooks for local state management:

```javascript
const [data, setData] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

useEffect(() => {
  fetchData();
}, []);

const fetchData = async () => {
  setLoading(true);
  try {
    const response = await api.get('/endpoint');
    setData(response.data);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

## Routing Configuration

Location: `App.jsx`

```jsx
<BrowserRouter>
  <Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/upload" element={<Upload />} />
    <Route path="/history" element={<History />} />
    <Route path="/report/:id" element={<ReportViewer />} />
  </Routes>
</BrowserRouter>
```

## Performance Optimization

### Code Splitting
```javascript
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Upload = lazy(() => import('./pages/Upload'));
```

### Memoization
```javascript
const Dashboard = memo(function Dashboard() {
  // Component code
});
```

### Image Optimization
- Use WebP format for modern browsers
- Lazy load images
- Optimize image dimensions

## Build for Production

### 1. Build Application

```bash
npm run build
```

Output: `dist/` directory

### 2. Preview Build Locally

```bash
npm run preview
```

### 3. Deploy to Server

Copy `dist/` directory to web server:

```bash
# Using SCP
scp -r dist/* user@server:/var/www/html/

# Using FTP
# Upload dist/* to /public_html/
```

## Environment Configuration

### Development (.env.development)
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_DEBUG=true
```

### Production (.env.production)
```env
VITE_API_BASE_URL=https://api.yourdomain.com/api
VITE_DEBUG=false
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+
- Not supported: IE 11

## Testing

### Component Testing

```javascript
import { render, screen } from '@testing-library/react';
import Dashboard from './Dashboard';

test('renders dashboard', () => {
  render(<Dashboard />);
  expect(screen.getByText('Dashboard')).toBeInTheDocument();
});
```

Run tests:
```bash
npm test
```

## Deployment Options

### Netlify

```bash
npm run build
# Deploy dist/ folder
```

### Vercel

```bash
npm run build
# Connect Git repository to Vercel
```

### GitHub Pages

```bash
# Update vite.config.js base
export default {
  base: '/repository-name/'
}

npm run build
```

### Traditional Server (Nginx)

```nginx
server {
  listen 80;
  server_name yourdomain.com;

  root /var/www/frontend/dist;
  index index.html;

  location / {
    try_files $uri /index.html;
  }

  location /api/ {
    proxy_pass http://backend:8000/api/;
  }
}
```

## Docker Deployment

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

Build and run:
```bash
docker build -t frontend .
docker run -p 3000:3000 frontend
```

## Security

### Content Security Policy

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'">
```

### HTTPS

Always use HTTPS in production. Configure redirects:

```nginx
server {
  listen 80;
  server_name yourdomain.com;
  return 301 https://$server_name$request_uri;
}
```

### API Security

- Validate all inputs
- Sanitize output
- Use CSRF tokens
- Implement rate limiting
- Use secure cookies

## Troubleshooting

### Node Modules Issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use

```bash
# Kill process on port 5173
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :5173
kill -9 <PID>
```

### Blank Page After Build

- Check API_BASE_URL in .env
- Check browser console for errors
- Verify backend is running
- Clear browser cache

### Styling Not Applied

- Check CSS imports in components
- Verify CSS class names match
- Clear browser cache
- Rebuild: `npm run build`

## Performance Metrics

Monitor performance using:

```javascript
// Web Vitals
import { getLCP, getFID, getFCP, getLCPEntries } from 'web-vitals';

getLCP(console.log);
getFID(console.log);
getFCP(console.log);
```

## Chrome DevTools

### Performance Profiling
1. Open DevTools → Performance
2. Click record → Perform actions → Stop
3. Analyze the timeline

### Network Profiling
1. Open DevTools → Network
2. Reload page
3. Check API requests and response times

## Advanced Configuration

### Vite Configuration (vite.config.js)

```javascript
export default {
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  }
}
```

## Additional Resources

- [React Documentation](https://react.dev/)
- [React Router](https://reactrouter.com/)
- [Vite Documentation](https://vitejs.dev/)
- [Axios Documentation](https://axios-http.com/)

## Support

For issues or questions, refer to main README.md or contact support.
