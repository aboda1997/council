import type {
  CouncilFiltersResponse,
  GeneralResponse,
  StudentUniversityEdu,
  StudentViewResponse,
  TransferToFacultyResponse,
  FileActionResponse,
  UploadedFile,
} from "@/utils/types";
import provider from "./general";
import type {
  InquireStudentsListResponse,
  InquireStudentQuery,
} from "@/utils/types";

export class TransferStudentsProvider {
  static async filters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/transferStudents/filters/");
  }

  static async formFilters(
    faculty_id: number | undefined,
    university_id: number | undefined
  ): Promise<CouncilFiltersResponse> {
    return await provider.get("api/transferStudents/formFilters/", {
      params: { faculty_id, university_id },
    });
  }

  static async getStudent(Id: number): Promise<StudentViewResponse> {
    return await provider.get("api/transferStudents/student/", {
      params: {
        Id,
      },
    });
  }

  static async getFacultyData(
    faculty_id: number
  ): Promise<TransferToFacultyResponse> {
    return await provider.get("api/transferStudents/facultyData/", {
      params: { faculty_id },
    });
  }

  static async transferStudent(
    Id: number,
    transferData: StudentUniversityEdu
  ): Promise<GeneralResponse> {
    return await provider.put("api/transferStudents/transfer/", {
      Id,
      faculty_id: transferData.studentFaculty_id,
      transfer_date: transferData.transferDate,
      equivalent_hours: transferData.totalEquivalentHours,
      transfer_level: transferData.studentLevel_id,
      fulfillment_id: transferData.transferFulfillment_id,
    });
  }

  static async getStudentsList(
    query: InquireStudentQuery
  ): Promise<InquireStudentsListResponse> {
    return await provider.get("api/transferStudents/studentsList/", {
      params: {
        ...query,
      },
    });
  }

  static async uploadAttachments(
    studentUniqueId: string,
    files: Array<File>
  ): Promise<FileActionResponse> {
    const formData = new FormData();
    formData.append("action", "CREATE");
    formData.append("uniqueId", studentUniqueId);
    files.forEach((file: File) => {
      formData.append("files", file);
    });
    return await provider.put("api/transferStudents/attachments/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  }

  static async downloadAttachments(fileId: string): Promise<Blob> {
    return await provider.get("api/transferStudents/attachments/", {
      params: {
        fileId,
      },
      responseType: "blob",
    });
  }

  static async deleteAttachments(
    files: Array<UploadedFile>
  ): Promise<FileActionResponse> {
    return await provider.put("api/transferStudents/attachments/", {
      action: "DELETE",
      files,
    });
  }
}
