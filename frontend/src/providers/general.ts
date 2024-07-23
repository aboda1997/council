import { useUserDataStore } from "@/stores/userData";
import { ToastTypes } from "@/utils/enums";
import { redirectToLogin, showErrorToastMessage } from "@/utils/globals";
import axios, { type AxiosError } from "axios";

// General Axios Instance used everywhere in the providers
const instance = axios.create({
  baseURL: import.meta.env.VITE_API_ENDPOINT,
});

// Axios Request Interceptors
// Currently adds authentication token To any request being sent.
instance.interceptors.request.use(
  (conf) => {
    const config = { ...conf };
    const userDataStore = useUserDataStore();
    if (config.headers && userDataStore.accessToken !== "") {
      config.headers.authorization = `Bearer ${userDataStore.accessToken}`;
    }
    return config;
  },
  (error) => error
);

// Axios Response Interceptors
// On Success: Update accessToken to the one in the request.
// On Failure: Handles few know cases, such as logging out,
// and then raise the exception again
instance.interceptors.response.use(
  (response) => {
    const userDataStore = useUserDataStore();
    if (response.headers.authorization) {
      userDataStore.accessToken = response.headers.authorization;
    }
    return Promise.resolve(response.data);
  },
  (error: AxiosError) => {
    const userDataStore = useUserDataStore();
    let message =
      "حدث خطأ يرجى ابلاغ الدعم الفنى|An error occured please contact technical support";
    if (error.response) {
      if (error.response.data.detail) {
        message = error.response.data.detail;
      }
      if (error.response.status === 401) {
        userDataStore.resetUserData();
        if (window.location.pathname !== "/login") {
          showErrorToastMessage(message, ToastTypes.WARN);
          redirectToLogin();
        }
      }
    }
    return Promise.reject(message);
  }
);

export default instance;
