import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Alert,
  Collapse,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
const DAYS = [
  { key: 'monday', label: 'Monday' },
  { key: 'tuesday', label: 'Tuesday' },
  { key: 'wednesday', label: 'Wednesday' },
  { key: 'thursday', label: 'Thursday' },
  { key: 'friday', label: 'Friday' },
  { key: 'saturday', label: 'Saturday' },
  { key: 'sunday', label: 'Sunday' },
];

const TIME_SLOTS = [
  '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
  '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM'
];

const WeeklyCalendar = ({ onCourseRemove, conflicts = [] }) => {
  // For now, set empty currentSchedule since we don't have schedule context
  const currentSchedule = null;
  const [scheduleData, setScheduleData] = useState({});
  const [showConflicts, setShowConflicts] = useState(true);

  useEffect(() => {
    if (currentSchedule?.schedule_items) {
      const newScheduleData = {};
      
      // Initialize all days
      DAYS.forEach(day => {
        newScheduleData[day.key] = [];
      });

      // Populate with current schedule items
      currentSchedule.schedule_items.forEach(item => {
        item.offering.time_slots.forEach(timeSlot => {
          const dayKey = timeSlot.day_of_week;
          if (!newScheduleData[dayKey]) {
            newScheduleData[dayKey] = [];
          }
          
          newScheduleData[dayKey].push({
            id: `${item.id}-${timeSlot.id}`,
            course: item.offering.course,
            offering: item.offering,
            timeSlot: timeSlot,
            scheduleItem: item,
          });
        });
      });

      // Sort by start time
      Object.keys(newScheduleData).forEach(day => {
        newScheduleData[day].sort((a, b) => 
          new Date(`1970/01/01 ${a.timeSlot.start_time}`) - 
          new Date(`1970/01/01 ${b.timeSlot.start_time}`)
        );
      });

      setScheduleData(newScheduleData);
    }
  }, [currentSchedule]);

  const formatTime = (timeString) => {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  const getTimeSlotHeight = (startTime, endTime) => {
    const start = new Date(`1970/01/01 ${startTime}`);
    const end = new Date(`1970/01/01 ${endTime}`);
    const duration = (end - start) / (1000 * 60); // duration in minutes
    return Math.max(duration / 15, 2); // minimum 2 units, each unit = 15 minutes
  };

  const getTimeSlotTop = (startTime) => {
    const [hours, minutes] = startTime.split(':');
    const hour = parseInt(hours);
    const minute = parseInt(minutes);
    const totalMinutes = hour * 60 + minute;
    const startMinutes = 8 * 60; // 8:00 AM
    return ((totalMinutes - startMinutes) / 15) * 2; // 2 units per 15 minutes
  };

  const isConflicting = (courseItem) => {
    return conflicts.some(conflict => 
      conflict.courses.includes(courseItem.course.full_code)
    );
  };

  return (
    <Box>
      {conflicts.length > 0 && (
        <Alert 
          severity="warning" 
          sx={{ mb: 2 }}
          action={
            <IconButton
              size="small"
              onClick={() => setShowConflicts(!showConflicts)}
            >
              <InfoIcon />
            </IconButton>
          }
        >
          <Typography variant="body2">
            {conflicts.length} conflict{conflicts.length > 1 ? 's' : ''} detected in your schedule
          </Typography>
          <Collapse in={showConflicts}>
            <Box mt={1}>
              {conflicts.map((conflict, index) => (
                <Typography key={index} variant="caption" display="block">
                  • {conflict.description}
                </Typography>
              ))}
            </Box>
          </Collapse>
        </Alert>
      )}

      <Paper elevation={2} sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Weekly Schedule
        </Typography>
        
        <Grid container spacing={1}>
          {/* Time column */}
          <Grid item xs={1}>
            <Box sx={{ height: 600, position: 'relative' }}>
              {TIME_SLOTS.map((time, index) => (
                <Box
                  key={time}
                  sx={{
                    position: 'absolute',
                    top: index * 50,
                    left: 0,
                    fontSize: '0.75rem',
                    color: 'text.secondary',
                    transform: 'translateY(-50%)',
                  }}
                >
                  {time}
                </Box>
              ))}
            </Box>
          </Grid>

          {/* Day columns */}
          {DAYS.map(day => (
            <Grid item xs key={day.key}>
              <Box>
                <Typography variant="subtitle2" align="center" gutterBottom>
                  {day.label}
                </Typography>
                
                <Box
                  sx={{
                    minHeight: 600,
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    backgroundColor: 'background.paper',
                    position: 'relative',
                  }}
                >
                  {scheduleData[day.key]?.map((courseItem, index) => (
                    <Card
                      key={courseItem.id}
                      sx={{
                        position: 'absolute',
                        top: getTimeSlotTop(courseItem.timeSlot.start_time) * 2,
                        left: 4,
                        right: 4,
                        minHeight: getTimeSlotHeight(
                          courseItem.timeSlot.start_time,
                          courseItem.timeSlot.end_time
                        ) * 2,
                        backgroundColor: isConflicting(courseItem) ? 'error.light' : 'primary.light',
                        color: 'white',
                        '&:hover': {
                          backgroundColor: isConflicting(courseItem) ? 'error.main' : 'primary.main',
                        },
                      }}
                    >
                      <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
                        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                          <Box flexGrow={1}>
                            <Typography variant="body2" fontWeight="bold">
                              {courseItem.course.full_code}
                            </Typography>
                            <Typography variant="caption" display="block">
                              {formatTime(courseItem.timeSlot.start_time)} - {formatTime(courseItem.timeSlot.end_time)}
                            </Typography>
                            {courseItem.timeSlot.location && (
                              <Typography variant="caption" display="block">
                                {courseItem.timeSlot.location}
                              </Typography>
                            )}
                          </Box>
                          
                          <Box display="flex" alignItems="center">
                            {isConflicting(courseItem) && (
                              <Tooltip title="Schedule conflict detected">
                                <WarningIcon sx={{ fontSize: 16, mr: 0.5 }} />
                              </Tooltip>
                            )}
                            
                            <IconButton
                              size="small"
                              onClick={() => onCourseRemove(courseItem.offering.id)}
                              sx={{ 
                                color: 'white',
                                '&:hover': { backgroundColor: 'rgba(255,255,255,0.2)' }
                              }}
                            >
                              <DeleteIcon sx={{ fontSize: 16 }} />
                            </IconButton>
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                  
                  {(!scheduleData[day.key] || scheduleData[day.key].length === 0) && (
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: '100%',
                        color: 'text.secondary',
                        fontSize: '0.875rem',
                      }}
                    >
                      No classes
                    </Box>
                  )}
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Box>
  );
};

export default WeeklyCalendar;
