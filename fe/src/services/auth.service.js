// fe/src/services/auth.service.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/users/';

// Cấu hình mặc định cho axios
const axiosInstance = axios.create({
    baseURL: API_URL,
    withCredentials: true, // Quan trọng cho việc gửi cookies
    headers: {
        'Content-Type': 'application/json',
    }
});

// Interceptor để xử lý request
axiosInstance.interceptors.request.use(
    (config) => {
        // Lấy CSRF token từ cookie
        const csrfToken = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];

        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor để xử lý response
axiosInstance.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        // Nếu token hết hạn hoặc không hợp lệ
        if (error.response?.status === 401) {
            // Xóa thông tin người dùng trong localStorage
            localStorage.removeItem('user');
        }
        return Promise.reject(error);
    }
);

// Default accounts for fallback when backend is unavailable
const DEFAULT_ACCOUNTS = [
    {
        id: 1,
        username: 'doctor1',
        password: 'password',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        phone_number: '123-456-7890',
        is_doctor: true,
        is_patient: false,
        doctor_profile: {
            specialization: 'Cardiology'
        }
    },
    {
        id: 2,
        username: 'patient1',
        password: 'password',
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane.smith@example.com',
        phone_number: '987-654-3210',
        is_doctor: false,
        is_patient: true,
        patient_profile: {
            date_of_birth: '1990-01-01'
        }
    }
];

const authService = {
    login: async (credentials) => {
        try {
            const response = await axiosInstance.post('login/', credentials);
            if (response.data) {
                localStorage.setItem('user', JSON.stringify(response.data));
            }
            return response.data;
        } catch (error) {
            console.error('Login error:', error.response?.data);
            throw error;
        }
    },

    register: async (userData) => {
        try {
            const response = await axiosInstance.post('register/', userData);
            return response.data;
        } catch (error) {
            console.error('Registration error:', error.response?.data);
            throw error;
        }
    },

    logout: async () => {
        try {
            await axiosInstance.post('logout/');
            localStorage.removeItem('user');
            return true;
        } catch (error) {
            console.error('Logout error:', error.response?.data);
            throw error;
        }
    },

    getCurrentUser: async () => {
        try {
            const response = await axiosInstance.get('me/');
            return response.data;
        } catch (error) {
            console.error('Get current user error:', error.response?.data);
            return null;
        }
    },

    updateProfile: async (data) => {
        try {
            const response = await axiosInstance.put('update-profile/', data);
            return response.data;
        } catch (error) {
            console.error('Update profile error:', error.response?.data);
            throw error;
        }
    },

    // Kiểm tra xem người dùng đã đăng nhập hay chưa
    isAuthenticated: () => {
        const user = localStorage.getItem('user');
        return !!user;
    }
};

export default authService;