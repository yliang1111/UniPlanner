import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Autocomplete,
  TextField,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  School as SchoolIcon,
  Remove as RemoveIcon,
  Edit as EditIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { coursesAPI, schedulesAPI } from '../../services/api';

const SemesterGrid = ({ degreeAudits, onUpdate }) => {
  const [courses, setCourses] = useState([]);
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [selectedCell, setSelectedCell] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPrograms, setSelectedPrograms] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [departments, setDepartments] = useState([]);
  const [gridData, setGridData] = useState({});
  const [semesterRows, setSemesterRows] = useState({});

  // Initialize 14 semesters (7 years, 2 semesters per year)
  const SEMESTERS = [];
  const currentYear = new Date().getFullYear();
  for (let year = currentYear; year < currentYear + 7; year++) {
    SEMESTERS.push(
      { id: `fall-${year}`, name: `Fall ${year}`, year, semester: 'Fall' },
      { id: `spring-${year}`, name: `Spring ${year}`, year, semester: 'Spring' }
    );
  }

  // Initialize with 5 rows per semester
  useEffect(() => {
    const initialRows = {};
    SEMESTERS.forEach(semester => {
      initialRows[semester.id] = 5;
    });
    setSemesterRows(initialRows);
  }, []);

  useEffect(() => {
    loadCourses();
    loadSelectedCourses();
    loadDepartments();
  }, [degreeAudits]);

  // Reload courses when department filter changes
  useEffect(() => {
    if (departments.length > 0) {
      loadCourses(selectedDepartment);
    }
  }, [selectedDepartment, departments]);

  const loadCourses = async (departmentFilter = '') => {
    try {
      setLoading(true);
      const params = {};
      if (departmentFilter) {
        params.department = departmentFilter;
      }
      const response = await coursesAPI.getCourses(params);
      // Simple admin API returns { success: true, courses: [...] }
      const coursesData = response.data.courses || response.data.results || response.data;
      setCourses(Array.isArray(coursesData) ? coursesData : []);
    } catch (error) {
      console.error('Error loading courses:', error);
      setCourses([]);
    } finally {
      setLoading(false);
    }
  };

  const loadDepartments = async () => {
    try {
      const response = await coursesAPI.getDepartments();
      // Simple admin API returns { success: true, departments: [...] }
      const departmentsData = response.data.departments || response.data.results || response.data;
      setDepartments(Array.isArray(departmentsData) ? departmentsData : []);
    } catch (error) {
      console.error('Error loading departments:', error);
      setDepartments([]);
    }
  };

  const loadSelectedCourses = async () => {
    if (!degreeAudits || degreeAudits.length === 0) return;
    
    try {
      const allSelections = [];
      for (const audit of degreeAudits) {
        const response = await schedulesAPI.getCourseSelections(audit.id);
        const selections = response.data.map(selection => ({
          ...selection,
          degree_audit_id: audit.id,
          program_name: audit.program
        }));
        allSelections.push(...selections);
      }
      setSelectedCourses(allSelections);
    } catch (error) {
      console.error('Error loading course selections:', error);
      setSelectedCourses([]);
    }
  };

  const handleCellClick = (semesterId, rowIndex) => {
    setSelectedCell({ semesterId, rowIndex });
    setShowAddDialog(true);
  };

  const handleAddCourse = async () => {
    if (selectedCourse && selectedCell && degreeAudits.length > 0) {
      try {
        const semester = SEMESTERS.find(s => s.id === selectedCell.semesterId);
        
        // Add course to the first available degree audit
        const degreeAudit = degreeAudits[0];
        
        // Check if course is already added to this degree audit
        const existingCourse = selectedCourses.find(course => 
          course.course_details?.id === selectedCourse.id && 
          course.degree_audit_id === degreeAudit.id
        );
        
        if (existingCourse) {
          alert('This course is already added to your degree plan.');
          return;
        }
        
        const courseData = {
          degree_audit: degreeAudit.id,
          course: selectedCourse.id,
          status: 'planned',
          semester_taken: `${semester.semester} ${semester.year}`,
          notes: `Row ${selectedCell.rowIndex + 1} in ${semester.name}`,
          timetable_box_id: `${selectedCell.semesterId}-${selectedCell.rowIndex}`
        };
        
        console.log('Adding course with data:', courseData);
        const response = await schedulesAPI.addCourseSelection(courseData);
        console.log('Course added successfully:', response.data);
        
        // Update local state
        const newCourse = {
          id: response.data.id || Date.now(), // Use real ID from response
          course_details: {
            id: selectedCourse.id,
            full_code: selectedCourse.full_code,
            title: selectedCourse.title,
            credits: selectedCourse.credits,
            department: selectedCourse.department
          },
          status: 'planned',
          semester_taken: `${semester.semester} ${semester.year}`,
          degree_audit_id: degreeAudit.id,
          program_name: degreeAudit.program,
          timetable_box_id: `${selectedCell.semesterId}-${selectedCell.rowIndex}`,
          row_index: selectedCell.rowIndex
        };
        
        setSelectedCourses(prev => [...prev, newCourse]);
        
        setShowAddDialog(false);
        setSelectedCourse(null);
        setSelectedCell(null);
        
        if (onUpdate) {
          onUpdate();
        }
      } catch (error) {
        console.error('Error adding course selection:', error);
        console.error('Error details:', error.response?.data);
        
        let errorMessage = 'Failed to add course. ';
        if (error.response?.data?.error) {
          errorMessage += error.response.data.error;
        } else if (error.response?.status === 400) {
          errorMessage += 'This course may already be added to your degree plan.';
        } else if (error.response?.status === 500) {
          errorMessage += 'Server error. Please try again.';
        } else {
          errorMessage += 'Please try again.';
        }
        
        alert(errorMessage);
      }
    }
  };

  const handleRemoveCourse = async (courseId) => {
    try {
      await schedulesAPI.deleteCourseSelection(courseId);
      
      // Update local state
      setSelectedCourses(prev => prev.filter(course => course.id !== courseId));
      
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      console.error('Error removing course selection:', error);
      alert('Failed to remove course. Please try again.');
    }
  };

  const handleStatusChange = async (courseId, newStatus) => {
    try {
      const course = selectedCourses.find(c => c.id === courseId);
      if (course) {
        await schedulesAPI.updateCourseSelection(courseId, {
          ...course,
          status: newStatus
        });
        
        // Update local state
        setSelectedCourses(prev => prev.map(c => 
          c.id === courseId ? { ...c, status: newStatus } : c
        ));
        
        if (onUpdate) {
          onUpdate();
        }
      }
    } catch (error) {
      console.error('Error updating course status:', error);
      alert('Failed to update course status. Please try again.');
    }
  };

  const handleAddRow = (semesterId) => {
    setSemesterRows(prev => ({
      ...prev,
      [semesterId]: (prev[semesterId] || 5) + 1
    }));
  };

  const handleDepartmentChange = (departmentCode) => {
    setSelectedDepartment(departmentCode);
    setSearchTerm(''); // Clear search when department changes
    setSelectedCourse(null); // Clear selected course
  };

  const filteredCourses = courses.filter(course => {
    // Only filter by search term since department filtering is done on backend
    const matchesSearch = !searchTerm || 
                         course.full_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.title.toLowerCase().includes(searchTerm.toLowerCase());
    // Exclude ENG department
    const isNotEng = course.department?.code !== 'ENG';
    return matchesSearch && isNotEng;
  });

  const getCourseInCell = (semesterId, rowIndex) => {
    return selectedCourses.find(course => 
      course.timetable_box_id === `${semesterId}-${rowIndex}`
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'warning';
      case 'planned': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon />;
      case 'in_progress': return <WarningIcon />;
      case 'planned': return <InfoIcon />;
      default: return <InfoIcon />;
    }
  };

  const calculateSemesterProgress = (semesterId) => {
    const semesterCourses = selectedCourses.filter(course => 
      course.semester_taken && course.semester_taken.includes(SEMESTERS.find(s => s.id === semesterId)?.semester)
    );
    const completedCourses = semesterCourses.filter(course => course.status === 'completed');
    const totalCredits = semesterCourses.reduce((sum, course) => 
      sum + parseFloat(course.course_details?.credits || 0), 0);
    const completedCredits = completedCourses.reduce((sum, course) => 
      sum + parseFloat(course.course_details?.credits || 0), 0);
    
    return {
      total: semesterCourses.length,
      completed: completedCourses.length,
      totalCredits,
      completedCredits,
      percentage: semesterCourses.length > 0 ? (completedCourses.length / semesterCourses.length) * 100 : 0
    };
  };

  return (
    <Box>
      {/* Semester Grid */}
      <TableContainer sx={{ overflow: 'auto', maxWidth: '100%' }}>
        <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell sx={{ minWidth: 120, fontWeight: 'bold' }}>Semester</TableCell>
                {SEMESTERS.map((semester) => {
                  const progress = calculateSemesterProgress(semester.id);
                  return (
                    <TableCell key={semester.id} sx={{ minWidth: 200, textAlign: 'center' }}>
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {semester.name}
                        </Typography>
                        {progress.total > 0 && (
                          <>
                            <Typography variant="caption" color="text.secondary">
                              {progress.completed}/{progress.total} courses
                            </Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={progress.percentage} 
                              sx={{ height: 4, borderRadius: 2, mt: 1 }}
                            />
                          </>
                        )}
                      </Box>
                    </TableCell>
                  );
                })}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: Math.max(...Object.values(semesterRows)) }, (_, rowIndex) => (
                <TableRow key={rowIndex}>
                  <TableCell sx={{ fontWeight: 'bold', minWidth: 60 }}>
                    {rowIndex + 1}
                  </TableCell>
                  {SEMESTERS.map((semester) => {
                    const course = getCourseInCell(semester.id, rowIndex);
                    const maxRowsForSemester = semesterRows[semester.id] || 5;
                    const isWithinMaxRows = rowIndex < maxRowsForSemester;
                    
                    return (
                      <TableCell key={`${semester.id}-${rowIndex}`} sx={{ textAlign: 'center', minHeight: 80 }}>
                        {isWithinMaxRows ? (
                          <Box
                            sx={{
                              minHeight: 60,
                              border: '2px dashed #ccc',
                              borderRadius: 2,
                              p: 1,
                              cursor: 'pointer',
                              transition: 'all 0.2s',
                              '&:hover': {
                                borderColor: 'primary.main',
                                backgroundColor: 'primary.light',
                                opacity: 0.1
                              }
                            }}
                            onClick={() => handleCellClick(semester.id, rowIndex)}
                          >
                            {course ? (
                              <Box sx={{ position: 'relative' }}>
                                {/* Close button */}
                                <IconButton
                                  size="small"
                                  sx={{
                                    position: 'absolute',
                                    top: -8,
                                    right: -8,
                                    backgroundColor: 'error.main',
                                    color: 'white',
                                    width: 20,
                                    height: 20,
                                    '&:hover': {
                                      backgroundColor: 'error.dark',
                                    }
                                  }}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleRemoveCourse(course.id);
                                  }}
                                >
                                  <CloseIcon sx={{ fontSize: 12 }} />
                                </IconButton>
                                
                                <Typography variant="body2" fontWeight="bold" noWrap>
                                  {course.course_details?.full_code || course.course}
                                </Typography>
                                <Typography variant="caption" color="text.secondary" noWrap>
                                  {course.course_details?.title || 'N/A'}
                                </Typography>
                                <Box mt={1}>
                                  <Chip
                                    icon={getStatusIcon(course.status)}
                                    label={course.status.replace('_', ' ')}
                                    color={getStatusColor(course.status)}
                                    size="small"
                                    sx={{ mb: 1 }}
                                  />
                                </Box>
                                <Box display="flex" justifyContent="center" gap={1}>
                                  <FormControl size="small" sx={{ minWidth: 80 }}>
                                    <Select
                                      value={course.status}
                                      onChange={(e) => handleStatusChange(course.id, e.target.value)}
                                      onClick={(e) => e.stopPropagation()}
                                    >
                                      <MenuItem value="planned">Planned</MenuItem>
                                      <MenuItem value="in_progress">In Progress</MenuItem>
                                      <MenuItem value="completed">Completed</MenuItem>
                                    </Select>
                                  </FormControl>
                                </Box>
                              </Box>
                            ) : (
                              <Box 
                                display="flex" 
                                alignItems="center" 
                                justifyContent="center" 
                                height="100%"
                                color="text.secondary"
                              >
                                <Typography variant="caption">
                                  Click to add course
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        ) : (
                          // Show Add button if this semester has been expanded beyond default 5 rows
                          semesterRows[semester.id] > 5 ? (
                            <Box 
                              sx={{ 
                                position: 'relative',
                                minHeight: 60,
                                border: '2px dashed #ccc',
                                borderRadius: 2,
                                p: 1,
                                display: 'flex',
                                flexDirection: 'column',
                                justifyContent: 'center',
                                alignItems: 'center'
                              }}
                            >
                              {/* Cross mark in top-right corner */}
                              <Box
                                sx={{
                                  position: 'absolute',
                                  top: -8,
                                  right: -8,
                                  width: 20,
                                  height: 20,
                                  borderRadius: '50%',
                                  backgroundColor: '#ccc',
                                  color: 'white',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  cursor: 'pointer',
                                  fontSize: '12px',
                                  fontWeight: 'bold',
                                  '&:hover': {
                                    backgroundColor: '#999',
                                  }
                                }}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (window.confirm(`Delete row ${rowIndex + 1} from ${semester.name}?`)) {
                                    setSemesterRows(prev => ({
                                      ...prev,
                                      [semester.id]: Math.max(5, prev[semester.id] - 1)
                                    }));
                                  }
                                }}
                              >
                                ✕
                              </Box>
                              
                              <Button
                                size="small"
                                variant="outlined"
                                startIcon={<AddIcon />}
                                onClick={() => handleAddRow(semester.id)}
                              >
                                Add
                              </Button>
                            </Box>
                          ) : (
                            // Show blank cell for semesters that haven't been expanded
                            <Box sx={{ minHeight: 60 }} />
                          )
                        )}
                        
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
            </TableBody>
            {/* Bottom row with Add buttons for each semester */}
            <TableBody>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold', minWidth: 60 }}>
                  Actions
                </TableCell>
                {SEMESTERS.map((semester) => {
                  return (
                    <TableCell key={`actions-${semester.id}`} sx={{ textAlign: 'center', minHeight: 80 }}>
                      <Box display="flex" gap={1} justifyContent="center" flexDirection="column" alignItems="center">
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<AddIcon />}
                          onClick={() => handleAddRow(semester.id)}
                          sx={{ fontSize: '0.75rem', mb: 1 }}
                        >
                          Add
                        </Button>
                      </Box>
                    </TableCell>
                  );
                })}
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>


      {/* Add Course Dialog */}
      <Dialog open={showAddDialog} onClose={() => setShowAddDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Add Course
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {/* Filter and Course Search on same row */}
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              {/* Department Filter */}
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel>Filter by Department</InputLabel>
                <Select
                  value={selectedDepartment || ''}
                  onChange={(e) => handleDepartmentChange(e.target.value)}
                  label="Filter by Department"
                >
                  <MenuItem value="">All Departments</MenuItem>
                  {departments.filter(dept => dept.code !== 'ENG').map(dept => (
                    <MenuItem key={dept.id} value={dept.code}>
                      {dept.code} - {dept.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Course Search */}
              <Autocomplete
                options={filteredCourses}
                getOptionLabel={(option) => `${option.full_code} - ${option.title}`}
                value={selectedCourse}
                onChange={(event, newValue) => setSelectedCourse(newValue)}
                sx={{ flex: 1 }}
                loading={loading}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Search and Select Course"
                    placeholder={selectedDepartment ? `Search ${selectedDepartment} courses...` : "Type to search courses..."}
                    InputProps={{
                      ...params.InputProps,
                      startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                      endAdornment: (
                        <>
                          {loading ? <CircularProgress color="inherit" size={20} /> : null}
                          {params.InputProps.endAdornment}
                        </>
                      ),
                    }}
                  />
                )}
                renderOption={(props, option) => (
                  <Box component="li" {...props}>
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {option.full_code}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {option.title} ({option.credits} credits) - {option.department?.code || 'N/A'}
                      </Typography>
                    </Box>
                  </Box>
                )}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAddDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleAddCourse} 
            variant="contained"
            disabled={!selectedCourse}
          >
            Add Course
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SemesterGrid;
