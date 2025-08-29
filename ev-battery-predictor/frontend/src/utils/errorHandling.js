/**
 * Utility functions for handling API errors consistently across the application
 */

/**
 * Formats error messages from API responses
 * @param {Error} error - Axios error object
 * @param {string} defaultMessage - Default message if error cannot be parsed
 * @returns {string} - Human readable error message
 */
export const formatErrorMessage = (error, defaultMessage = 'An error occurred') => {
  if (!error.response?.data?.detail) {
    return defaultMessage;
  }

  const detail = error.response.data.detail;
  
  // If detail is a string, return it directly
  if (typeof detail === 'string') {
    return detail;
  }
  
  // If detail is an array of Pydantic validation errors
  if (Array.isArray(detail)) {
    return detail.map(err => {
      // Extract field name from location if available
      const fieldName = err.loc && err.loc.length > 1 ? err.loc[err.loc.length - 1] : '';
      const message = err.msg || 'Invalid input';
      
      return fieldName ? `${fieldName}: ${message}` : message;
    }).join(', ');
  }
  
  // If detail is an object but not an array
  if (typeof detail === 'object') {
    return JSON.stringify(detail);
  }
  
  return defaultMessage;
};

/**
 * Handles API errors and returns a standardized response
 * @param {Error} error - Axios error object
 * @param {string} defaultMessage - Default message if error cannot be parsed
 * @returns {Object} - Standardized error response
 */
export const handleApiError = (error, defaultMessage = 'An error occurred') => {
  return {
    success: false,
    error: formatErrorMessage(error, defaultMessage)
  };
};

/**
 * Handles API success responses
 * @param {*} data - Response data
 * @returns {Object} - Standardized success response
 */
export const handleApiSuccess = (data = null) => {
  return {
    success: true,
    data
  };
};