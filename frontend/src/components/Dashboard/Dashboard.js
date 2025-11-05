import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  Button,
  CircularProgress,
} from '@mui/material';
import {
  School as SchoolIcon,
  Schedule as ScheduleIcon,
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { coursesAPI } from '../../services/api';

const Dashboard = () => {
  // Get user data from localStorage instead of AuthContext
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [conflicts, setConflicts] = useState([]);
  const [currentSchedule, setCurrentSchedule] = useState(null);
  const [degreeAudits, setDegreeAudits] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load course recommendations
      const recResponse = await coursesAPI.getRecommendations();
      setRecommendations(recResponse.data.slice(0, 5)); // Show top 5
      
      // For now, set empty data since we don't have schedule context
      setCurrentSchedule(null);
      setDegreeAudits([]);
      setConflicts([]);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // If it's an authentication error, don't let it trigger the global interceptor
      if (error.response?.status === 401) {
        console.log('Authentication error in dashboard - user may need to re-login');
        // Don't rethrow the error to prevent the global interceptor from redirecting
        setRecommendations([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const getProgressPercentage = (audit) => {
    if (!audit || !audit.progress) return 0;
    return Math.round(audit.progress.percentage_complete);
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'info';
    if (percentage >= 40) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Welcome back, {user?.username || 'User'}!
      </Typography>

      <Grid container spacing={3}>
        {/* Current Schedule Overview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <ScheduleIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Current Schedule</Typography>
              </Box>
              
              {currentSchedule ? (
                <Box>
                  <Typography variant="body1" gutterBottom>
                    <strong>{currentSchedule.name}</strong> - {currentSchedule.semester} {currentSchedule.year}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {currentSchedule.total_credits} credits • {currentSchedule.schedule_items?.length || 0} courses
                  </Typography>
                  
                  {conflicts.length > 0 && (
                    <Alert severity="warning" sx={{ mt: 2 }}>
                      {conflicts.length} conflict{conflicts.length > 1 ? 's' : ''} detected in your schedule
                    </Alert>
                  )}
                  
                  {currentSchedule.schedule_items?.length > 0 && (
                    <List dense>
                      {currentSchedule.schedule_items.slice(0, 3).map((item, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={item.offering.course.full_code}
                            secondary={item.offering.course.title}
                          />
                        </ListItem>
                      ))}
                      {currentSchedule.schedule_items.length > 3 && (
                        <ListItem>
                          <ListItemText
                            primary={`+${currentSchedule.schedule_items.length - 3} more courses`}
                            sx={{ fontStyle: 'italic' }}
                          />
                        </ListItem>
                      )}
                    </List>
                  )}
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No active schedule found. Create one to get started!
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Degree Progress */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AssessmentIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Degree Progress</Typography>
              </Box>
              
              {degreeAudits.length > 0 ? (
                <Box>
                  {degreeAudits.map((audit, index) => (
                    <Box key={index} mb={2}>
                      <Typography variant="body2" gutterBottom>
                        {audit.degree_program}
                      </Typography>
                      <Box display="flex" alignItems="center" mb={1}>
                        <LinearProgress
                          variant="determinate"
                          value={getProgressPercentage(audit)}
                          color={getProgressColor(getProgressPercentage(audit))}
                          sx={{ flexGrow: 1, mr: 1 }}
                        />
                        <Typography variant="body2" color="text.secondary">
                          {getProgressPercentage(audit)}%
                        </Typography>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {audit.progress?.credits_earned || 0} / {audit.progress?.total_credits_required || 0} credits
                      </Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No degree program enrolled
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Course Recommendations */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Box display="flex" alignItems="center">
                  <SchoolIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Recommended Courses</Typography>
                </Box>
                <Button size="small" href="/courses">
                  View All
                </Button>
              </Box>
              
              {recommendations.length > 0 ? (
                <List>
                  {recommendations.map((rec, index) => (
                    <ListItem key={index} divider={index < recommendations.length - 1}>
                      <ListItemIcon>
                        {rec.can_take ? (
                          <CheckCircleIcon color="success" />
                        ) : (
                          <WarningIcon color="warning" />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={rec.course.full_code}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {rec.course.title}
                            </Typography>
                            <Box mt={1}>
                              <Chip
                                label={`${rec.credits} credits`}
                                size="small"
                                variant="outlined"
                                sx={{ mr: 1 }}
                              />
                              {rec.reason && (
                                <Chip
                                  label={rec.reason}
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                />
                              )}
                            </Box>
                            {!rec.can_take && rec.missing_prerequisites.length > 0 && (
                              <Typography variant="caption" color="error" display="block" mt={1}>
                                Missing: {rec.missing_prerequisites.join(', ')}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No recommendations available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;

