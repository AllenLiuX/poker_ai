// API configuration
// export const host_by_https = true;
export const host_on_local = true;
// export const API_URL = "http://13.56.253.58:5000";
export const API_URL = host_on_local 
  ? "http://localhost:5001" 
  : "https://3.101.133.162:5001";

// // export const API_URL = "https://api.aico-remix.com";
// export const FRONTEND_URL = host_by_https 
//   ? "https://aico-music.com" 
//   : "http://aico-music.com";
