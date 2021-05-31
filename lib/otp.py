#!/usr/bin/env python3

from base64 import urlsafe_b64encode, urlsafe_b64decode
from os import remove
from os.path import splitext, exists, basename, normpath, join, expanduser
from secrets import token_urlsafe
from time import time, ctime
from binascii import Error as BinasciiError


def generate_key(length):
    """
    Given an integer `length`, return a Base64-encoded key with `length`
    randomly generated bytes
    """
    key = token_urlsafe(-(length * -3 // 4))  # always rounds up
    return key.encode()


def xor(message, key):
    """
    Given bytes inputs `message` and `key`, return the xor of the two
    """
    xored = b""
    for m, k in zip(message, key):
        xored += chr(m ^ k).encode()
    return xored


def bn(name):
    return basename(normpath(name))


def encrypt_file_name(file, enc_names=False, file_dir="", keys_dir=""):
    """
    Given a file as a string input, return an OTP-encoded file and
    corresponding key as file names
    """
    name = bn(file)
    key = generate_key(len(name.encode()))
    if enc_names:
        encrypted = xor(name.encode(), key)
        encrypted = urlsafe_b64encode(encrypted).decode()
        enc_file = f"{join(file_dir, encrypted)}.otp"
    else:
        enc_file = f"{join(file_dir, name)}.otp"
    key_file = f"{join(keys_dir, key.decode())}.key"
    return enc_file, key_file


def decrypt_file_name(file, key_file, file_dir=""):
    """
    Given a string file and corresponding key, return the decrypted file name
    """
    if bn(file)[-4:] == ".otp":
        file_name = bn(file)[:-4].encode()
    else:
        file_name = bn(file).encode()
    key = bn(key_file[:-4]).encode()
    try:
        dec_file = xor(urlsafe_b64decode(file_name), key).decode()
    except BinasciiError:
        dec_file = file_name.decode()
    dec_file = join(file_dir, dec_file)
    return dec_file


def encrypt_file(
    file,
    file_dir="",
    keys_dir="",
    enc_names=False,
    del_toggle=False
):
    """
    Given a file, writes the encrypted message and corresponding key to
    separate files
    """
    msg = open(file, "rb").read()
    key = generate_key(len(msg))
    encrypted = xor(msg, key)
    enc_file, key_file = encrypt_file_name(file, enc_names, file_dir, keys_dir)

    # write to files
    with open(enc_file, "wb") as e:
        e.write(encrypted)
        e.close()
    with open(key_file, "wb") as k:
        k.write(key)
        k.close()
    log = f"{file}\n{enc_file}\n{key_file}\n{ctime(time())}\n\n"
    log_file = join(expanduser("~"), ".footprint-otp", "otp.log")
    try:
        with open(log_file, "a") as logfile:
            logfile.write(log)
            logfile.close()
    except FileNotFoundError:
        with open(log_file, "w") as logfile:
            logfile.write(log)
            logfile.close()
    if del_toggle:
        remove(file)
    return enc_file, key_file


def decrypt_file(
    file,
    key_file,
    file_dir="",
    del_toggle=False
):
    """
    Given a file and key file, reads the encrypted message from file using the
    key from key_file
    """
    msg = open(file, "rb").read()
    key = open(key_file, "rb").read()
    decrypted = xor(msg, key)
    dec_file = decrypt_file_name(file, key_file, file_dir)
    if del_toggle:
        remove(file)
        remove(key_file)
        try:
            log_file = join(expanduser("~"), ".footprint-otp", "otp.log")
            old_log = open(log_file, "r").readlines()
            files = [bn(line[:-1]) for line in old_log]
            # find the index of the file name
            ind = files.index(bn(file)) - 1
            # designate the indices of the lines to be removed i.e. the file
            # and the four lines immediately following it
            rmv = []
            for i in range(5):
                rmv.append(ind + i)
            # updated log contains everything but the removed item
            new_log = [j for i, j in enumerate(old_log) if i not in rmv]
            with open(log_file, "w") as logfile:
                for line in new_log:
                    logfile.write(line)
                logfile.close()
        except ValueError:
            pass
    dec, ext = splitext(dec_file)
    if exists(f"{dec}{ext}"):
        i = 0
        while exists(f"{dec}({str(i)}){ext}"):
            i += 1
        dec_file = f"{dec}({str(i)}){ext}"
    with open(dec_file, "wb") as d:
        d.write(decrypted)
        d.close()
    return dec_file
