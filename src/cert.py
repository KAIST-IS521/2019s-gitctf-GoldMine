import json
import jsonschema
import os
from db import RecordType, commit_record, edit_record, read_record, record_path
from exceptions import DifferentKeyOwnerException, InvalidKeyException, KeyAlreadyRevokedException
from gpg_helper import init_secret_key, scan_pgp_key, sign_data, validate_signed_data


sign_certificate_schema = {
    "type": "object",
    "properties": {
        "uid": { "type": "string", "pattern": "^[a-zA-Z0-9_]+$" },
        "fingerprint": { "type": "string" },
        "certificate": { "type": "string" },
        "signature": { "type": "string" },
    },
    "required": [ "uid", "fingerprint", "certificate", "signature" ],
    "additionalProperties": False,
}

def initialize():
    init_secret_key()
    init_crl()

def init_crl():
    try:
        crl = []
        edit_record(RecordType.CRL, 'crl', crl)
        commit_record(RecordType.CRL, 'crl', is_new=True)
    except:
        pass

def generate_record(uid):
    new_record = {
        "uid": uid,
        "certificates": []
    }

    edit_record(RecordType.Certificate, uid, new_record)
    commit_record(RecordType.Certificate, uid, is_new=True)

def is_revoked(fingerprint):
    fingerprint = fingerprint.upper()
    crl_record, _ = read_record(RecordType.CRL, 'crl')
    return fingerprint in crl_record

def download_crl():
    crl, _  = read_record(RecordType.CRL, 'crl')
    return json.dumps(crl)

def revoke_key(uid, fingerprint):
    fingerprint = fingerprint.upper()
    cert, _ = read_record(RecordType.Certificate, uid)
    fingerprints = map(lambda x: x['fingerprint'], cert['certificates'])

    if fingerprint not in fingerprints:
        raise DifferentKeyOwnerException()

    if is_revoked(fingerprint):
        raise KeyAlreadyRevokedException()

    fp_list, ref_revision = read_record(RecordType.CRL, 'crl')
    fp_list.append(fingerprint)
    edit_record(RecordType.CRL, 'crl', fp_list)
    commit_record(RecordType.CRL, 'crl', ref_revision)

def delete_head_tail(data):
    return "\n".join(data.strip().splitlines()[1:-1])

def check_name(uid, key_uid):
    return uid == key_uid or key_uid.startswith(uid + " ")

def upload_key(uid, key_data):
    key = scan_pgp_key(key_data)

    if not key:
        raise InvalidKeyException()

    if not check_name(uid, key[0]['uids'][0]):
        raise DifferentKeyOwnerException()

    fingerprint = key[0]['fingerprint']
    if is_revoked(fingerprint):
        raise KeyAlreadyRevokedException()

    cert, ref_revision = read_record(RecordType.Certificate, uid)
    sub = {
        'fingerprint' : fingerprint,
        'certificate' : key_data,
    }

    cert['certificates'].append(sub)

    edit_record(RecordType.Certificate, uid, cert)
    commit_record(RecordType.Certificate, uid, ref_revision)

def download_cert(uid):
    data, _ = read_record(RecordType.Certificate, uid)

    for i in reversed(data['certificates']): # Order by upload time desc
        if not is_revoked(i['fingerprint']):
            data = delete_head_tail(i['certificate'])
            sign = sign_data(data)
            cert = {
                'uid' : uid,
                'signature' : sign,
            }
            cert.update(i)
            return json.dumps(cert)
    else:
        return "Certificate doesn't exist"

def is_valid_format(cert):
    try:
        jsonschema.validate(cert, sign_certificate_schema)
        return True
    except:
        return False

def is_valid_certificate(cert_json):
    cert = json.loads(cert_json)

    if not is_valid_format(cert):
        return False

    uid = cert['uid']
    certificate = cert['certificate']
    key = scan_pgp_key(certificate)
    if not check_name(uid, key[0]['uids'][0]):
        return False

    fingerprint = key[0]['fingerprint']
    if fingerprint != cert['fingerprint'] or is_revoked(fingerprint):
        return False

    return validate_signed_data(delete_head_tail(certificate), cert['signature'])
