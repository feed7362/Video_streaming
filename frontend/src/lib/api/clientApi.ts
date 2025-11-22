import axios, { type AxiosInstance, AxiosError } from "axios";

const apiClient: AxiosInstance = axios.create({
    baseURL: "http://localhost",
    // 1. Обов'язково для надсилання/отримання кук через CORS
    withCredentials: true,
});

apiClient.interceptors.response.use(
    (res) => res,
    (error: AxiosError) => {
        const status = error.response?.status;

        // 3. Обробка помилки неавторизованого доступу (401)
        if (status === 401) {
            console.warn("Unauthorized (401): Access Token expired or invalid. Redirecting to login.");

            // Тут повинна бути логіка:
            // 1) Спроба оновити токен (Refresh Token Flow)
            // 2) Або примусовий вихід та перенаправлення на сторінку входу
            // window.location.href = '/login'; 
        }

        console.error("API error:", error.response?.data || error.message);
        return Promise.reject(error);
    }
);

export default apiClient;