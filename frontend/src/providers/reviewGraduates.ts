import type {
  CouncilFiltersResponse,
  GeneralResponse,
  InquireStudentQuery,
  InquireStudentsListResponse,
  StudentViewResponse,
  StudentUniversityEdu,
} from "@/utils/types";
import provider from "./general";

export class ReviewGraduatesProvider {
  static async filters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/reviewGraduates/filters/");
  }

  static async formFilters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/reviewGraduates/formFilters/");
  }

  static async getStudent(
    Id: number,
    selectedStudentType?: string
  ): Promise<StudentViewResponse> {
    return await provider.get("api/reviewGraduates/student/", {
      params: {
        Id,
        selectedStudentType,
      },
    });
  }

  static async editStudentData(
    Id: number,
    studentData: StudentUniversityEdu
  ): Promise<GeneralResponse> {
    return await provider.put("api/reviewGraduates/student/", {
      Id,
      studentData,
    });
  }

  static async getStudentsList(
    query: InquireStudentQuery
  ): Promise<InquireStudentsListResponse> {
    return await provider.get("api/reviewGraduates/studentsList/", {
      params: {
        ...query,
      },
    });
  }
}
