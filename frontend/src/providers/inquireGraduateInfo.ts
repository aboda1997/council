import type {
  CouncilFiltersResponse,
  FileActionResponse,
  GeneralResponse,
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

export class InquireGraduateInfoProvider {
  static async filters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/inquireGraduateInfo/filters/");
  }

  static async formFilters(): Promise<CouncilFiltersResponse> {
    return await provider.get("api/inquireGraduateInfo/formFilters/");
  }

  static async getStudent(Id: number): Promise<StudentViewResponse> {
    return await provider.get("api/inquireGraduateInfo/student/", {
      params: {
        Id,
      },
    });
  }

  static async getStudentHistory(Id: number): Promise<StudentHistoryResponse> {
    return await provider.get("api/inquireGraduateInfo/studentHistory/", {
      params: {
        Id,
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
    return await provider.put("api/inquireGraduateInfo/student/", {
      Id,
      studentData: {
        student,
        studentSecondaryEdu,
        studentUniversityEdu,
        studentImposedCourses,
      },
    });
  }

  static async deleteStudent(Id: number): Promise<GeneralResponse> {
    return await provider.delete("api/inquireGraduateInfo/student/", {
      data: { Id },
    });
  }

  static async getStudentsList(
    query: InquireStudentQuery
  ): Promise<InquireStudentsListResponse> {
    return await provider.get("api/inquireGraduateInfo/studentsList/", {
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
    return await provider.put(
      "api/inquireGraduateInfo/attachments/",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
  }

  static async downloadAttachments(fileId: string): Promise<Blob> {
    return await provider.get("api/inquireGraduateInfo/attachments/", {
      params: {
        fileId,
      },
      responseType: "blob",
    });
  }

  static async deleteAttachments(
    files: Array<UploadedFile>
  ): Promise<FileActionResponse> {
    return await provider.put("api/inquireGraduateInfo/attachments/", {
      action: "DELETE",
      files,
    });
  }
}
