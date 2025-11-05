import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
  Divider,
  Chip,
  Avatar,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Person as PersonIcon,
  School as SchoolIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { authAPI } from '../../services/api';

const Profile = () => {
  // Get user data from localStorage instead of AuthContext
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const isAuthenticated = !!user;
  const isAdmin = user?.username === 'admin';
  const isGuest = user?.username === 'guest';
  const isSpecialUser = isAdmin || isGuest;
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editing, setEditing] = useState(false);
  const [profileData, setProfileData] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirm_password: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
    date_of_birth: '',
    // Student-specific fields
    student_id: '',
    graduation_year: '',
    gpa: '',
    enrollment_status: 'active',
  });

  useEffect(() => {
    if (isAuthenticated) {
      loadProfile();
    }
  }, [isAuthenticated]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await authAPI.getProfile();
      if (response.data.success) {
        setProfileData(response.data);
        const data = response.data;
        
        setFormData({
          username: data.user.username || '',
          password: '',
          confirm_password: '',
          first_name: data.user.first_name || '',
          last_name: data.user.last_name || '',
          email: data.user.email || '',
          phone: data.profile.phone || '',
          address: data.profile.address || '',
          date_of_birth: data.profile.date_of_birth || '',
          student_id: data.student_profile?.student_id || '',
          graduation_year: data.student_profile?.graduation_year || '',
          gpa: data.student_profile?.gpa || '',
          enrollment_status: data.student_profile?.enrollment_status || 'active',
        });
      }
    } catch (error) {
      setError('Failed to load profile');
      console.error('Profile load error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      // Validate password confirmation
      if (formData.password && formData.password !== formData.confirm_password) {
        setError('Passwords do not match');
        return;
      }
      
      // Prepare data for API (exclude confirm_password)
      const updateData = { ...formData };
      delete updateData.confirm_password;
      
      // If password is empty, don't send it
      if (!updateData.password) {
        delete updateData.password;
      }
      
      const response = await authAPI.updateProfile(updateData);
      if (response.data.success) {
        setSuccess('Profile updated successfully');
        setEditing(false);
        setEditDialogOpen(false);
        await loadProfile(); // Reload profile data
      } else {
        setError(response.data.error || 'Failed to update profile');
      }
    } catch (error) {
      setError('Failed to update profile');
      console.error('Profile update error:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditing(false);
    setEditDialogOpen(false);
    setError('');
    setSuccess('');
    // Reset form data to original values
    if (profileData) {
      const data = profileData;
      setFormData({
        username: data.user.username || '',
        password: '',
        confirm_password: '',
        first_name: data.user.first_name || '',
        last_name: data.user.last_name || '',
        email: data.user.email || '',
        phone: data.profile.phone || '',
        address: data.profile.address || '',
        date_of_birth: data.profile.date_of_birth || '',
        student_id: data.student_profile?.student_id || '',
        graduation_year: data.student_profile?.graduation_year || '',
        gpa: data.student_profile?.gpa || '',
        enrollment_status: data.student_profile?.enrollment_status || 'active',
      });
    }
  };

  const handleEditClick = () => {
    setEditDialogOpen(true);
    setEditing(true);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!profileData) {
    return (
      <Box>
        <Alert severity="error">Failed to load profile data</Alert>
      </Box>
    );
  }

  const isStudent = profileData.profile.role === 'student';

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Profile
      </Typography>

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

      {/* Profile Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Avatar sx={{ width: 64, height: 64, bgcolor: 'primary.main' }}>
              <PersonIcon sx={{ fontSize: 32 }} />
            </Avatar>
            <Box>
              <Typography variant="h5">
                {profileData.user.username}
              </Typography>
              {isSpecialUser && (
                <Chip 
                  label={isAdmin ? "Admin Account" : "Guest Account"} 
                  color={isAdmin ? "error" : "warning"} 
                  size="small" 
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
            <Box sx={{ ml: 'auto' }}>
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={handleEditClick}
              >
                Edit Profile
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Edit Profile Dialog */}
      <Dialog 
        open={editDialogOpen} 
        onClose={handleCancel}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Profile</DialogTitle>
        <DialogContent>
          {isSpecialUser && (
            <Alert severity="info" sx={{ mb: 2 }}>
              {isAdmin 
                ? "Admin accounts have restricted editing capabilities. Username and password cannot be changed." 
                : "Guest accounts have restricted editing capabilities. Username and password cannot be changed."
              }
            </Alert>
          )}
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              disabled={isSpecialUser}
              helperText={isSpecialUser ? "Username cannot be changed for admin/guest accounts" : ""}
            />
            
            <TextField
              fullWidth
              label="New Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              disabled={isSpecialUser}
              helperText={isSpecialUser ? "Password cannot be changed for admin/guest accounts" : "Leave blank to keep current password"}
            />
            
            <TextField
              fullWidth
              label="Confirm New Password"
              name="confirm_password"
              type="password"
              value={formData.confirm_password}
              onChange={handleChange}
              disabled={isSpecialUser}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancel}>
            Cancel
          </Button>
          <Button 
            onClick={handleSave} 
            variant="contained"
            disabled={saving}
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
          >
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Profile;

