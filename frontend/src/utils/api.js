/**
 * API Client Utility
 * Handles all API requests to the backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Make a fetch request to the API
 * @param {string} endpoint - API endpoint path (e.g., '/api/users')
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {object} data - Request body data for POST/PUT
 * @returns {Promise} - Response data or error
 */
export const fetchAPI = async (endpoint, method = 'GET', data = null) => {
  const url = `${API_BASE_URL}${endpoint}`;

  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Add request body for POST and PUT
  if (data && (method === 'POST' || method === 'PUT')) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, options);

    // Handle response
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      let errorMessage = `API Error: ${response.status} ${response.statusText}`;
      
      if (errorData.detail) {
        // Handle Pydantic validation errors (array of errors)
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail
            .map(err => `${err.loc.join('.')}: ${err.msg}`)
            .join('; ');
        } else {
          errorMessage = errorData.detail;
        }
      }
      
      console.error(`API Response [${response.status}]:`, errorData);
      throw new Error(errorMessage);
    }

    // Parse and return response
    const responseData = await response.json();
    return responseData;
  } catch (error) {
    console.error(`API Error [${method} ${endpoint}]:`, error);
    throw error;
  }
};

/**
 * Upload a file to the API
 * @param {string} endpoint - API endpoint for file upload
 * @param {File} file - File object to upload
 * @returns {Promise} - Response data
 */
export const uploadFile = async (endpoint, file) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header for FormData
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('File upload error:', error);
    throw error;
  }
};

/**
 * Download a file from the API
 * @param {string} endpoint - API endpoint for file download
 * @param {string} filename - Desired filename for the download
 */
export const downloadFile = async (endpoint, filename) => {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Download failed: ${response.status}`);
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error('File download error:', error);
    throw error;
  }
};

/**
 * Get the API base URL (useful for constructing URLs in components)
 * @returns {string} - The base URL of the API
 */
export const getApiBaseUrl = () => API_BASE_URL;

/**
 * Retry API call with exponential backoff
 * @param {Function} apiFn - Async function to retry
 * @param {number} maxRetries - Maximum number of retries
 * @param {number} delay - Initial delay in ms
 * @returns {Promise} - Response data
 */
export const retryAPI = async (apiFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiFn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
};

/**
 * Create an API error handler
 * @param {Error} error - The error object
 * @returns {string} - User-friendly error message
 */
export const getErrorMessage = (error) => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred. Please try again.';
};

const apiClient = {
  fetchAPI,
  uploadFile,
  downloadFile,
  getApiBaseUrl,
  retryAPI,
  getErrorMessage,
};

export default apiClient;