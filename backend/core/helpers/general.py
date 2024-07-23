import datetime
from collections import namedtuple

import environ
import gridfs
from django.db import connections
from django.utils import timezone
from bson.objectid import ObjectId
from pymongo import MongoClient

from core.models.db import User
from core.utils.exceptions import InternalServerError
from core.utils.messages import EXCEPTIONS


def get_signature(record: dict[str, any]):
    user_name = ""
    user_id = record.get("createdBy")
    update_date = record.get("createdAt")
    if record.get("updatedBy") and record.get("updatedAt"):
        user_id = record.get("updatedBy")
        update_date = record.get("updatedAt")
    if (not user_id and user_id != 0) or not update_date:
        return {}
    if user_id == 0:
        user_name = "النظام|System"
    else:
        user = User.objects.filter(id=user_id).values("fullname").first()
        user_name = user.get("fullname") if user else "مستخدم غير معروف|Unknown User"
    return {
        "signatureId": user_id,
        "signatureName": user_name,
        "signatureDate": update_date,
    }


# Functions to get data from request
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_app_url(request):
    path = ""
    split_path = request.path.split("/")
    for index in range(1, len(split_path) - 2):
        path += "/" + split_path[index]
    return path


def get_request_summary(request):
    summary = {
        "TIMESTAMP": timezone.now(),
        "IP": get_client_ip(request),
        "APP_PATH": get_app_url(request),
        "FULL_PATH": request.path,
    }
    if isinstance(request.user, dict):
        summary["USER_ID"] = request.user.get("id")
    return summary


# Json Serialization Related Functions
def adjust_date_attr(value):
    return str(value)


def adjust_list_attrs(value):
    for index, item in enumerate(value):
        if isinstance(item, dict):
            value[index] = adjust_dict_attrs(item)
        elif isinstance(item, list):
            value[index] = adjust_list_attrs(item)
        elif isinstance(item, datetime.date):
            value[index] = adjust_date_attr(item)
    return value


def adjust_dict_attrs(item):
    for (key, value) in item.items():
        if type(value) == datetime.date:
            item[key] = adjust_date_attr(value)
        elif isinstance(value, dict):  # recurse into sub-docs
            item[key] = adjust_dict_attrs(value)
        elif isinstance(value, list):  # recurse into sub-docs
            item[key] = adjust_list_attrs(value)
    return item


# Mongo Related Functions
def get_mongo_db_connection():
    env = environ.Env(MONGO_DB_PORT=(int, 0))
    client = MongoClient(
        host=env("MONGO_DB_HOST"),
        port=env("MONGO_DB_PORT"),
        username=env("MONGO_DB_USERNAME"),
        password=env("MONGO_DB_PASSWORD"),
        authSource=env("MONGO_DB_NAME"),
    )
    db = client[env("MONGO_DB_NAME")]
    return db


# Log Related Functions
def log_activity(
    message: str, payload: dict[str, any], request_summary: dict[str, any]
):
    try:
        db = get_mongo_db_connection()
        collection = db["activitieslogs"]
        formalized_log = {
            "createdAt": request_summary.get("TIMESTAMP", timezone.now()),
            "createdBy": request_summary.get("USER_ID", 0),
            "clientIP": request_summary.get("IP", "unknown"),
            "pathURL": request_summary.get("FULL_PATH", "unknown"),
            "message": message,
            "payload": payload,
        }
        formalized_log = adjust_dict_attrs(formalized_log)
        collection.insert_one(formalized_log)
    except (Exception):
        raise InternalServerError(EXCEPTIONS.get("MONGO_INTERNAL_ERROR"))


def log_user_auth(message: str, request_summary: dict[str, any]):
    try:
        db = get_mongo_db_connection()
        collection = db["authlogs"]
        formalized_log = {
            "createdAt": request_summary.get("TIMESTAMP", timezone.now()),
            "createdBy": request_summary.get("USER_ID", 0),
            "clientIP": request_summary.get("IP", "unknown"),
            "message": message,
        }
        collection.insert_one(formalized_log)
    except (Exception):
        raise InternalServerError(detail=EXCEPTIONS.get("MONGO_INTERNAL_ERROR"))


# SQL Related Functions
def dict_fetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def namedtuple_fetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def run_sql_command(sql_query, sql_params, fetch_mode=0, target_db="default"):
    with connections[target_db].cursor() as cursor:
        cursor.execute(sql_query, sql_params)
        if fetch_mode == 0:
            return cursor.fetchone()
        elif fetch_mode == 1:
            return cursor.fetchall()
        elif fetch_mode == 2:
            return dict_fetchall(cursor)
        elif fetch_mode == 3:
            return namedtuple_fetchall(cursor)


def can_upload_file(file):
    max_bytes = 2097152
    max_size_str = "2MB"
    allowed_mimetypes = ["image/png", "image/jpeg", "application/pdf"]
    allowed_types_str = "jpeg, jpg, png, pdf"

    if file.size > max_bytes:
        return {
            "success": False,
            "message": EXCEPTIONS.get("INVALID_FILE_SIZE").format(max=max_size_str),
        }

    if file.content_type not in allowed_mimetypes:
        return {
            "success": False,
            "message": EXCEPTIONS.get("INVALID_FILE_TYPE").format(
                types=allowed_types_str
            ),
        }

    return {"success": True}


def upload_files(files):
    try:
        db = get_mongo_db_connection()
        fs = gridfs.GridFS(db, "studentsattachments")
        uploaded = []
        failed = []
        for file in files:
            result = can_upload_file(file)
            if result.get("success"):
                file_id = fs.put(file, filename=file.name)
                uploaded.append(
                    {
                        "attachmentId": str(file_id),
                        "filename": file.name,
                        "mimetype": file.content_type,
                    }
                )
            else:
                failed.append(
                    {
                        "filename": file.name,
                        "message": result.get("message"),
                    }
                )

        return {"success": uploaded, "failed": failed}

    except (Exception):
        raise InternalServerError(detail=EXCEPTIONS.get("GRID_FS_INTERNAL_ERROR"))


def get_file(id):
    try:
        db = get_mongo_db_connection()
        fs = gridfs.GridFS(db, "studentsattachments")
        if not fs.exists(ObjectId(id)):
            raise InternalServerError(detail=EXCEPTIONS.get("GRID_FS_FILE_NOT_FOUND"))
        return fs.get(ObjectId(id))

    except (Exception):
        raise InternalServerError(detail=EXCEPTIONS.get("GRID_FS_INTERNAL_ERROR"))


def delete_files(files_data):
    try:
        db = get_mongo_db_connection()
        fs = gridfs.GridFS(db, "studentsattachments")

        deleted_files = []
        not_found_files = []

        for file_data in files_data:
            file_id = file_data.get("attachmentId")
            if fs.exists(ObjectId(file_id)):
                fs.delete(ObjectId(file_id))
                deleted_files.append(file_data)
            else:
                file_data["message"] = EXCEPTIONS.get("GRID_FS_FILE_NOT_FOUND")
                not_found_files.append(file_data)

        return {"success": deleted_files, "failed": not_found_files}

    except (Exception):
        raise InternalServerError(detail=EXCEPTIONS.get("GRID_FS_INTERNAL_ERROR"))
