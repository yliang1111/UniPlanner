# UniPlanner - Intelligent Degree Planning and Audit System

UniPlanner is a comprehensive full-stack application designed to help students plan their academic journey with intelligent course scheduling, prerequisite validation, and degree progress tracking.

## Features

### Core Advanced Features

1. **Prerequisite Validation**: Uses graph traversal algorithms to check if a user can take a course based on completed prerequisites
2. **Degree Audit Dashboard**: Visual progress tracking for degree requirements with real-time updates
3. **Schedule Conflict Detection**: Prevents users from adding overlapping courses with intelligent conflict resolution
4. **Drag-and-Drop UI**: Interactive weekly calendar for building and managing schedules

### Additional Features

- Course catalog with advanced filtering and search
- Personalized course recommendations
- Real-time schedule optimization suggestions
- Multi-semester planning support
- Academic progress visualization

## Tech Stack

- **Frontend**: React.js with Material-UI
- **Backend**: Django REST Framework
- **Database**: SQLite (development)
- **Authentication**: Django's built-in authentication system

## Project Structure

```
UniPlanner/
├── backend/                 # Django backend
│   ├── courses/            # Course management app
│   ├── users/              # User management app
│   ├── schedules/          # Schedule management app
│   └── uniplanner/         # Main Django project
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts
│   │   └── services/       # API services
└── docs/                   # Documentation
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install django djangorestframework django-cors-headers python-decouple
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Courses
- `GET /api/courses/courses/` - List all courses
- `GET /api/courses/courses/available/` - Get available courses for student
- `GET /api/courses/courses/recommendations/` - Get course recommendations
- `GET /api/courses/courses/{id}/can_take/` - Check if student can take course

### Schedules
- `GET /api/schedules/schedules/` - List user schedules
- `POST /api/schedules/schedules/` - Create new schedule
- `POST /api/schedules/schedules/{id}/add_course/` - Add course to schedule
- `GET /api/schedules/schedules/{id}/conflicts/` - Get schedule conflicts

### Users
- `GET /api/users/users/me/` - Get current user profile
- `GET /api/users/profiles/` - Get user profiles

## Demo Credentials

- Username: `admin`
- Password: `admin123`

## Key Algorithms

### Prerequisite Validation
- Uses graph traversal (BFS/DFS) to validate prerequisite chains
- Implements cycle detection for prerequisite graphs
- Provides topological sorting for course recommendations

### Schedule Conflict Detection
- Time overlap detection using interval arithmetic
- Location and instructor conflict detection
- Real-time conflict resolution suggestions

### Degree Audit
- Real-time progress calculation
- Requirement satisfaction tracking
- Visual progress indicators

## Development

### Adding New Features

1. **Backend**: Add models, serializers, and views in appropriate Django apps
2. **Frontend**: Create React components and integrate with API services
3. **Testing**: Add unit tests for both backend and frontend

### Database Schema

The application uses a relational database with the following key models:
- `Course`: Course information and metadata
- `Prerequisite`: Prerequisite relationships between courses
- `Schedule`: Student schedules for specific semesters
- `DegreeProgram`: Degree program definitions
- `DegreeRequirement`: Requirements for degree programs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

