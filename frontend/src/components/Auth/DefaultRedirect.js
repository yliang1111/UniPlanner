import React from 'react';

const DefaultRedirect = () => {
  // Simple redirect based on localStorage
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  
  // Admin goes to course management
  if (user?.username === 'admin') {
    window.location.href = '/admin/courses';
    return null;
  }
  
  // Guest and other users go to dashboard
  window.location.href = '/dashboard';
  return null;
};

export default DefaultRedirect;
