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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  Autocomplete,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { adminAPI } from '../../services/api';

const CourseManagement = () => {
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [degreePrograms, setDegreePrograms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Filter states
  const [filters, setFilters] = useState({
    department: ''
  });
  
  // Dialog states
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);
  
  // Predefined options
  const courseCodes = ['ACTSC', 'AMATH', 'CO', 'CS', 'MATBUS', 'MATH', 'PMATH', 'STAT'];
  const creditOptions = [0.25, 0.5, 0.75, 1.0];
  const termOptions = ['fall', 'winter', 'spring'];
  
  // Form data
  const [formData, setFormData] = useState({
    department_code: '',
    course_number: '',
    title: '',
    description: '',
    credits: '',
    is_active: true,
    terms_offered: [],
    prerequisites: [],
    prerequisite_groups: [],
    corequisites: [],
    antirequisites: [],
    restricted_to_majors: [],
  });

  useEffect(() => {
    // Don't load courses by default - only load when department filter is selected
    loadDepartmentsAndPrograms();
  }, []);

  // Handle department filter change
  const handleDepartmentFilter = (department) => {
    setFilters(prev => ({ ...prev, department }));
    if (department === '') {
      // Clear courses when "All" is selected
      setCourses([]);
      setFilteredCourses([]);
    } else {
      // Load courses for specific department
      loadData(1, department);
    }
  };

  const loadDepartmentsAndPrograms = async () => {
    try {
      setLoading(true);
      const [departmentsRes, degreeProgramsRes] = await Promise.all([
        adminAPI.getAdminDepartments(),
        adminAPI.getAdminDegreePrograms(),
      ]);
      
      setDepartments(departmentsRes.data.departments || []);
      setDegreePrograms(degreeProgramsRes.data.degree_programs || []);
    } catch (error) {
      setError('Failed to load departments and programs');
      console.error('Load data error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadData = async (page = 1, department = '') => {
    try {
      setLoading(true);
      const coursesRes = await adminAPI.getAdminCourses({ 
        page, 
        page_size: 100, 
        department 
      });
      
      const coursesData = coursesRes.data.courses || [];
      setCourses(coursesData);
      setFilteredCourses(coursesData);
    } catch (error) {
      setError('Failed to load courses');
      console.error('Load data error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (course = null) => {
    setEditingCourse(course);
    if (course) {
      setFormData({
        department_code: course.department?.code || '',
        course_number: course.course_number,
        title: course.title,
        description: course.description,
        credits: course.credits,
        is_active: course.is_active,
        terms_offered: course.terms_offered || [],
        prerequisites: course.prerequisites || [],
        prerequisite_groups: course.prerequisite_groups || [],
        corequisites: course.corequisites || [],
        antirequisites: course.antirequisites || [],
        restricted_to_majors: course.restricted_to_majors || [],
      });
    } else {
      setFormData({
        department_code: '',
        course_number: '',
        title: '',
        description: '',
        credits: '',
        is_active: true,
        terms_offered: [],
        prerequisites: [],
        prerequisite_groups: [],
        corequisites: [],
        antirequisites: [],
        restricted_to_majors: [],
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingCourse(null);
    setError('');
    setSuccess('');
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const addPrerequisiteGroup = () => {
    const newGroup = {
      id: `temp_${Date.now()}`,
      name: '',
      description: '',
      is_required: true,
      courses: []
    };
    setFormData(prev => ({
      ...prev,
      prerequisite_groups: [...prev.prerequisite_groups, newGroup]
    }));
  };

  const updatePrerequisiteGroup = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      prerequisite_groups: prev.prerequisite_groups.map((group, i) => 
        i === index ? { ...group, [field]: value } : group
      )
    }));
  };

  const removePrerequisiteGroup = (index) => {
    setFormData(prev => ({
      ...prev,
      prerequisite_groups: prev.prerequisite_groups.filter((_, i) => i !== index)
    }));
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      // Find department by code
      const department = departments.find(d => d.code === formData.department_code);
      if (!department) {
        setError('Please select a valid department');
        return;
      }
      
      const courseData = {
        department_id: department.id,
        course_number: formData.course_number,
        title: formData.title,
        description: formData.description,
        credits: parseFloat(formData.credits),
        is_active: formData.is_active,
        terms_offered: formData.terms_offered,
        prerequisites: formData.prerequisites.filter(p => p.id !== 'none').map(p => p.id),
        corequisites: formData.corequisites.filter(c => c.id !== 'none').map(c => c.id),
        antirequisites: formData.antirequisites.filter(a => a.id !== 'none').map(a => a.id),
        restricted_to_majors: formData.restricted_to_majors.map(m => m.id),
      };
      
      let response;
      if (editingCourse) {
        response = await adminAPI.updateAdminCourse(editingCourse.id, courseData);
      } else {
        response = await adminAPI.createAdminCourse(courseData);
      }
      
      if (response.data.success) {
        setSuccess(editingCourse ? 'Course updated successfully' : 'Course created successfully');
        await loadData();
        handleCloseDialog();
      } else {
        setError(response.data.error || 'Failed to save course');
      }
    } catch (error) {
      setError('Failed to save course');
      console.error('Save course error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (courseId) => {
    if (!window.confirm('Are you sure you want to delete this course?')) {
      return;
    }
    
    try {
      setLoading(true);
      const response = await adminAPI.deleteAdminCourse(courseId);
      if (response.data.success) {
        setSuccess('Course deleted successfully');
        await loadData();
      } else {
        setError(response.data.error || 'Failed to delete course');
      }
    } catch (error) {
      setError('Failed to delete course');
      console.error('Delete course error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading && courses.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Course Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Course
        </Button>
      </Box>

      {/* Results Counter */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Showing {filteredCourses.length} of {courses.length} courses
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Typography variant="subtitle2" fontWeight="bold">
                        Course Code
                      </Typography>
                      <FormControl size="small" sx={{ minWidth: 120 }}>
                        <Select
                          value={filters.department}
                          onChange={(e) => handleDepartmentFilter(e.target.value)}
                          displayEmpty
                          sx={{ 
                            '& .MuiSelect-select': { 
                              padding: '6px 8px',
                              fontSize: '0.875rem'
                            }
                          }}
                        >
                          <MenuItem value="">All</MenuItem>
                          {departments
                            .filter(dept => dept.code !== 'ENG')
                            .sort((a, b) => a.code.localeCompare(b.code))
                            .map((dept) => (
                              <MenuItem key={dept.id} value={dept.code}>
                                {dept.code}
                              </MenuItem>
                            ))}
                        </Select>
                      </FormControl>
                    </Box>
                  </TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Credits</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Prerequisites</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredCourses.length === 0 && !loading ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                      <Typography variant="body1" color="text.secondary">
                        {filters.department 
                          ? `No courses found for ${filters.department} department`
                          : 'Select a department to view courses'
                        }
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredCourses.map((course) => (
                  <TableRow key={course.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {course.full_code}
                      </Typography>
                    </TableCell>
                    <TableCell>{course.title}</TableCell>
                    <TableCell>{course.department.name}</TableCell>
                    <TableCell>{course.credits}</TableCell>
                    <TableCell>
                      <Chip
                        label={course.is_active ? 'Active' : 'Inactive'}
                        color={course.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {course.prerequisites && course.prerequisites.length > 0 ? (
                        <Typography variant="caption">
                          {course.prerequisites.length} prerequisite(s)
                        </Typography>
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          None
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Edit Course">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(course)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Course">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDelete(course.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Course Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingCourse ? 'Edit Course' : 'Add New Course'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Department Code</InputLabel>
                <Select
                  name="department_code"
                  value={formData.department_code}
                  onChange={handleChange}
                  label="Department Code"
                >
                  {courseCodes.map((code) => (
                    <MenuItem key={code} value={code}>
                      {code}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Course Number"
                name="course_number"
                value={formData.course_number}
                onChange={handleChange}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Course Title"
                name="title"
                value={formData.title}
                onChange={handleChange}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                multiline
                rows={3}
                value={formData.description}
                onChange={handleChange}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Credits</InputLabel>
                <Select
                  name="credits"
                  value={formData.credits}
                  onChange={handleChange}
                  label="Credits"
                >
                  {creditOptions.map((credit) => (
                    <MenuItem key={credit} value={credit}>
                      {credit}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Terms Offered</InputLabel>
                <Select
                  multiple
                  name="terms_offered"
                  value={formData.terms_offered}
                  onChange={handleChange}
                  label="Terms Offered"
                  renderValue={(selected) => selected.map(term => term.charAt(0).toUpperCase() + term.slice(1)).join(', ')}
                >
                  {termOptions.map((term) => (
                    <MenuItem key={term} value={term}>
                      {term.charAt(0).toUpperCase() + term.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={handleChange}
                    name="is_active"
                  />
                }
                label="Active"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={[
                  { id: 'none', full_code: 'None', title: 'No prerequisites' },
                  ...courses.filter(c => c.id !== editingCourse?.id)
                ]}
                getOptionLabel={(option) => `${option.full_code} - ${option.title}`}
                value={formData.prerequisites}
                onChange={(event, newValue) => {
                  // Filter out "None" if other courses are selected
                  const filteredValue = newValue.filter(item => 
                    item.id !== 'none' || newValue.length === 1
                  );
                  setFormData(prev => ({ ...prev, prerequisites: filteredValue }));
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Prerequisites (Individual)"
                    placeholder="Select prerequisite courses or None"
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  Prerequisite Groups (One of Multiple)
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={addPrerequisiteGroup}
                  size="small"
                >
                  Add Group
                </Button>
              </Box>
              
              {formData.prerequisite_groups.map((group, index) => (
                <Card key={group.id} sx={{ mb: 2, p: 2 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Group Name"
                        value={group.name}
                        onChange={(e) => updatePrerequisiteGroup(index, 'name', e.target.value)}
                        placeholder="e.g., Statistics Requirement"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={group.is_required}
                            onChange={(e) => updatePrerequisiteGroup(index, 'is_required', e.target.checked)}
                          />
                        }
                        label="Required"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Description"
                        value={group.description}
                        onChange={(e) => updatePrerequisiteGroup(index, 'description', e.target.value)}
                        placeholder="Description of this requirement group"
                        multiline
                        rows={2}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Autocomplete
                        multiple
                        options={courses.filter(c => c.id !== editingCourse?.id)}
                        getOptionLabel={(option) => `${option.full_code} - ${option.title}`}
                        value={group.courses}
                        onChange={(event, newValue) => {
                          updatePrerequisiteGroup(index, 'courses', newValue);
                        }}
                        renderInput={(params) => (
                          <TextField
                            {...params}
                            label="Courses (One of these)"
                            placeholder="Select courses for this group"
                          />
                        )}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Button
                        variant="outlined"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={() => removePrerequisiteGroup(index)}
                        size="small"
                      >
                        Remove Group
                      </Button>
                    </Grid>
                  </Grid>
                </Card>
              ))}
            </Grid>
            
            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={[
                  { id: 'none', full_code: 'None', title: 'No corequisites' },
                  ...courses.filter(c => c.id !== editingCourse?.id)
                ]}
                getOptionLabel={(option) => `${option.full_code} - ${option.title}`}
                value={formData.corequisites}
                onChange={(event, newValue) => {
                  // Filter out "None" if other courses are selected
                  const filteredValue = newValue.filter(item => 
                    item.id !== 'none' || newValue.length === 1
                  );
                  setFormData(prev => ({ ...prev, corequisites: filteredValue }));
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Corequisites"
                    placeholder="Select corequisite courses or None"
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={[
                  { id: 'none', full_code: 'None', title: 'No antirequisites' },
                  ...courses.filter(c => c.id !== editingCourse?.id)
                ]}
                getOptionLabel={(option) => `${option.full_code} - ${option.title}`}
                value={formData.antirequisites}
                onChange={(event, newValue) => {
                  // Filter out "None" if other courses are selected
                  const filteredValue = newValue.filter(item => 
                    item.id !== 'none' || newValue.length === 1
                  );
                  setFormData(prev => ({ ...prev, antirequisites: filteredValue }));
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Antirequisites"
                    placeholder="Select antirequisite courses or None"
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={degreePrograms}
                getOptionLabel={(option) => option.name}
                value={formData.restricted_to_majors}
                onChange={(event, newValue) => {
                  setFormData(prev => ({ ...prev, restricted_to_majors: newValue }));
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Restricted to Majors"
                    placeholder="Select majors (leave empty for all majors)"
                  />
                )}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CourseManagement;
