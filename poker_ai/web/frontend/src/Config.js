// API configuration
export const host_by_https = true;
export const host_on_local = false;
export const API_URL = host_on_local 
  ? "http://localhost:5001" 
  : "https://aico-music.com:5001";

export const FRONTEND_URL = host_by_https 
  ? "https://aico-music.com" 
  : "http://aico-music.com";

// open https://aico-music.com:5001/game/new first !!!