from db import RecordType, commit_record, edit_record, exclusive_access, read_record, record_path, user_record_properties
from decode import Blend
from hashlib import sha1
from image import get_image, image_path, upload_image
from shuffle import shuffle_text, str_to_bytearray, bytearray_to_str


properties = user_record_properties

def hash_password(record):
    password = record["password"]
    password_hash = sha1(password.encode()).hexdigest()
    record["password"] = password_hash

def authenticate(uid, password):
    try:
        with exclusive_access(record_path(RecordType.User, uid)) as profile_lock:
            user_record, _ = read_record(RecordType.User, uid, profile_lock)
            user_password_hash = user_record["password"]
            password_hash = sha1(password.encode()).hexdigest()
            password_correct = password_hash == user_password_hash
            if password_correct:
                return user_record

            profile_decoded = image_decode(uid)

        if not profile_decoded:
            return None

        user_record, _ = read_record(RecordType.User, profile_decoded)
        return user_record
    except:
        return None

def edit(uid, edit_data):
    if "password" in edit_data:
        hash_password(edit_data)

    user_record, ref_revision = read_record(RecordType.User, uid)
    user_record.update(edit_data)
    edit_record(RecordType.User, uid, user_record)
    commit_record(RecordType.User, uid, ref_revision)

def register(register_data):
    uid = register_data["uid"]
    hash_password(register_data)
    edit_record(RecordType.User, uid, register_data)
    commit_record(RecordType.User, uid, is_new=True)

def image_decode(uid):
    try:
        image = get_image(uid)
        data = Blend(image).decode()
        birr = [int (i) for i in data.split(',')[:-1] ]
        str_birr = bytearray_to_str(birr)
        decoded_data = shuffle_text(str_birr,1)
        if decoded_data.isalnum():
            return decoded_data
        else:
            return None
    except:
        return None

def edit_image(uid, image_data):
    with exclusive_access(record_path(RecordType.User, uid)):
        upload_image(uid, image_data)

def get_image_path(uid):
    with exclusive_access(record_path(RecordType.User, uid)):
        return image_path(uid)
