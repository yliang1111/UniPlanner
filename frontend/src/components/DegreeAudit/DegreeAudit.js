import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  Button,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Autocomplete,
  Tabs,
  Tab,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  School as SchoolIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Assignment as AssignmentIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { coursesAPI, schedulesAPI } from '../../services/api';
import SemesterGrid from './SemesterGrid';
const DegreeAudit = () => {
  const [degreeAudits, setDegreeAudits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [availablePrograms, setAvailablePrograms] = useState([]);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [enrolling, setEnrolling] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    loadDegreeAudits();
    loadAvailablePrograms();
  }, []);

  const loadDegreeAudits = async () => {
    try {
      setLoading(true);
      const response = await schedulesAPI.getDegreeAudits();
      // Handle both direct array response and paginated response
      const audits = response.data.results || response.data;
      setDegreeAudits(Array.isArray(audits) ? audits : []);
    } catch (error) {
      console.error('Error loading degree audits:', error);
      setDegreeAudits([]);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailablePrograms = async () => {
    try {
      const response = await coursesAPI.getPrograms();
      // Handle both direct array response and paginated response
      const programs = response.data.programs || response.data;
      const programArray = Array.isArray(programs) ? programs : [];
      setAvailablePrograms(programArray);
    } catch (error) {
      console.error('Error loading available programs:', error);
      setAvailablePrograms([]);
    }
  };

  const handleRefresh = async (auditId) => {
    setLoading(true);
    try {
      await schedulesAPI.refreshDegreeAudit(auditId);
      await loadDegreeAudits();
    } catch (error) {
      console.error('Error refreshing degree audit:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEnrollInProgram = async () => {
    if (!selectedProgram) return;
    
    try {
      setEnrolling(true);
      await schedulesAPI.enrollInDegreeProgram(selectedProgram.id);
      setShowAddDialog(false);
      setSelectedProgram(null);
      await loadDegreeAudits();
    } catch (error) {
      console.error('Error enrolling in program:', error);
    } finally {
      setEnrolling(false);
    }
  };

  const handleUnenrollFromProgram = async (auditId) => {
    try {
      await schedulesAPI.unenrollFromDegreeProgram(auditId);
      await loadDegreeAudits();
    } catch (error) {
      console.error('Error unenrolling from program:', error);
    }
  };


  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'info';
    if (percentage >= 40) return 'warning';
    return 'error';
  };

  const getRequirementIcon = (isSatisfied) => {
    return isSatisfied ? (
      <CheckCircleIcon color="success" />
    ) : (
      <WarningIcon color="warning" />
    );
  };

  const getRequirementColor = (isSatisfied) => {
    return isSatisfied ? 'success' : 'warning';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!degreeAudits || degreeAudits.length === 0) {
    return (
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4">
            Degree Audit
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setShowAddDialog(true)}
          >
            Add Degree Program
          </Button>
        </Box>
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <SchoolIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No Degree Program Enrolled
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Select a degree program to track your academic progress
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowAddDialog(true)}
            >
              Add Degree Program
            </Button>
          </CardContent>
        </Card>

        {/* Add Program Dialog */}
        <Dialog open={showAddDialog} onClose={() => setShowAddDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Degree Program</DialogTitle>
          <DialogContent>
            {availablePrograms.length === 0 ? (
              <Box display="flex" justifyContent="center" p={2}>
                <CircularProgress />
              </Box>
            ) : (
              <Autocomplete
              options={availablePrograms || []}
              getOptionLabel={(option) => option.name}
              value={selectedProgram}
              onChange={(event, newValue) => setSelectedProgram(newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Select Degree Program"
                  placeholder="Search for a degree program..."
                  margin="normal"
                  fullWidth
                />
              )}
              renderOption={(props, option) => (
                <Box component="li" {...props}>
                  <Typography variant="subtitle1">{option.name}</Typography>
                </Box>
              )}
            />
            )}
            {selectedProgram && (
              <Box mt={2}>
                <Typography variant="body2" color="text.secondary">
                  {selectedProgram.description}
                </Typography>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowAddDialog(false)}>Cancel</Button>
            <Button
              onClick={handleEnrollInProgram}
              variant="contained"
              disabled={!selectedProgram || enrolling}
            >
              {enrolling ? <CircularProgress size={20} /> : 'Add Program'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Degree Audit
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setShowAddDialog(true)}
            sx={{ mr: 2 }}
          >
            Add Program
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => degreeAudits.forEach(audit => handleRefresh(audit.id))}
            disabled={loading}
          >
            Refresh All
          </Button>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab 
            icon={<AssignmentIcon />} 
            label="Program Requirements" 
            iconPosition="start"
          />
          <Tab 
            icon={<TimelineIcon />} 
            label="Course Selection" 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Box>
          {degreeAudits && degreeAudits.map((audit, auditIndex) => (
        <Card key={auditIndex} sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Box>
                <Typography variant="h5" gutterBottom>
                  {audit.program}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Last updated: {new Date(audit.last_updated).toLocaleDateString()}
                </Typography>
              </Box>
              <Box>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={loading ? <CircularProgress size={16} /> : <RefreshIcon />}
                  onClick={() => handleRefresh(audit.id)}
                  disabled={loading}
                  sx={{ mr: 1 }}
                >
                  Refresh
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={() => handleUnenrollFromProgram(audit.id)}
                >
                  Remove
                </Button>
              </Box>
            </Box>

            {/* Overall Progress */}
            <Card variant="outlined" sx={{ mb: 3, p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Overall Progress
              </Typography>
              <Box display="flex" alignItems="center" mb={2}>
                <LinearProgress
                  variant="determinate"
                  value={audit.progress?.percentage_complete || 0}
                  color={getProgressColor(audit.progress?.percentage_complete || 0)}
                  sx={{ flexGrow: 1, mr: 2, height: 8, borderRadius: 4 }}
                />
                <Typography variant="h6" color="primary">
                  {Math.round(audit.progress?.percentage_complete || 0)}%
                </Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    Credits Earned
                  </Typography>
                  <Typography variant="h6">
                    {audit.progress?.credits_earned || 0}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    Credits Required
                  </Typography>
                  <Typography variant="h6">
                    {audit.progress?.total_credits_required || 0}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    Credits Remaining
                  </Typography>
                  <Typography variant="h6" color="error">
                    {audit.progress?.credits_remaining || 0}
                  </Typography>
                </Grid>
              </Grid>
            </Card>

            {/* Requirements */}
            <Typography variant="h6" gutterBottom>
              Degree Requirements
            </Typography>
            
            {audit.requirement_status?.map((requirement, reqIndex) => (
              <Accordion key={reqIndex} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" width="100%">
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      {getRequirementIcon(requirement.is_satisfied)}
                    </ListItemIcon>
                    <Box flexGrow={1}>
                      <Typography variant="subtitle1">
                        {requirement.requirement.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {requirement.requirement.requirement_type.replace('_', ' ').toUpperCase()}
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center" mr={2}>
                      <Chip
                        label={`${requirement.credits_earned}/${requirement.credits_required} credits`}
                        color={getRequirementColor(requirement.is_satisfied)}
                        variant="outlined"
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      <LinearProgress
                        variant="determinate"
                        value={(requirement.credits_earned / requirement.credits_required) * 100}
                        color={getRequirementColor(requirement.is_satisfied)}
                        sx={{ width: 100, height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {requirement.requirement.description}
                  </Typography>
                  
                  {requirement.satisfied_courses.length > 0 && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Satisfied Courses:
                      </Typography>
                      <List dense>
                        {requirement.satisfied_courses.map((course, courseIndex) => (
                          <ListItem key={courseIndex}>
                            <ListItemIcon>
                              <CheckCircleIcon color="success" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText
                              primary={course.full_code}
                              secondary={course.title}
                            />
                            <Chip
                              label={`${course.credits} credits`}
                              size="small"
                              variant="outlined"
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {!requirement.is_satisfied && (
                    <Alert severity="warning" sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        <strong>Remaining:</strong> {requirement.credits_required - requirement.credits_earned} credits needed
                      </Typography>
                    </Alert>
                  )}
                </AccordionDetails>
              </Accordion>
            ))}

            {/* Summary */}
            <Divider sx={{ my: 3 }} />
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="success.main" gutterBottom>
                    Satisfied Requirements
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {audit.requirement_status?.filter(req => req.is_satisfied).length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    of {audit.requirement_status?.length || 0} total
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="warning.main" gutterBottom>
                    Pending Requirements
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {audit.requirement_status?.filter(req => !req.is_satisfied).length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    need completion
                  </Typography>
                </Card>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      ))}
        </Box>
      )}

      {/* Course Selection Tab */}
      {activeTab === 1 && (
        <Box>
          {degreeAudits.length === 0 ? (
            <Alert severity="info">
              Please add a degree program first to start building your course selection grid.
            </Alert>
          ) : (
            <SemesterGrid 
              degreeAudits={degreeAudits} 
              onUpdate={() => {
                // Reload degree audits to refresh progress
                loadDegreeAudits();
              }}
            />
          )}
        </Box>
      )}

      {/* Add Program Dialog */}
      <Dialog open={showAddDialog} onClose={() => setShowAddDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Degree Program</DialogTitle>
        <DialogContent>
          {availablePrograms.length === 0 ? (
            <Box display="flex" justifyContent="center" p={2}>
              <CircularProgress />
            </Box>
          ) : (
            <Autocomplete
            options={availablePrograms || []}
            getOptionLabel={(option) => option.name}
            value={selectedProgram}
            onChange={(event, newValue) => setSelectedProgram(newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Select Degree Program"
                placeholder="Search for a degree program..."
                margin="normal"
                fullWidth
              />
            )}
            renderOption={(props, option) => (
              <Box component="li" {...props}>
                <Typography variant="subtitle1">{option.name}</Typography>
              </Box>
            )}
          />
          )}
          {selectedProgram && (
            <Box mt={2}>
              <Typography variant="body2" color="text.secondary">
                {selectedProgram.description}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAddDialog(false)}>Cancel</Button>
          <Button
            onClick={handleEnrollInProgram}
            variant="contained"
            disabled={!selectedProgram || enrolling}
          >
            {enrolling ? <CircularProgress size={20} /> : 'Add Program'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DegreeAudit;

