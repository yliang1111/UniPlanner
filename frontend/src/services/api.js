import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Only redirect to login if we're not already on the login page
      // and if the error is not from a specific API call that should handle its own errors
      const currentPath = window.location.pathname;
      if (currentPath !== '/login' && currentPath !== '/signup') {
        // Check if this is a critical authentication failure
        const isAuthEndpoint = error.config?.url?.includes('/auth/');
        if (isAuthEndpoint) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const coursesAPI = {
  // Get all courses
  getCourses: (params = {}) => api.get('/courses/courses/', { params }),
  
  // Get available courses for student
  getAvailableCourses: () => api.get('/courses/courses/available/'),
  
  // Get course recommendations
  getRecommendations: (targetCourseId = null) => {
    const params = targetCourseId ? { target_course: targetCourseId } : {};
    return api.get('/courses/courses/recommendations/', { params });
  },
  
  // Get prerequisite chain for a course
  getPrerequisiteChain: (courseId) => api.get(`/courses/courses/${courseId}/prerequisite_chain/`),
  
  // Check if student can take a course
  canTakeCourse: (courseId) => api.get(`/courses/courses/${courseId}/can_take/`),
  
  // Get course offerings
  getOfferings: (params = {}) => api.get('/courses/offerings/', { params }),
  
  // Get departments (all departments from database)
  getDepartments: (params = {}) => api.get('/courses/simple-admin/departments/', { params }),
  
  // Get degree programs
  getDegreePrograms: (params = {}) => api.get('/courses/degree-programs/', { params }),
  
  // Get programs (admin-managed programs)
  getPrograms: (params = {}) => api.get('/courses/simple-admin/programs/', { params }),
  
  // Get courses (all courses from database, including inactive ones)
  getCourses: (params = {}) => api.get('/courses/simple-admin/courses/', { params }),
};

export const schedulesAPI = {
  // Get user's schedules
  getSchedules: (params = {}) => api.get('/schedules/schedules/', { params }),
  
  // Create a new schedule
  createSchedule: (data) => api.post('/schedules/schedules/', data),
  
  // Get schedule with items
  getScheduleWithItems: (scheduleId) => api.get(`/schedules/schedules/${scheduleId}/?with_items=true`),
  
  // Add course to schedule
  addCourseToSchedule: (scheduleId, offeringId) => 
    api.post(`/schedules/schedules/${scheduleId}/add_course/`, { offering_id: offeringId }),
  
  // Remove course from schedule
  removeCourseFromSchedule: (scheduleId, offeringId) => 
    api.post(`/schedules/schedules/${scheduleId}/remove_course/`, { offering_id: offeringId }),
  
  // Get schedule conflicts
  getScheduleConflicts: (scheduleId) => api.get(`/schedules/schedules/${scheduleId}/conflicts/`),
  
  // Get schedule optimization suggestions
  getScheduleOptimization: (scheduleId) => api.get(`/schedules/schedules/${scheduleId}/optimize/`),
  
  // Get alternative offerings for a conflicting course
  getAlternatives: (scheduleId, offeringId) => 
    api.get(`/schedules/schedules/${scheduleId}/alternatives/?offering_id=${offeringId}`),
  
  // Get degree audits
  getDegreeAudits: () => api.get('/schedules/degree-audits/'),
  
  // Refresh degree audit
  refreshDegreeAudit: (auditId) => api.post(`/schedules/degree-audits/${auditId}/refresh/`),
  
  // Enroll in degree program
  enrollInDegreeProgram: (degreeProgramId) => 
    api.post('/schedules/degree-audits/enroll/', { degree_program_id: degreeProgramId }),
  
  // Unenroll from degree program
  unenrollFromDegreeProgram: (auditId) =>
    api.delete(`/schedules/degree-audits/${auditId}/unenroll/`),

  // Course selections
  getCourseSelections: (degreeAuditId) =>
    api.get(`/schedules/course-selections/by_degree_audit/?degree_audit_id=${degreeAuditId}`),
  
  addCourseSelection: (data) =>
    api.post('/schedules/course-selections/', data),
  
  updateCourseSelection: (id, data) =>
    api.put(`/schedules/course-selections/${id}/`, data),
  
  deleteCourseSelection: (id) =>
    api.delete(`/schedules/course-selections/${id}/`),
};

export const usersAPI = {
  // Get current user profile
  getCurrentUser: () => api.get('/users/users/me/'),
  
  // Get user profile
  getUserProfile: (userId) => api.get(`/users/profiles/${userId}/`),
  
  // Create/update user profile
  updateUserProfile: (data) => api.post('/users/profiles/', data),
  
  // Get user's degrees
  getUserDegrees: (profileId) => api.get(`/users/profiles/${profileId}/degrees/`),
  
  // Get user's completed courses
  getCompletedCourses: (profileId) => api.get(`/users/profiles/${profileId}/completed_courses/`),
};

// Admin API
export const adminAPI = {
  // Course management
  getAdminCourses: (params = {}) => api.get('/courses/simple-admin/courses/', { params }),
  createAdminCourse: (courseData) => api.post('/courses/simple-admin/courses/create/', courseData),
  updateAdminCourse: (courseId, courseData) => api.put(`/courses/simple-admin/courses/${courseId}/`, courseData),
  deleteAdminCourse: (courseId) => api.delete(`/courses/simple-admin/courses/${courseId}/delete/`),
  
  // Department management
  getAdminDepartments: () => api.get('/courses/simple-admin/departments/'),
  
  // Degree program management
  getAdminDegreePrograms: () => api.get('/courses/simple-admin/degree-programs/'),
  
  // Program management
  getProgramTypes: () => api.get('/courses/simple-admin/program-types/'),
  getPrograms: () => api.get('/courses/simple-admin/programs/'),
  createProgram: (programData) => api.post('/courses/simple-admin/programs/create/', programData),
  updateProgram: (programId, programData) => api.put(`/courses/simple-admin/programs/${programId}/`, programData),
  deleteProgram: (programId) => api.delete(`/courses/simple-admin/programs/${programId}/delete/`),
  createProgramRequirement: (requirementData) => api.post('/courses/simple-admin/program-requirements/create/', requirementData),
  createProgramCourseRequirement: (courseReqData) => api.post('/courses/simple-admin/program-course-requirements/create/', courseReqData),
  
  // Program requirements management
  getProgramRequirements: (programId) => api.get(`/courses/simple-admin/programs/${programId}/requirements/`),
  createProgramRequirement: (requirementData) => {
    console.log('Creating requirement:', requirementData);
    return api.post('/courses/simple-admin/program-requirements/', requirementData);
  },
  updateProgramRequirement: (requirementId, requirementData) => {
    console.log('Updating requirement:', requirementId, requirementData);
    return api.put(`/courses/simple-admin/program-requirements/${requirementId}/`, requirementData);
  },
  deleteProgramRequirement: (requirementId) => {
    console.log('Deleting requirement:', requirementId);
    return api.delete(`/courses/simple-admin/program-requirements/${requirementId}/delete/`);
  },
};

// Authentication API
export const authAPI = {
  // Login (using custom auth endpoint)
  login: (username, password) => {
    return api.post('/users/auth/login/', {
      username: username,
      password: password
    }, {
      headers: { 'Content-Type': 'application/json' }
    });
  },
  
  // Logout
  logout: () => api.post('/users/auth/logout/'),
  
  // Check if user is authenticated
  checkAuth: () => api.get('/users/auth/profile/'),
  
  // Signup
  signup: (userData) => {
    return api.post('/users/auth/signup/', userData, {
      headers: { 'Content-Type': 'application/json' }
    });
  },
  
  // Get user profile
  getProfile: () => api.get('/users/auth/profile/'),
  
  // Update user profile
  updateProfile: (profileData) => {
    return api.put('/users/auth/profile/update/', profileData, {
      headers: { 'Content-Type': 'application/json' }
    });
  },
};


export default api;
