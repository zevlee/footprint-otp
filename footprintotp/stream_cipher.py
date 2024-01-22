#!/usr/bin/env python3

from . import bn, Utils
from base64 import urlsafe_b64encode, urlsafe_b64decode
from os import remove
from os.path import splitext, exists, join
from time import time, ctime
from binascii import Error as BinasciiError


class StreamCipher:

    @staticmethod
    def xor(message, key):
        """
        Given bytes inputs `message` and `key`, return the bitwise XOR of the two
        
        :param message: Message
        :type message: bytes
        :param key: Key
        :type key: bytes
        :return: Bitwise XOR of message and key
        :rtype: bytes
        """
        return bytes(m ^ k for m, k in zip(message, key))

    @staticmethod
    def encrypt_filename(filename, key_file, enc_names=False, file_dir="", keys_dir=""):
        """
        Given a filename as a string input, return an OTP-encoded file and
        corresponding key as file names
        
        :param filename: Filename
        :type filename: str
        :param key_file: Key filename
        :type key_file: str
        :param enc_names: Encrypt filenames option
        :type enc_names: bool
        :param file_dir: File directory
        :type file_dir: str
        :param keys_dir: Keys directory
        :type keys_dir: str
        :return: Tuple of encrypted filename and key filename
        :rtype: tuple
        """
        name = bn(filename)
        key = bn(key_file)
        if enc_names:
            encrypted = urlsafe_b64encode(
                StreamCipher.xor(name.encode(), key.encode())
            ).decode()
            enc_file = f"{join(file_dir, encrypted)}.otp"
        else:
            enc_file = f"{join(file_dir, name)}.otp"
        key_file = join(keys_dir, key)
        return enc_file, key_file

    @staticmethod
    def decrypt_filename(filename, key_file, file_dir=""):
        """
        Given a string file and corresponding key, return the decrypted
        file name
        
        :param filename: Filename
        :type filename: str
        :param key_file: Key filename
        :type key_file: str
        :param file_dir: File directory
        :type file_dir: str
        :return: Decrypted file name
        :rtype: str
        """
        if bn(filename)[-4:] == ".otp":
            dec_file = bn(filename)[:-4].encode()
        else:
            dec_file = bn(filename).encode()
        key = bn(key_file).encode()
        try:
            dec_file = StreamCipher.xor(
                urlsafe_b64decode(dec_file), key
            ).decode()
        except BinasciiError:
            dec_file = dec_file.decode()
        dec_file = join(file_dir, dec_file)
        return dec_file

    @staticmethod
    def encrypt_file(
        filename,
        key_file,
        file_dir="",
        keys_dir="",
        log_dir="",
        enc_names=False,
        del_toggle=False
    ):
        """
        Given a filename, writes the encrypted message and corresponding key to
        separate files
        
        :param filename: Filename
        :type filename: str
        :param key_file: Key filename
        :type key_file: str
        :param file_dir: File directory
        :type file_dir: str
        :param keys_dir: Keys directory
        :type keys_dir: str
        :param log_dir: Log directory
        :type log_dir: str
        :param enc_names: Encrypt filenames option
        :type enc_names: bool
        :param del_toggle: Delete files option
        :type del_toggle: bool
        :return: Tuple of encrypted filename and key filename
        :rtype: tuple
        """
        msg = open(filename, "rb").read()
        key = open(key_file, "rb").read()
        encrypted = StreamCipher.xor(msg, key)
        enc_filename, key_filename = StreamCipher.encrypt_filename(
            filename, key_file, enc_names, file_dir, keys_dir
        )

        # Write to files
        with open(enc_filename, "wb") as e:
            e.write(encrypted)
            e.close()
        with open(key_filename, "wb") as k:
            k.write(key)
            k.close()
        log = f"{filename}\n{enc_filename}\n{key_filename}\n{ctime(time())}\n\n"
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
            remove(filename)
        return enc_filename, key_filename

    @staticmethod
    def decrypt_file(
        filename,
        key_file,
        file_dir="",
        log_dir="",
        del_toggle=False
    ):
        """
        Given a file and key file, reads the encrypted message from file using
        the key from key_file
        
        :param filename: Filename
        :type filename: str
        :param key_file: Key filename
        :type key_file: str
        :param file_dir: File directory
        :type file_dir: str
        :param log_dir: Log directory
        :type log_dir: str
        :param del_toggle: Delete files option
        :type del_toggle: bool
        :return: Decrypted filename
        :rtype: str
        """
        msg = open(filename, "rb").read()
        key = open(key_file, "rb").read()
        decrypted = StreamCipher.xor(msg, key)
        dec_file = StreamCipher.decrypt_filename(filename, key_file, file_dir)
        if del_toggle:
            remove(filename)
            remove(key_file)
            try:
                log_file = join(log_dir, "otp.log")
                old_log = open(log_file, "r").readlines()
                files = [bn(line[:-1]) for line in old_log]
                # Find the index of the filename
                ind = files.index(bn(filename)) - 1
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
