// Chart.js wrapper component for Smart Robotic Arm Dashboard
// This file exports Chart.js functionality for use in the dashboard

// Import Chart.js from CDN (loaded in HTML)
// The Chart class is available globally when Chart.js is loaded via CDN

// Export Chart class for use in other modules
export const Chart = window.Chart

// Additional chart utilities and configurations
export const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "top",
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: "rgba(0, 0, 0, 0.1)",
      },
    },
    x: {
      grid: {
        color: "rgba(0, 0, 0, 0.1)",
      },
    },
  },
}

// Common chart color schemes
export const chartColors = {
  primary: "rgb(99, 102, 241)",
  primaryAlpha: "rgba(99, 102, 241, 0.1)",
  success: "rgb(34, 197, 94)",
  successAlpha: "rgba(34, 197, 94, 0.1)",
  warning: "rgb(245, 158, 11)",
  warningAlpha: "rgba(245, 158, 11, 0.1)",
  error: "rgb(239, 68, 68)",
  errorAlpha: "rgba(239, 68, 68, 0.1)",
}

// Helper function to create line chart configuration
export const createLineChartConfig = (labels, datasets, options = {}) => {
  return {
    type: "line",
    data: {
      labels,
      datasets,
    },
    options: {
      ...chartDefaults,
      ...options,
    },
  }
}

// Helper function to create bar chart configuration
export const createBarChartConfig = (labels, datasets, options = {}) => {
  return {
    type: "bar",
    data: {
      labels,
      datasets,
    },
    options: {
      ...chartDefaults,
      ...options,
    },
  }
}
