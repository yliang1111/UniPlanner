import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/Layout/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import CourseCatalog from './components/CourseCatalog/CourseCatalog';
import ScheduleBuilder from './components/ScheduleBuilder/ScheduleBuilder';
import DegreeAudit from './components/DegreeAudit/DegreeAudit';
import Login from './components/Auth/Login';
import Signup from './components/Auth/Signup';
import Profile from './components/Profile/Profile';
import CourseManagement from './components/Admin/CourseManagement';
import ProgramManagement from './components/Admin/ProgramManagement';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import Redirect from './components/Auth/Redirect';

// Create Material-UI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

function App() {
  // Set document title
  useEffect(() => {
    document.title = 'UniPlanner - Degree Planning System';
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                        <Route path="/" element={<Redirect />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/courses" element={<CourseCatalog />} />
                        <Route path="/schedule" element={<ScheduleBuilder />} />
                        <Route path="/audit" element={<DegreeAudit />} />
                            <Route path="/profile" element={<Profile />} />
                            <Route path="/admin/courses" element={<CourseManagement />} />
                            <Route path="/admin/programs" element={<ProgramManagement />} />
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;