import type {
  CouncilFiltersResponse,
  NumberAcceptedStudentsResponse,
} from "@/utils/types";
import provider from "../general";

export class NumberAcceptedStudentsProvider {
  static async filters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/numberAcceptedStudents/filters/");
  }

  static async getReportData(
    query: object
  ): Promise<NumberAcceptedStudentsResponse> {
    return await provider.get("api/numberAcceptedStudents/report/", {
      params: {
        ...query,
      },
    });
  }
}
