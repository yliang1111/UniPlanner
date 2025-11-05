import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  School as SchoolIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { adminAPI } from '../../services/api';
import { usePageTitle } from '../../hooks/usePageTitle';
import ProgramRequirements from './ProgramRequirements';

const ProgramManagement = () => {
  const [programs, setPrograms] = useState([]);
  const [programTypes, setProgramTypes] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Dialog states
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProgram, setEditingProgram] = useState(null);
  const [requirementsDialogOpen, setRequirementsDialogOpen] = useState(false);
  const [selectedProgramForRequirements, setSelectedProgramForRequirements] = useState(null);

  // Form data
  const [formData, setFormData] = useState({
    name: '',
    program_type_id: '',
    code: '',
    description: '',
    minimum_overall_average: '',
    minimum_major_average: '',
    total_credits_required: '',
    co_op_available: false,
    honours_available: false,
    is_active: true,
  });


  usePageTitle('Program Management');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [programsRes, programTypesRes, coursesRes] = await Promise.all([
        adminAPI.getPrograms(),
        adminAPI.getProgramTypes(),
        adminAPI.getAdminCourses(),
      ]);

      setPrograms(programsRes.data.programs || []);
      setProgramTypes(programTypesRes.data.program_types || []);
      setCourses(coursesRes.data.courses || []);
    } catch (error) {
      setError('Failed to load data');
      console.error('Load data error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (program = null) => {
    setEditingProgram(program);
    if (program) {
      setFormData({
        name: program.name,
        program_type_id: program.program_type.id,
        code: program.code,
        description: program.description,
        minimum_overall_average: program.minimum_overall_average || '',
        minimum_major_average: program.minimum_major_average || '',
        total_credits_required: program.total_credits_required || '',
        co_op_available: program.co_op_available,
        honours_available: program.honours_available,
        is_active: program.is_active,
      });
    } else {
      setFormData({
        name: '',
        program_type_id: '',
        code: '',
        description: '',
        minimum_overall_average: '',
        minimum_major_average: '',
        total_credits_required: '',
        co_op_available: false,
        honours_available: false,
        is_active: true,
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingProgram(null);
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

  const handleSave = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const programData = {
        ...formData,
        minimum_overall_average: formData.minimum_overall_average ? parseFloat(formData.minimum_overall_average) : null,
        minimum_major_average: formData.minimum_major_average ? parseFloat(formData.minimum_major_average) : null,
        total_credits_required: formData.total_credits_required ? parseFloat(formData.total_credits_required) : 0,
      };

      let response;
      if (editingProgram) {
        response = await adminAPI.updateProgram(editingProgram.id, programData);
      } else {
        response = await adminAPI.createProgram(programData);
      }

      if (response.data.success) {
        setSuccess(editingProgram ? 'Program updated successfully' : 'Program created successfully');
        await loadData();
        handleCloseDialog();
      } else {
        setError(response.data.error || 'Failed to save program');
      }
    } catch (error) {
      setError('Failed to save program');
      console.error('Save program error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (programId) => {
    if (!window.confirm('Are you sure you want to delete this program?')) {
      return;
    }

    try {
      setLoading(true);
      const response = await adminAPI.deleteProgram(programId);
      if (response.data.success) {
        setSuccess('Program deleted successfully');
        await loadData();
      } else {
        setError(response.data.error || 'Failed to delete program');
      }
    } catch (error) {
      setError('Failed to delete program');
      console.error('Delete program error:', error);
    } finally {
      setLoading(false);
    }
  };


  const handleManageRequirements = (program) => {
    setSelectedProgramForRequirements(program);
    setRequirementsDialogOpen(true);
  };

  const handleCloseRequirementsDialog = () => {
    setRequirementsDialogOpen(false);
    setSelectedProgramForRequirements(null);
  };


  if (loading && programs.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Program Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Program
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {programs.map((program) => (
          <Grid item xs={12} md={6} lg={4} key={program.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Typography variant="h6" component="h2">
                      {program.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {program.program_type.display_name}
                    </Typography>
                    <Chip 
                      label={program.code} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                      sx={{ mt: 1 }}
                    />
                  </Box>
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(program)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    {/* Requirements Management Button */}
                    <IconButton
                      size="small"
                      onClick={() => handleManageRequirements(program)}
                      color="secondary"
                      title="Manage Requirements"
                    >
                      <SchoolIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(program.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>

                <Typography variant="body2" sx={{ mb: 2 }}>
                  {program.description}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Credits Required:</strong> {program.total_credits_required}
                  </Typography>
                  {program.minimum_overall_average && (
                    <Typography variant="body2" color="text.secondary">
                      <strong>Min Overall Average:</strong> {program.minimum_overall_average}%
                    </Typography>
                  )}
                  {program.minimum_major_average && (
                    <Typography variant="body2" color="text.secondary">
                      <strong>Min Major Average:</strong> {program.minimum_major_average}%
                    </Typography>
                  )}
                </Box>

                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  {program.co_op_available && (
                    <Chip label="Co-op" size="small" color="info" variant="outlined" />
                  )}
                  {program.honours_available && (
                    <Chip label="Honours" size="small" color="secondary" variant="outlined" />
                  )}
                  <Chip 
                    label={program.is_active ? 'Active' : 'Inactive'} 
                    size="small" 
                    color={program.is_active ? 'success' : 'default'} 
                    variant="outlined" 
                  />
                </Box>


              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Program Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingProgram ? 'Edit Program' : 'Add New Program'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Program Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Program Code"
                name="code"
                value={formData.code}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Program Type</InputLabel>
                <Select
                  name="program_type_id"
                  value={formData.program_type_id}
                  onChange={handleChange}
                  label="Program Type"
                  required
                >
                  {programTypes.map((type) => (
                    <MenuItem key={type.id} value={type.id}>
                      {type.display_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
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
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Total Credits Required"
                name="total_credits_required"
                type="number"
                value={formData.total_credits_required}
                onChange={handleChange}
                inputProps={{ step: 0.5, min: 0 }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Minimum Overall Average (%)"
                name="minimum_overall_average"
                type="number"
                value={formData.minimum_overall_average}
                onChange={handleChange}
                inputProps={{ step: 0.1, min: 0, max: 100 }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Minimum Major Average (%)"
                name="minimum_major_average"
                type="number"
                value={formData.minimum_major_average}
                onChange={handleChange}
                inputProps={{ step: 0.1, min: 0, max: 100 }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.co_op_available}
                    onChange={handleChange}
                    name="co_op_available"
                  />
                }
                label="Co-op Available"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.honours_available}
                    onChange={handleChange}
                    name="honours_available"
                  />
                }
                label="Honours Available"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
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
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleSave} color="primary" variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Save Program'}
          </Button>
        </DialogActions>
      </Dialog>


      {/* Requirements Management Dialog */}
      <Dialog 
        open={requirementsDialogOpen} 
        onClose={handleCloseRequirementsDialog} 
        maxWidth="lg" 
        fullWidth
      >
        <DialogTitle>
          Manage Requirements - {selectedProgramForRequirements?.name}
        </DialogTitle>
        <DialogContent>
          {selectedProgramForRequirements && (
            <ProgramRequirements 
              programId={selectedProgramForRequirements.id}
              onClose={handleCloseRequirementsDialog}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseRequirementsDialog}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProgramManagement;
