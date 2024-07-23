import type {
  CouncilFiltersResponse,
  AcceptedStudentsNamesResponse,
} from "@/utils/types";
import provider from "../general";

export class AcceptedStudentsNamesProvider {
  static async filters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/acceptedStudentsNames/filters/");
  }

  static async getReportData(
    query: object
  ): Promise<AcceptedStudentsNamesResponse> {
    return await provider.get("api/acceptedStudentsNames/report/", {
      params: {
        ...query,
      },
    });
  }
}
