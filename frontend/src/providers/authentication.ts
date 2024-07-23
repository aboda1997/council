import type {
  LoginResponse,
  ForgetPasswordResponse,
  CheckTokenResponse,
  GeneralResponse,
  UserPermissionsResponse,
} from "@/utils/types";
import type { LocationQueryValue } from "vue-router";
import provider from "./general";

// Provider for all things related to authentication
export class AuthenticationProvider {
  static async submitLogin(
    username: string,
    password: string
  ): Promise<LoginResponse> {
    return await provider.post("/api/authentication/login/", {
      username,
      password,
    });
  }
  static async getUserPermissions(): Promise<UserPermissionsResponse> {
    return await provider.get("/api/authentication/userPermissions/");
  }
  static async submitEmail(
    email: string,
    lang: string | null
  ): Promise<ForgetPasswordResponse> {
    return await provider.post("/api/authentication/forget/", { email, lang });
  }
  static async checkToken(
    emailToken: LocationQueryValue | LocationQueryValue[]
  ): Promise<CheckTokenResponse> {
    return await provider.post("api/authentication/checkToken/", {
      emailToken,
    });
  }
  static async saveNewPassword(
    password: string,
    rePassword: string,
    emailToken: LocationQueryValue | LocationQueryValue[]
  ): Promise<GeneralResponse> {
    return await provider.post("api/authentication/savePassword/", {
      password,
      rePassword,
      emailToken,
    });
  }
}
