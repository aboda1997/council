import type { FiltersSearchType } from "@/utils/enums";
import type {
  GeneralResponse,
  CDStudentResponse,
  StudentsListResponse as CDStudentsListResponse,
  CouncilFiltersResponse,
  GSListResponse,
  CDStudent,
} from "@/utils/types";
import provider from "./general";
export class InquireCDStudentProvider {
  static async filters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/inquireCDStudent/filters/");
  }

  static async gsFilters(selectedYear: string): Promise<GSListResponse> {
    return await provider.get("api/inquireCDStudent/gsFilters/", {
      params: {
        selectedYear,
      },
    });
  }

  static async getStudent(
    selectedYear: string,
    nationalId: string,
    seatNumber: number
  ): Promise<CDStudentResponse> {
    return await provider.get("api/inquireCDStudent/student/", {
      params: {
        selectedYear,
        nationalId,
        seatNumber,
      },
    });
  }

  static async addStudent(
    selectedYear: string,
    student: CDStudent
  ): Promise<GeneralResponse> {
    return await provider.post("api/inquireCDStudent/student/", {
      selectedYear,
      student,
    });
  }

  static async editStudent(
    selectedYear: string,
    nationalId: string,
    seatNumber: number,
    student: CDStudent
  ): Promise<GeneralResponse> {
    return await provider.put("api/inquireCDStudent/student/", {
      selectedYear,
      nationalId,
      seatNumber,
      student,
    });
  }

  static async deleteStudent(
    selectedYear: string,
    nationalId?: string,
    seatNumber?: number
  ): Promise<GeneralResponse> {
    return await provider.delete("api/inquireCDStudent/student/", {
      data: { selectedYear, nationalId, seatNumber },
    });
  }

  static async getStudentsList(
    selectedYear: string,
    searchField: string,
    searchType?: FiltersSearchType,
    page = 0,
    perPage = 10
  ): Promise<CDStudentsListResponse> {
    return await provider.get("api/inquireCDStudent/list/", {
      params: {
        selectedYear,
        searchType,
        searchField,
        page,
        perPage,
      },
    });
  }
}
