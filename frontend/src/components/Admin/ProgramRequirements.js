import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
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
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Autocomplete,
  FormControlLabel,
  Switch
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { adminAPI } from '../../services/api';

const ProgramRequirements = ({ programId, onClose }) => {
  const [requirements, setRequirements] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingRequirement, setEditingRequirement] = useState(null);
  const [expandedRequirements, setExpandedRequirements] = useState({});

  const [formData, setFormData] = useState({
    name: '',
    requirement_type: 'course_group',
    description: '',
    courses_required: 1,
    minimum_level: null,
    maximum_courses: null,
    subject_codes: [],
    require_different_subjects: false,
    minimum_subjects: 1,
    order: 0,
    is_required: true,
    parent_requirement: null,
    selected_courses: [],
    is_parent: false
  });

  useEffect(() => {
    if (programId) {
      loadRequirements();
      loadCourses();
    }
  }, [programId]);

  const loadRequirements = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getProgramRequirements(programId);
      setRequirements(response.data.requirements || []);
    } catch (error) {
      setError('Failed to load requirements');
      console.error('Load requirements error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCourses = async () => {
    try {
      const response = await adminAPI.getAdminCourses({ page_size: 1000 });
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('Load courses error:', error);
    }
  };

  const handleAddRequirement = (parentRequirement = null) => {
    setEditingRequirement(null);
    setFormData({
      name: '',
      requirement_type: 'course_group',
      description: '',
      courses_required: 1,
      minimum_level: null,
      maximum_courses: null,
      subject_codes: [],
      require_different_subjects: false,
      minimum_subjects: 1,
      order: requirements.length,
      is_required: true,
      parent_requirement: parentRequirement ? parentRequirement.id : null,
      selected_courses: [],
      is_parent: !parentRequirement
    });
    setDialogOpen(true);
  };

  const handleEditRequirement = (requirement) => {
    setEditingRequirement(requirement);
    setFormData({
      name: requirement.name,
      requirement_type: requirement.requirement_type,
      description: requirement.description,
      courses_required: requirement.courses_required || 1,
      minimum_level: requirement.minimum_level,
      maximum_courses: requirement.maximum_courses,
      subject_codes: requirement.subject_codes || [],
      require_different_subjects: requirement.require_different_subjects || false,
      minimum_subjects: requirement.minimum_subjects || 1,
      order: requirement.order,
      is_required: requirement.is_required,
      parent_requirement: requirement.parent_requirement,
      selected_courses: requirement.course_requirements ? requirement.course_requirements.map(cr => cr.course) : [],
      is_parent: !requirement.parent_requirement
    });
    setDialogOpen(true);
  };

  const handleSaveRequirement = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      const requirementData = {
        ...formData,
        program_id: programId,
        courses: formData.selected_courses.map(course => `${course.department.code}${course.course_number}`)
      };

      console.log('Saving requirement:', requirementData);
      console.log('Editing requirement:', editingRequirement);

      if (editingRequirement) {
        console.log('Updating requirement with ID:', editingRequirement.id);
        const response = await adminAPI.updateProgramRequirement(editingRequirement.id, requirementData);
        console.log('Update response:', response);
        setSuccess('Requirement updated successfully');
      } else {
        console.log('Creating new requirement');
        const response = await adminAPI.createProgramRequirement(requirementData);
        console.log('Create response:', response);
        setSuccess('Requirement created successfully');
      }

      setDialogOpen(false);
      loadRequirements();
    } catch (error) {
      console.error('Save requirement error:', error);
      setError(`Failed to save requirement: ${error.message || error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRequirement = async (requirementId) => {
    if (window.confirm('Are you sure you want to delete this requirement?')) {
      try {
        setLoading(true);
        setError('');
        setSuccess('');
        
        console.log('Deleting requirement with ID:', requirementId);
        const response = await adminAPI.deleteProgramRequirement(requirementId);
        console.log('Delete response:', response);
        setSuccess('Requirement deleted successfully');
        loadRequirements();
      } catch (error) {
        console.error('Delete requirement error:', error);
        setError(`Failed to delete requirement: ${error.message || error}`);
      } finally {
        setLoading(false);
      }
    }
  };

  const toggleRequirement = (requirementId) => {
    setExpandedRequirements(prev => ({
      ...prev,
      [requirementId]: !prev[requirementId]
    }));
  };

  const getRequirementTypeLabel = (type) => {
    const labels = {
      'course_group': 'Course Group',
      'subject_requirement': 'Subject Requirement',
      'credit_requirement': 'Credit Requirement',
      'average_requirement': 'Average Requirement',
      'level_requirement': 'Level Requirement'
    };
    return labels[type] || type;
  };

  const getParentRequirements = () => {
    return requirements.filter(req => !req.parent_requirement);
  };

  const renderRequirementCard = (requirement) => {
    const isExpanded = expandedRequirements[requirement.id];
    
    return (
      <Card key={requirement.id} sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              {requirement.name}
              {requirement.parent_requirement && (
                <Chip 
                  label="Sub-requirement" 
                  size="small" 
                  color="info" 
                  sx={{ ml: 1 }}
                />
              )}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip 
                label={getRequirementTypeLabel(requirement.requirement_type)} 
                size="small" 
                color="primary" 
              />
              {requirement.courses_required && (
                <Chip 
                  label={`${requirement.courses_required} required`} 
                  size="small" 
                  color="secondary" 
                />
              )}
              {requirement.sub_requirements && requirement.sub_requirements.length > 0 && (
                <Chip 
                  label={`${requirement.sub_requirements.length} sub-requirements`} 
                  size="small" 
                  color="success" 
                />
              )}
              <IconButton 
                onClick={() => toggleRequirement(requirement.id)}
                size="small"
              >
                <ExpandMoreIcon 
                  sx={{ 
                    transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.3s'
                  }}
                />
              </IconButton>
            </Box>
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {requirement.description}
          </Typography>
          
          {requirement.course_requirements && requirement.course_requirements.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Courses ({requirement.course_requirements.length}):
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {requirement.course_requirements.map((courseReq, index) => (
                  <Chip 
                    key={index} 
                    label={`${courseReq.course.department.code} ${courseReq.course.course_number} - ${courseReq.course.title}`} 
                    size="small" 
                    variant="outlined"
                    color="primary"
                  />
                ))}
              </Box>
            </Box>
          )}
          
          {requirement.sub_requirements && requirement.sub_requirements.length > 0 && (
            <Box sx={{ mt: 2, ml: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
                Sub-requirements:
              </Typography>
              {requirement.sub_requirements.map((subReq, index) => (
                <Box key={subReq.id} sx={{ mb: 1, pl: 2, borderLeft: '2px solid', borderColor: 'primary.light' }}>
                  <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                    {subReq.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {subReq.description}
                  </Typography>
                  {subReq.course_requirements && subReq.course_requirements.length > 0 && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                        Courses ({subReq.course_requirements.length}):
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {subReq.course_requirements.map((courseReq, courseIndex) => (
                          <Chip 
                            key={courseIndex} 
                            label={`${courseReq.course.department.code} ${courseReq.course.course_number}`} 
                            size="small" 
                            variant="outlined"
                            color="secondary"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                  <Box sx={{ mt: 1, display: 'flex', gap: 0.5 }}>
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<EditIcon />}
                      onClick={() => handleEditRequirement(subReq)}
                      sx={{ fontSize: '0.75rem', py: 0.5, px: 1 }}
                    >
                      Edit
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={() => handleDeleteRequirement(subReq.id)}
                      sx={{ fontSize: '0.75rem', py: 0.5, px: 1 }}
                    >
                      Delete
                    </Button>
                  </Box>
                </Box>
              ))}
            </Box>
          )}

          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end', mt: 2 }}>
            {!requirement.parent_requirement && (
              <Button
                variant="outlined"
                size="small"
                startIcon={<AddIcon />}
                onClick={() => handleAddRequirement(requirement)}
                color="secondary"
              >
                Add Sub-requirement
              </Button>
            )}
            <Button
              variant="outlined"
              size="small"
              startIcon={<EditIcon />}
              onClick={() => handleEditRequirement(requirement)}
            >
              Edit
            </Button>
            <Button
              variant="outlined"
              size="small"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => handleDeleteRequirement(requirement.id)}
            >
              Delete
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">
          Program Requirements
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddRequirement}
        >
          Add Requirement
        </Button>
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

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {requirements.length === 0 && !loading ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center">
              No requirements found. Add a requirement to get started.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Box>
          {getParentRequirements().map(requirement => renderRequirementCard(requirement))}
        </Box>
      )}

      {/* Add/Edit Requirement Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingRequirement ? 'Edit Requirement' : 'Add Requirement'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Requirement Name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Requirement Type</InputLabel>
                <Select
                  value={formData.requirement_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, requirement_type: e.target.value }))}
                  label="Requirement Type"
                >
                  <MenuItem value="course_group">Course Group</MenuItem>
                  <MenuItem value="subject_requirement">Subject Requirement</MenuItem>
                  <MenuItem value="credit_requirement">Credit Requirement</MenuItem>
                  <MenuItem value="average_requirement">Average Requirement</MenuItem>
                  <MenuItem value="level_requirement">Level Requirement</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Courses Required"
                type="number"
                value={formData.courses_required}
                onChange={(e) => setFormData(prev => ({ ...prev, courses_required: parseInt(e.target.value) || 1 }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Order"
                type="number"
                value={formData.order}
                onChange={(e) => setFormData(prev => ({ ...prev, order: parseInt(e.target.value) || 0 }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Parent Requirement</InputLabel>
                <Select
                  value={formData.parent_requirement || ''}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    parent_requirement: e.target.value || null,
                    is_parent: !e.target.value
                  }))}
                  label="Parent Requirement"
                >
                  <MenuItem value="">None (Top Level)</MenuItem>
                  {getParentRequirements().map((req) => (
                    <MenuItem key={req.id} value={req.id}>
                      {req.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Minimum Level"
                type="number"
                value={formData.minimum_level || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, minimum_level: e.target.value ? parseInt(e.target.value) : null }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Maximum Courses"
                type="number"
                value={formData.maximum_courses || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, maximum_courses: e.target.value ? parseInt(e.target.value) : null }))}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.require_different_subjects}
                    onChange={(e) => setFormData(prev => ({ ...prev, require_different_subjects: e.target.checked }))}
                  />
                }
                label="Require Different Subjects"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_required}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_required: e.target.checked }))}
                  />
                }
                label="Required"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: 'primary.main' }}>
                📚 Course Selection
              </Typography>
              <Autocomplete
                multiple
                options={courses}
                getOptionLabel={(option) => `${option.department.code} ${option.course_number} - ${option.title}`}
                value={formData.selected_courses}
                onChange={(event, newValue) => {
                  setFormData(prev => ({ ...prev, selected_courses: newValue }));
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Select Courses"
                    placeholder="Choose courses for this requirement"
                    helperText={formData.parent_requirement ? "Select courses for this sub-requirement" : "Select courses for this requirement"}
                  />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      {...getTagProps({ index })}
                      key={option.id}
                      label={`${option.department.code} ${option.course_number}`}
                      size="small"
                      color="primary"
                    />
                  ))
                }
                filterSelectedOptions
                isOptionEqualToValue={(option, value) => option.id === value.id}
              />
              {formData.selected_courses.length > 0 && (
                <Typography variant="caption" color="success.main" sx={{ mt: 1, display: 'block' }}>
                  ✅ {formData.selected_courses.length} course(s) selected
                </Typography>
              )}
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleSaveRequirement}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
          >
            {editingRequirement ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProgramRequirements;
