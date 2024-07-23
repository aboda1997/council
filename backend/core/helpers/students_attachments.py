from core.helpers.general import (
    delete_files,
    get_file,
    log_activity,
    upload_files,
)
from core.utils.exceptions import InvalidParamsError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.models.db import Graduates, Students, StudentsAttachments


def get_student_attachment(file_id):
    if not file_id:
        raise InvalidParamsError(EXCEPTIONS.get("MISSING_ATTACHMENT_FILE_ID"))
    attachment = (
        StudentsAttachments.objects.filter(attachmentId=file_id)
        .values("mimetype")
        .first()
    )
    if not attachment:
        raise InvalidParamsError(EXCEPTIONS.get("ATTACHMENT_NOT_FOUND"))

    file = get_file(file_id)

    return {"file": file, "content_type": attachment.get("mimetype")}


def create_student_attachments(
    user_id, student_unique_id, files, student_type: str = "student"
):
    if not student_unique_id:
        raise InvalidParamsError(EXCEPTIONS.get("MISSING_STUDENT_UNIQUE_ID"))

    if student_type == "student":
        if not Students.objects.filter(uniqueId=student_unique_id).exists():
            raise InvalidParamsError(EXCEPTIONS.get("STUDENT_NOT_FOUND_BY_UNIQUE_ID"))
    elif student_type == "graduate":
        if not Graduates.objects.filter(uniqueId=student_unique_id).exists():
            raise InvalidParamsError(EXCEPTIONS.get("STUDENT_NOT_FOUND_BY_UNIQUE_ID"))
    else:
        raise InvalidParamsError(EXCEPTIONS.get("INVALID_STUDENT_TYPE"))

    current_files_count = StudentsAttachments.objects.filter(
        uniqueId=student_unique_id
    ).count()
    if current_files_count + len(files) > 5:
        raise InvalidParamsError(
            EXCEPTIONS.get("MAX_ATTACHMENT_BY_STUDENT").format(maxCount=5)
        )

    results = upload_files(files)
    for file_data in results.get("success"):
        StudentsAttachments(
            createdBy=user_id,
            uniqueId=student_unique_id,
            attachmentId=file_data.get("attachmentId"),
            filename=file_data.get("filename"),
            mimetype=file_data.get("mimetype"),
        ).save()

    return results


def delete_student_attachments(files_data, request_summary):
    if not isinstance(files_data, list):
        raise InvalidParamsError(EXCEPTIONS.get("INVALID_DELETE_ATTACHMENT_REQUEST"))
    for file_data in files_data:
        if "attachmentId" not in file_data or "filename" not in file_data:
            raise InvalidParamsError(
                EXCEPTIONS.get("INVALID_DELETE_ATTACHMENT_REQUEST")
            )

    results = delete_files(files_data)

    deleted_ids = []
    for deleted_file in results.get("success"):
        deleted_ids.append(deleted_file.get("attachmentId"))

    attachments_query = StudentsAttachments.objects.filter(attachmentId__in=deleted_ids)

    payload = {"deleted_attachments": list(attachments_query.values().all())}
    log_activity("Delete Attachment", payload, request_summary)

    attachments_query.delete()

    return results
