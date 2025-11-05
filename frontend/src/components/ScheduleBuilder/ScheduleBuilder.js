import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
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
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Warning as WarningIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import WeeklyCalendar from './WeeklyCalendar';
import SemesterPlanner from './SemesterPlanner';
const SEMESTER_OPTIONS = [
  { value: 'fall', label: 'Fall' },
  { value: 'spring', label: 'Spring' },
  { value: 'summer', label: 'Summer' },
  { value: 'winter', label: 'Winter' },
];

const ScheduleBuilder = () => {
  // For now, set empty state since we don't have schedule context
  const currentSchedule = null;
  
  const [tabValue, setTabValue] = useState(0);
  const [newScheduleDialog, setNewScheduleDialog] = useState(false);
  
  const [newSchedule, setNewSchedule] = useState({
    name: '',
    semester: 'fall',
    year: new Date().getFullYear(),
  });
  
  const [conflicts, setConflicts] = useState([]);

  useEffect(() => {
    if (currentSchedule) {
      loadConflicts();
    }
  }, [currentSchedule]);

  const loadConflicts = async () => {
    // For now, set empty conflicts since we don't have schedule context
    setConflicts([]);
  };


  const handleCreateSchedule = async () => {
    // For now, just close the dialog since we don't have schedule context
    setNewScheduleDialog(false);
    setNewSchedule({ name: '', semester: 'fall', year: new Date().getFullYear() });
    console.log('Creating schedule:', newSchedule);
  };

  const handleRemoveCourse = async (offeringId) => {
    // For now, just log since we don't have schedule context
    console.log('Removing course:', offeringId);
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`schedule-tabpanel-${index}`}
      aria-labelledby={`schedule-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Schedule Builder
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setNewScheduleDialog(true)}
        >
          New Schedule
        </Button>
      </Box>

      {!currentSchedule ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <ScheduleIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No Active Schedule
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Create a new schedule to start planning your courses
            </Typography>
            <Button
              variant="contained"
              onClick={() => setNewScheduleDialog(true)}
            >
              Create Schedule
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Box>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="Semester Planning" />
            <Tab label="Weekly Calendar" />
            <Tab label="Course List" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <SemesterPlanner />
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <WeeklyCalendar 
              onCourseRemove={handleRemoveCourse}
              conflicts={conflicts}
            />
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Current Schedule: {currentSchedule.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {currentSchedule.semester} {currentSchedule.year} • {currentSchedule.total_credits} credits
                    </Typography>

                    {currentSchedule.schedule_items?.length > 0 ? (
                      <List>
                        {currentSchedule.schedule_items.map((item, index) => (
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
                              >
                                <DeleteIcon />
                              </IconButton>
                            </ListItemSecondaryAction>
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No courses added to this schedule yet.
                      </Typography>
                    )}

                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                {conflicts.length > 0 && (
                  <Card sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="h6" color="error" gutterBottom>
                        <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Conflicts
                      </Typography>
                      {conflicts.map((conflict, index) => (
                        <Alert key={index} severity="warning" sx={{ mb: 1 }}>
                          {conflict.description}
                        </Alert>
                      ))}
                    </CardContent>
                  </Card>
                )}

                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Schedule Summary
                    </Typography>
                    <Box>
                      <Typography variant="body2" gutterBottom>
                        <strong>Total Credits:</strong> {currentSchedule.total_credits}
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        <strong>Courses:</strong> {currentSchedule.schedule_items?.length || 0}
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        <strong>Conflicts:</strong> {conflicts.length}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>
        </Box>
      )}

      {/* New Schedule Dialog */}
      <Dialog open={newScheduleDialog} onClose={() => setNewScheduleDialog(false)}>
        <DialogTitle>Create New Schedule</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Schedule Name"
            fullWidth
            variant="outlined"
            value={newSchedule.name}
            onChange={(e) => setNewSchedule({ ...newSchedule, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Semester</InputLabel>
            <Select
              value={newSchedule.semester}
              label="Semester"
              onChange={(e) => setNewSchedule({ ...newSchedule, semester: e.target.value })}
            >
              {SEMESTER_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="Year"
            type="number"
            fullWidth
            variant="outlined"
            value={newSchedule.year}
            onChange={(e) => setNewSchedule({ ...newSchedule, year: parseInt(e.target.value) })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewScheduleDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateSchedule} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

    </Box>
  );
};

export default ScheduleBuilder;
