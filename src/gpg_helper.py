import gnupg
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

_gpg = gnupg.GPG(gpgbinary='/usr/bin/gpg2', gnupghome='./keys')
_key = "MELONG_MELONG_buy_me_a_MELONA"

def init_secret_key():
    key_path = Path(".", "keys", "GoldMine_CA_KEY")
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if not key_path.exists():
        input_data = _gpg.gen_key_input(key_length=3072, name_real='GoldMine CA', passphrase=_key)
        gen_key = _gpg.gen_key(input_data)

        with open(key_path, 'w') as key_file:
            key_file.write(_gpg.export_keys(gen_key.fingerprint, True, passphrase=_key))
    else:
        with open(key_path, 'r') as key_file:
            _gpg.import_keys(key_file.read())

def scan_pgp_key(data):
    with NamedTemporaryFile() as tempfile:
        tempfile.write(data.encode())
        tempfile.flush()
        scan_result=_gpg.scan_keys(tempfile.name)

    if len(scan_result.fingerprints) == 1:
        return scan_result
    else:
        return None

def sign_data(data):
    signed=_gpg.sign(data, detach=True, passphrase=_key)
    return str(signed)

def validate_signed_data(data, signature):
    with NamedTemporaryFile() as tempsig:
        tempsig.write(signature.encode())
        tempsig.flush()
        verification=_gpg.verify_data(tempsig.name, data.encode())

    return verification.valid
