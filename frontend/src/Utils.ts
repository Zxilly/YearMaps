export function isDebug() {
    return process.env.NODE_ENV === 'development';
}

export const BASE_URI = isDebug() ? 'http://localhost:5000' : '';

export const API_URI = `${BASE_URI}/api`;

export const TIME_URI = `${BASE_URI}/update_time`;
