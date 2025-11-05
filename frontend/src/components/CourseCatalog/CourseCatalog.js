import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  School as SchoolIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { coursesAPI } from '../../services/api';

const CourseCatalog = () => {
  const [tabValue, setTabValue] = useState(0);
  const [courses, setCourses] = useState([]);
  const [availableCourses, setAvailableCourses] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const [filters, setFilters] = useState({
    search: '',
    department: '',
    minCredits: '',
    maxCredits: '',
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load departments
      const deptResponse = await coursesAPI.getDepartments();
      setDepartments(deptResponse.data.departments || deptResponse.data.results || deptResponse.data || []);
      
      // Load all courses
      await loadCourses();
      
      // Load available courses
      await loadAvailableCourses();
      
      // Load recommendations
      await loadRecommendations();
    } catch (error) {
      console.error('Error loading initial data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCourses = async () => {
    try {
      const params = {
        with_prerequisites: true,
        ...filters,
      };
      
      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (params[key] === '') {
          delete params[key];
        }
      });
      
      const response = await coursesAPI.getCourses(params);
      setCourses(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading courses:', error);
    }
  };

  const loadAvailableCourses = async () => {
    try {
      const response = await coursesAPI.getAvailableCourses();
      setAvailableCourses(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading available courses:', error);
    }
  };

  const loadRecommendations = async () => {
    try {
      const response = await coursesAPI.getRecommendations();
      setRecommendations(response.data);
    } catch (error) {
      console.error('Error loading recommendations:', error);
    }
  };

  const handleFilterChange = (field, value) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
  };

  const handleSearch = () => {
    loadCourses();
  };

  const handleAddToSchedule = async (course) => {
    // For now, we'll just show a message
    // In a real implementation, you'd need to select a specific offering
    alert(`To add ${course.full_code} to your schedule, please use the Schedule Builder to select a specific time slot.`);
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`catalog-tabpanel-${index}`}
      aria-labelledby={`catalog-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  const CourseCard = ({ course, showPrerequisites = false }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography variant="h6" gutterBottom>
              {course.full_code}
            </Typography>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              {course.title}
            </Typography>
            <Typography variant="body2" paragraph>
              {course.description}
            </Typography>
          </Box>
          <Box display="flex" flexDirection="column" alignItems="flex-end">
            <Chip
              label={`${course.credits} credits`}
              color="primary"
              variant="outlined"
              sx={{ mb: 1 }}
            />
            {course.can_take !== undefined && (
              <Chip
                icon={course.can_take ? <CheckCircleIcon /> : <WarningIcon />}
                label={course.can_take ? 'Available' : 'Prerequisites Required'}
                color={course.can_take ? 'success' : 'warning'}
                variant="outlined"
                size="small"
              />
            )}
          </Box>
        </Box>

        {showPrerequisites && course.prerequisites && course.prerequisites.length > 0 && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">
                Prerequisites ({course.prerequisites.length})
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <List dense>
                {Array.isArray(course.prerequisites) ? course.prerequisites.map((prereq, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={prereq.full_code} secondary={prereq.title} />
                  </ListItem>
                )) : null}
              </List>
            </AccordionDetails>
          </Accordion>
        )}

        {course.missing_prerequisites && course.missing_prerequisites.length > 0 && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Missing Prerequisites:</strong> {course.missing_prerequisites.join(', ')}
            </Typography>
          </Alert>
        )}

        {course.reason && (
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Recommendation:</strong> {course.reason}
            </Typography>
          </Alert>
        )}

        <Box display="flex" justifyContent="flex-end" mt={2}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => handleAddToSchedule(course)}
            disabled={!course.can_take}
          >
            Add to Schedule
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Course Catalog
      </Typography>

      <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
        <Tab label="All Courses" />
        <Tab label="Available Courses" />
        <Tab label="Recommendations" />
      </Tabs>

      <TabPanel value={tabValue} index={0}>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Search & Filter
            </Typography>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Search courses"
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  InputProps={{
                    startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Department</InputLabel>
                  <Select
                    value={filters.department}
                    label="Department"
                    onChange={(e) => handleFilterChange('department', e.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    {Array.isArray(departments) ? departments.map((dept) => (
                      <MenuItem key={dept.id} value={dept.code}>
                        {dept.code} - {dept.name}
                      </MenuItem>
                    )) : null}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  label="Min Credits"
                  type="number"
                  value={filters.minCredits}
                  onChange={(e) => handleFilterChange('minCredits', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  label="Max Credits"
                  type="number"
                  value={filters.maxCredits}
                  onChange={(e) => handleFilterChange('maxCredits', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={handleSearch}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Search'}
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            {Array.isArray(courses) && courses.length > 0 ? (
              courses.map((course) => (
                <CourseCard key={course.id} course={course} showPrerequisites />
              ))
            ) : (
              <Card>
                <CardContent sx={{ textAlign: 'center', py: 6 }}>
                  <SchoolIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No courses found
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Try adjusting your search criteria
                  </Typography>
                </CardContent>
              </Card>
            )}
          </Box>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Alert severity="info" sx={{ mb: 3 }}>
          These are courses you can take based on your completed prerequisites.
        </Alert>
        
        {Array.isArray(availableCourses) && availableCourses.length > 0 ? (
          availableCourses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))
        ) : (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <CheckCircleIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No available courses
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Complete more prerequisites to unlock additional courses
              </Typography>
            </CardContent>
          </Card>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Alert severity="info" sx={{ mb: 3 }}>
          These courses are recommended based on your degree requirements and academic progress.
        </Alert>
        
        {Array.isArray(recommendations) && recommendations.length > 0 ? (
          recommendations.map((rec) => (
            <CourseCard key={rec.course.id} course={rec.course} />
          ))
        ) : (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <InfoIcon sx={{ fontSize: 64, color: 'info.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No recommendations available
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Complete your profile to get personalized course recommendations
              </Typography>
            </CardContent>
          </Card>
        )}
      </TabPanel>
    </Box>
  );
};

export default CourseCatalog;
