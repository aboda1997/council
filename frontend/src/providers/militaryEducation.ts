import type {
  CouncilFiltersResponse,
  GeneralResponse,
  MilitaryEducationListResponse,
  MilitaryEduViewResponse,
  StudentMilitaryEdu,
} from "@/utils/types";
import provider from "./general";

export class MilitaryEducationProvider {
  static async filters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/militaryEducation/filters/");
  }

  static async formFilters(Id: number): Promise<CouncilFiltersResponse> {
    return await provider.get("api/militaryEducation/formFilters/", {
      params: {
        Id,
      },
    });
  }

  static async getStudentData(Id: number): Promise<MilitaryEduViewResponse> {
    return await provider.get("api/militaryEducation/student/", {
      params: {
        Id,
      },
    });
  }

  static async addStudentData(
    Id: number,
    studentMilitaryEdu: StudentMilitaryEdu
  ): Promise<GeneralResponse> {
    return await provider.post("api/militaryEducation/student/", {
      Id,
      studentMilitaryEdu,
    });
  }
  static async editStudentData(
    Id: number,
    studentMilitaryEdu: StudentMilitaryEdu
  ): Promise<GeneralResponse> {
    return await provider.put("api/militaryEducation/student/", {
      Id,
      studentMilitaryEdu,
    });
  }

  static async deleteStudentData(Id: number): Promise<GeneralResponse> {
    return await provider.delete("api/militaryEducation/student/", {
      data: { Id },
    });
  }

  static async getStudentsList(
    query: object
  ): Promise<MilitaryEducationListResponse> {
    return await provider.get("api/militaryEducation/studentsList/", {
      params: {
        ...query,
      },
    });
  }
}
