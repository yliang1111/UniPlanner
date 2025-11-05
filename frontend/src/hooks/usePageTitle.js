import { useEffect } from 'react';

/**
 * Custom hook to set page title dynamically
 * @param {string} title - The page title to set
 */
export const usePageTitle = (title) => {
  useEffect(() => {
    const baseTitle = 'UniPlanner';
    document.title = title ? `${title} - ${baseTitle}` : baseTitle;
    
    // Cleanup function to reset title when component unmounts
    return () => {
      document.title = baseTitle;
    };
  }, [title]);
};

export default usePageTitle;

