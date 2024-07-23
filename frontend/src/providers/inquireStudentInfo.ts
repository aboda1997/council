import type {
  CouncilFiltersResponse,
  FileActionResponse,
  GeneralResponse,
  RevertTransactionResponse,
  SecondaryGSInfoResponse,
  Student,
  StudentHistoryResponse,
  StudentImposedCourse,
  StudentSecondaryEdu,
  StudentUniversityEdu,
  StudentViewResponse,
  UploadedFile,
} from "@/utils/types";
import provider from "./general";
import type {
  InquireStudentsListResponse,
  InquireStudentQuery,
} from "@/utils/types";

export class InquireStudentInfoProvider {
  static async filters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/inquireStudentInfo/filters/");
  }

  static async formFilters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/inquireStudentInfo/formFilters/");
  }

  static async popupfilters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/inquireStudentInfo/popupFilters/");
  }

  static async getSecondaryGSInfo(
    NID: string,
    certificate: number,
    certYear: number
  ): Promise<SecondaryGSInfoResponse> {
    return await provider.get("api/inquireStudentInfo/secondaryGSInfo/", {
      params: {
        NID,
        certificate,
        certYear,
      },
    });
  }

  static async getStudent(Id: number): Promise<StudentViewResponse> {
    return await provider.get("api/inquireStudentInfo/student/", {
      params: {
        Id,
      },
    });
  }

  static async getStudentHistory(Id: number): Promise<StudentHistoryResponse> {
    return await provider.get("api/inquireStudentInfo/studentHistory/", {
      params: {
        Id,
      },
    });
  }

  static async addStudent(
    student: Student,
    studentSecondaryEdu?: StudentSecondaryEdu,
    studentUniversityEdu?: StudentUniversityEdu,
    studentImposedCourses?: StudentImposedCourse[] | undefined
  ): Promise<GeneralResponse> {
    return await provider.post("api/inquireStudentInfo/student/", {
      studentData: {
        student,
        studentSecondaryEdu,
        studentUniversityEdu,
        studentImposedCourses,
      },
    });
  }

  static async editStudent(
    Id: number,
    student: Student,
    studentSecondaryEdu?: StudentSecondaryEdu,
    studentUniversityEdu?: StudentUniversityEdu,
    studentImposedCourses?: StudentImposedCourse[] | undefined
  ): Promise<GeneralResponse> {
    return await provider.put("api/inquireStudentInfo/student/", {
      Id,
      studentData: {
        student,
        studentSecondaryEdu,
        studentUniversityEdu,
        studentImposedCourses,
      },
    });
  }

  static async revertTransaction(
    Id: number,
    transactionId: number
  ): Promise<RevertTransactionResponse> {
    return await provider.put("api/inquireStudentInfo/revertTransaction/", {
      Id,
      transactionId,
    });
  }

  static async deleteStudent(Id: number): Promise<GeneralResponse> {
    return await provider.delete("api/inquireStudentInfo/student/", {
      data: { Id },
    });
  }

  static async getStudentsList(
    query: InquireStudentQuery
  ): Promise<InquireStudentsListResponse> {
    return await provider.get("api/inquireStudentInfo/studentsList/", {
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
    return await provider.put("api/inquireStudentInfo/attachments/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  }

  static async downloadAttachments(fileId: string): Promise<Blob> {
    return await provider.get("api/inquireStudentInfo/attachments/", {
      params: {
        fileId,
      },
      responseType: "blob",
    });
  }

  static async deleteAttachments(
    files: Array<UploadedFile>
  ): Promise<FileActionResponse> {
    return await provider.put("api/inquireStudentInfo/attachments/", {
      action: "DELETE",
      files,
    });
  }
}
