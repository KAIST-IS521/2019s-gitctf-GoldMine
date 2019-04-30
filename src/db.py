import json
import jsonschema
from contextlib import nullcontext
from enum import Enum
from exceptions import FileOnEditException, RecordAlreadyExistsException
from filelock import FileLock
from pathlib import Path
from shutil import move


user_schema = {
    "type": "object",
    "properties": {
        "uid": { "type" : "string", "pattern": "^[a-zA-Z0-9_]+$" },
        "last_name": { "type" : "string" },
        "first_name": { "type" : "string" },
        "email": { "type" : "string" },
        "password": { "type" : "string" },
    },
    "required": [ "uid", "last_name", "first_name", "email", "password" ],
    "additionalProperties": False,
}

user_record_properties = user_schema["properties"].keys()

certificate_schema = {
    "type": "object",
    "properties": {
        "uid": { "type" : "string", "pattern": "^[a-zA-Z0-9_]+$" },
        "certificates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fingerprint": { "type" : "string" },
                    "certificate": { "type" : "string" },
                },
                "required": [ "fingerprint", "certificate" ],
                "additionalProperties": False,
            },
        },
    },
    "required": [ "uid", "certificates" ],
    "additionalProperties": False,
}

crl_schema = {
    "type": "array",
    "items": {
        "type": "string",  # Fingerprint
    },
}

class RecordType(Enum):
    User = 0,
    Certificate = 1,
    CRL = 2,

def exclusive_access(path):
    lock_path = path.with_name("{}.lock".format(path.name))
    return FileLock(lock_path)

def get_revision(path):
    return path.stat().st_mtime

def read_json(path, lock=None):
    with nullcontext() if lock else exclusive_access(path):
        revision = get_revision(path)
        with open(path, "r") as record_file:
            record = json.load(record_file)
            return record, revision

def write_json(path, record, lock=None):
    with nullcontext() if lock else exclusive_access(path):
        if path.exists():
            raise FileOnEditException()
        try:
            with open(path, "w") as record_file:
                json.dump(record, record_file)
        except:
            path.unlink()
            raise

def record_path(record_type, id, is_write=False):
    db_options = {
        RecordType.User: "user",
        RecordType.Certificate: "certificate",
        RecordType.CRL: "crl",
    }

    file_name = "{}.new".format(id) if is_write else id
    return Path(".", "db", db_options[record_type], file_name)

def validate_record(record_type, record):
    schema_options = {
        RecordType.User: user_schema,
        RecordType.Certificate: certificate_schema,
        RecordType.CRL: crl_schema,
    }
    jsonschema.validate(record, schema_options[record_type])

def read_record(record_type, id, lock=None):
    path = record_path(record_type, id, False)
    record, revision = read_json(path, lock)
    validate_record(record_type, record)
    return record, revision

def commit_record(record_type, id, ref_revision=0, is_new=False):
    src = record_path(record_type, id, True)
    dst = record_path(record_type, id, False)
    src_lock = exclusive_access(src)
    dst_lock = exclusive_access(dst)

    with src_lock, dst_lock:
        try:
            if dst.exists():
                if is_new:
                    raise RecordAlreadyExistsException()

                target_revision = dst.stat().st_mtime
                if target_revision != ref_revision:
                    raise FileOnEditException()

            move(src, dst)
        finally:
            if src.exists():
                src.unlink()

def edit_record(record_type, id, record, lock=None):
    path = record_path(record_type, id, True)
    path.parent.mkdir(parents=True, exist_ok=True)
    validate_record(record_type, record)
    write_json(path, record, lock)
