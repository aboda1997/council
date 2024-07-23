import type {
  CouncilFiltersResponse,
  UniversityStatusStatisticsResponse,
} from "@/utils/types";
import provider from "../general";

export class UniversityStatusStatisticsProvider {
  static async filters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/universityStatusStatistics/filters/");
  }

  static async getReportData(
    query: object
  ): Promise<UniversityStatusStatisticsResponse> {
    return await provider.get("api/universityStatusStatistics/report/", {
      params: {
        ...query,
      },
    });
  }
}
