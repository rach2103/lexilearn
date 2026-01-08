import { useEffect, useRef } from 'react';

const useTimeTracking = () => {
  const startTimeRef = useRef(null);
  const totalTimeRef = useRef(0);

  useEffect(() => {
    // Start tracking time when component mounts
    startTimeRef.current = Date.now();
    
    // Load existing time from localStorage
    const savedTime = localStorage.getItem('totalStudyTime');
    if (savedTime) {
      totalTimeRef.current = parseInt(savedTime, 10);
    }

    // Save time when page unloads
    const handleBeforeUnload = () => {
      if (startTimeRef.current) {
        const sessionTime = Math.floor((Date.now() - startTimeRef.current) / 1000);
        totalTimeRef.current += sessionTime;
        localStorage.setItem('totalStudyTime', totalTimeRef.current.toString());
      }
    };

    // Save time periodically (every 30 seconds)
    const interval = setInterval(() => {
      if (startTimeRef.current) {
        const sessionTime = Math.floor((Date.now() - startTimeRef.current) / 1000);
        const newTotal = totalTimeRef.current + sessionTime;
        localStorage.setItem('totalStudyTime', newTotal.toString());
        startTimeRef.current = Date.now(); // Reset start time
        totalTimeRef.current = newTotal;
      }
    }, 30000);

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      handleBeforeUnload();
      clearInterval(interval);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  const getTotalTime = () => {
    const savedTime = localStorage.getItem('totalStudyTime');
    return savedTime ? parseInt(savedTime, 10) : 0;
  };

  return { getTotalTime };
};

export default useTimeTracking;