#!/usr/bin/env python3

from lib.utils import Utils
from base64 import urlsafe_b64encode, urlsafe_b64decode
from os import remove
from os.path import splitext, exists, join
from secrets import token_bytes
from time import time, ctime
from binascii import Error as BinasciiError


class OneTimePad:

    @staticmethod
    def xor(message, key):
        """
        Given bytes inputs `message` and `key`, return the xor of the two
        """
        return bytes(m ^ k for m, k in zip(message, key))

    @staticmethod
    def encrypt_filename(file, enc_names=False, file_dir="", keys_dir=""):
        """
        Given a file as a string input, return an OTP-encoded file and
        corresponding key as file names
        """
        name = Utils.bn(file)
        key = token_bytes(len(name.encode()))
        if enc_names:
            encrypted = urlsafe_b64encode(
                OneTimePad.xor(name.encode(), key)
            ).decode()
            enc_file = f"{join(file_dir, encrypted)}.otp"
        else:
            enc_file = f"{join(file_dir, name)}.otp"
        key_file = f"{join(keys_dir, urlsafe_b64encode(key).decode())}.key"
        return enc_file, key_file

    @staticmethod
    def decrypt_filename(file, key_file, file_dir=""):
        """
        Given a string file and corresponding key, return the decrypted
        file name
        """
        if Utils.bn(file)[-4:] == ".otp":
            filename = Utils.bn(file)[:-4].encode()
        else:
            filename = Utils.bn(file).encode()
        key = urlsafe_b64decode(Utils.bn(key_file[:-4]).encode())
        try:
            dec_file = OneTimePad.xor(
                urlsafe_b64decode(filename), key
            ).decode()
        except BinasciiError:
            dec_file = filename.decode()
        dec_file = join(file_dir, dec_file)
        return dec_file

    @staticmethod
    def encrypt_file(
        file,
        file_dir="",
        keys_dir="",
        log_dir="",
        enc_names=False,
        del_toggle=False
    ):
        """
        Given a file, writes the encrypted message and corresponding key to
        separate files
        """
        msg = open(file, "rb").read()
        key = token_bytes(len(msg))
        encrypted = OneTimePad.xor(msg, key)
        enc_file, key_file = OneTimePad.encrypt_filename(
            file, enc_names, file_dir, keys_dir
        )

        # Write to files
        with open(enc_file, "wb") as e:
            e.write(encrypted)
            e.close()
        with open(key_file, "wb") as k:
            k.write(key)
            k.close()
        log = f"{file}\n{enc_file}\n{key_file}\n{ctime(time())}\n\n"
        log_file = join(log_dir, "otp.log")
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

    @staticmethod
    def decrypt_file(
        file,
        key_file,
        file_dir="",
        log_dir="",
        del_toggle=False
    ):
        """
        Given a file and key file, reads the encrypted message from file using
        the key from key_file
        """
        msg = open(file, "rb").read()
        key = open(key_file, "rb").read()
        decrypted = OneTimePad.xor(msg, key)
        dec_file = OneTimePad.decrypt_filename(file, key_file, file_dir)
        if del_toggle:
            remove(file)
            remove(key_file)
            try:
                log_file = join(log_dir, "otp.log")
                old_log = open(log_file, "r").readlines()
                files = [Utils.bn(line[:-1]) for line in old_log]
                # Find the index of the file name
                ind = files.index(Utils.bn(file)) - 1
                # Designate the indices of the lines to be removed i.e. the
                # file and the four lines immediately following it
                rmv = []
                for i in range(5):
                    rmv.append(ind + i)
                # Updated log contains everything but the removed item
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
