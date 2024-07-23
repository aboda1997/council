import type {
  CouncilFiltersResponse,
  GeneralResponse,
  InquireStudentQuery,
  InquireStudentsListResponse,
} from "@/utils/types";
import provider from "./general";

export class ReviewInitiallyAcceptedProvider {
  static async filters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/reviewInitiallyAccepted/filters/");
  }

  static async formFilters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/reviewInitiallyAccepted/formFilters/");
  }

  static async editStudentData(
    studentsIds: (number | undefined)[],
    studentStatus?: number,
    studentFulfillment?: number
  ): Promise<GeneralResponse> {
    return await provider.put("api/reviewInitiallyAccepted/reviewStudents/", {
      studentsIds,
      studentStatus,
      studentFulfillment,
    });
  }

  static async getStudentsList(
    query: InquireStudentQuery
  ): Promise<InquireStudentsListResponse> {
    return await provider.get("api/reviewInitiallyAccepted/studentsList/", {
      params: {
        ...query,
      },
    });
  }
}
