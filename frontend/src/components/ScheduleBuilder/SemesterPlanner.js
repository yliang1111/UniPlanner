import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  Schedule as ScheduleIcon,
  School as SchoolIcon,
} from '@mui/icons-material';
import { coursesAPI } from '../../services/api';

const SEMESTER_OPTIONS = [
  { value: 'fall', label: 'Fall' },
  { value: 'spring', label: 'Spring' },
  { value: 'summer', label: 'Summer' },
  { value: 'winter', label: 'Winter' },
];

const YEAR_OPTIONS = Array.from({ length: 6 }, (_, i) => new Date().getFullYear() + i);

const SemesterPlanner = () => {
  // For now, set empty currentSchedule since we don't have schedule context
  const currentSchedule = null;
  
  const [semesterPlans, setSemesterPlans] = useState({});
  const [addCourseDialog, setAddCourseDialog] = useState(false);
  const [alternativesDialog, setAlternativesDialog] = useState(false);
  const [selectedSemester, setSelectedSemester] = useState('');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  
  const [availableOfferings, setAvailableOfferings] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [alternatives, setAlternatives] = useState([]);
  const [selectedOffering, setSelectedOffering] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (currentSchedule) {
      loadConflicts();
      loadSemesterPlans();
    }
  }, [currentSchedule]);

  const loadSemesterPlans = () => {
    if (currentSchedule?.schedule_items) {
      const plans = {};
      currentSchedule.schedule_items.forEach(item => {
        const key = `${item.offering.semester}_${item.offering.year}`;
        if (!plans[key]) {
          plans[key] = {
            semester: item.offering.semester,
            year: item.offering.year,
            courses: [],
            totalCredits: 0
          };
        }
        plans[key].courses.push(item);
        plans[key].totalCredits += item.offering.course.credits;
      });
      setSemesterPlans(plans);
    }
  };

  const loadConflicts = async () => {
    // For now, set empty conflicts since we don't have schedule context
    setConflicts([]);
  };

  const loadAvailableOfferings = async (semester, year) => {
    try {
      setLoading(true);
      const response = await coursesAPI.getOfferings({
        semester: semester,
        year: year,
        available_only: true,
      });
      setAvailableOfferings(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading offerings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCourse = async (offeringId) => {
    // For now, just close the dialog since we don't have schedule context
    setAddCourseDialog(false);
    console.log('Adding course:', offeringId);
  };

  const handleRemoveCourse = async (offeringId) => {
    // For now, just log since we don't have schedule context
    console.log('Removing course:', offeringId);
  };

  const handleAddAlternative = async (alternativeOfferingId) => {
    // For now, just close the dialog since we don't have schedule context
    setAlternativesDialog(false);
    console.log('Adding alternative course:', alternativeOfferingId);
  };

  const openAddCourseDialog = (semester, year) => {
    setSelectedSemester(semester);
    setSelectedYear(year);
    setAddCourseDialog(true);
    loadAvailableOfferings(semester, year);
  };

  const getSemesterDisplayName = (semester) => {
    return SEMESTER_OPTIONS.find(opt => opt.value === semester)?.label || semester;
  };

  const getTotalCredits = () => {
    return Object.values(semesterPlans).reduce((total, plan) => total + plan.totalCredits, 0);
  };

  const getTotalCourses = () => {
    return Object.values(semesterPlans).reduce((total, plan) => total + plan.courses.length, 0);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          Semester Planning
        </Typography>
        <Box display="flex" gap={2}>
          <Chip 
            icon={<SchoolIcon />} 
            label={`${getTotalCourses()} Courses`} 
            color="primary" 
            variant="outlined" 
          />
          <Chip 
            icon={<ScheduleIcon />} 
            label={`${getTotalCredits()} Credits`} 
            color="secondary" 
            variant="outlined" 
          />
        </Box>
      </Box>

      {conflicts.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Schedule Conflicts Detected
          </Typography>
          {conflicts.map((conflict, index) => (
            <Typography key={index} variant="body2">
              • {conflict.description}
            </Typography>
          ))}
        </Alert>
      )}

      {Object.keys(semesterPlans).length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <SchoolIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No Courses Planned
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Start planning your semesters by adding courses to your schedule
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => openAddCourseDialog('fall', new Date().getFullYear())}
            >
              Add First Course
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {Object.entries(semesterPlans)
            .sort(([a], [b]) => {
              const [semA, yearA] = a.split('_');
              const [semB, yearB] = b.split('_');
              if (yearA !== yearB) return parseInt(yearA) - parseInt(yearB);
              const order = { fall: 1, winter: 2, spring: 3, summer: 4 };
              return order[semA] - order[semB];
            })
            .map(([key, plan]) => (
              <Grid item xs={12} md={6} key={key}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6">
                        {getSemesterDisplayName(plan.semester)} {plan.year}
                      </Typography>
                      <Box display="flex" gap={1}>
                        <Chip 
                          label={`${plan.totalCredits} credits`} 
                          size="small" 
                          color="primary" 
                          variant="outlined" 
                        />
                        <Chip 
                          label={`${plan.courses.length} courses`} 
                          size="small" 
                          color="secondary" 
                          variant="outlined" 
                        />
                      </Box>
                    </Box>

                    <Divider sx={{ mb: 2 }} />

                    {plan.courses.length > 0 ? (
                      <List dense>
                        {plan.courses.map((item, index) => (
                          <ListItem key={index} divider>
                            <ListItemText
                              primary={item.offering.course.full_code}
                              secondary={
                                <Box>
                                  <Typography variant="body2" color="text.secondary">
                                    {item.offering.course.title}
                                  </Typography>
                                  <Box mt={1}>
                                    <Chip
                                      label={`${item.offering.course.credits} credits`}
                                      size="small"
                                      variant="outlined"
                                      sx={{ mr: 1 }}
                                    />
                                    <Chip
                                      label={item.offering.section}
                                      size="small"
                                      color="primary"
                                      variant="outlined"
                                    />
                                  </Box>
                                  {item.offering.time_slots.map((slot, slotIndex) => (
                                    <Typography key={slotIndex} variant="caption" display="block">
                                      {slot.day_of_week}: {slot.start_time} - {slot.end_time}
                                      {slot.location && ` (${slot.location})`}
                                    </Typography>
                                  ))}
                                </Box>
                              }
                            />
                            <ListItemSecondaryAction>
                              <IconButton
                                edge="end"
                                onClick={() => handleRemoveCourse(item.offering.id)}
                                color="error"
                                size="small"
                              >
                                <DeleteIcon />
                              </IconButton>
                            </ListItemSecondaryAction>
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                        No courses in this semester
                      </Typography>
                    )}

                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={() => openAddCourseDialog(plan.semester, plan.year)}
                      fullWidth
                      sx={{ mt: 2 }}
                    >
                      Add Course to {getSemesterDisplayName(plan.semester)} {plan.year}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
        </Grid>
      )}

      {/* Add Course Dialog */}
      <Dialog 
        open={addCourseDialog} 
        onClose={() => setAddCourseDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Add Course to {getSemesterDisplayName(selectedSemester)} {selectedYear}
        </DialogTitle>
        <DialogContent>
          {loading ? (
            <Box display="flex" justifyContent="center" p={3}>
              <CircularProgress />
            </Box>
          ) : (
            <List>
              {availableOfferings.map((offering, index) => (
                <ListItem key={index} divider>
                  <ListItemText
                    primary={offering.course.full_code}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {offering.course.title}
                        </Typography>
                        <Box mt={1}>
                          <Chip
                            label={`${offering.course.credits} credits`}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 1 }}
                          />
                          <Chip
                            label={offering.section}
                            size="small"
                            color="primary"
                            variant="outlined"
                            sx={{ mr: 1 }}
                          />
                          {offering.is_available && (
                            <Chip
                              label="Available"
                              size="small"
                              color="success"
                              variant="outlined"
                            />
                          )}
                        </Box>
                        {offering.time_slots.map((slot, slotIndex) => (
                          <Typography key={slotIndex} variant="caption" display="block">
                            {slot.day_of_week}: {slot.start_time} - {slot.end_time}
                            {slot.location && ` (${slot.location})`}
                          </Typography>
                        ))}
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Button
                      size="small"
                      variant="contained"
                      onClick={() => handleAddCourse(offering.id)}
                    >
                      Add
                    </Button>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddCourseDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Alternatives Dialog */}
      <Dialog 
        open={alternativesDialog} 
        onClose={() => setAlternativesDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Schedule Conflict - Alternative Times</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            The course you selected conflicts with your current schedule. Here are alternative times:
          </Alert>
          <List>
            {alternatives.map((offering, index) => (
              <ListItem key={index} divider>
                <ListItemText
                  primary={offering.course.full_code}
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {offering.course.title}
                      </Typography>
                      <Box mt={1}>
                        <Chip
                          label={`${offering.course.credits} credits`}
                          size="small"
                          variant="outlined"
                          sx={{ mr: 1 }}
                        />
                        <Chip
                          label={offering.section}
                          size="small"
                          color="primary"
                          variant="outlined"
                          sx={{ mr: 1 }}
                        />
                        <Chip
                          label="No Conflicts"
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      </Box>
                      {offering.time_slots.map((slot, slotIndex) => (
                        <Typography key={slotIndex} variant="caption" display="block">
                          {slot.day_of_week}: {slot.start_time} - {slot.end_time}
                          {slot.location && ` (${slot.location})`}
                        </Typography>
                      ))}
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={() => handleAddAlternative(offering.id)}
                  >
                    Add Alternative
                  </Button>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAlternativesDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SemesterPlanner;

