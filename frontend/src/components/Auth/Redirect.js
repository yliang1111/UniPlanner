import React from 'react';
import { useNavigate } from 'react-router-dom';

const Redirect = () => {
  const navigate = useNavigate();
  
  React.useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (user.username === 'admin') {
      navigate('/admin/courses');
    } else {
      navigate('/dashboard');
    }
  }, [navigate]);

  return null;
};

export default Redirect;



