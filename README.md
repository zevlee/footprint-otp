![Alt text](https://raw.githubusercontent.com/zevlee/footprint-otp/main/footprint-otp.svg?token=AOK4M5FJGPZVTSIANY2X3ITAVJ2XC)

# Footprint OTP
Footprint OTP is a simple encryption program that uses the [one-time pad](https://en.wikipedia.org/wiki/One-time_pad) technique. It uses the Python [secrets](https://docs.python.org/3/library/secrets.html) module for key generation.

### Signing Key
[Download my signing key here.](https://zevlee.me/sign.txt)

### Building on Windows
1. MSYS2 is needed to build on Windows. [Get it from the MSYS2 website.](https://www.msys2.org/)
2. Download a copy of this repository, then extract it to your home folder for MSYS2 (Usually ``C:\msys64\home\<user>``).
3. Go to your folder for MSYS2 and run ``mingw32.exe``. The following commands will be executed in the console that appears.
4. Enter the ``windows`` directory of the extracted repository.
```
cd footprint-otp/windows
```
5. Run ``bootstrap.sh`` to install any missing dependencies.
```
chmod +x bootstrap.sh && ./bootstrap.sh
```
6. Run ``build.sh``.
```
chmod +x build.sh && ./build.sh
```

### Building on macOS
1. Brew is needed to install PyGObject. [Get it from the brew website.](https://brew.sh)
2. Clone this repository.
```
git clone https://github.com/zevlee/footprint-otp.git
```
3. Enter the ``macos`` directory.
```
cd footprint-otp/macos
```
4. Run ``bootstrap.sh`` to install any missing dependencies.
```
chmod +x bootstrap.sh && ./bootstrap.sh
```
5. Run ``build.sh``.
```
chmod +x build.sh && ./build.sh
```

### Building on Linux
1. Ensure PyGObject is installed.
2. Clone this repository
```
git clone https://github.com/zevlee/footprint-otp.git
```
3. Enter the ``linux`` directory
```
cd footprint-otp/linux
```
4. Run ``bootstrap.sh`` to install pyinstaller via pip if you haven't already.
```
chmod +x bootstrap.sh && ./bootstrap.sh
```
5. Run ``build.sh``.
```
chmod +x build.sh && ./build.sh
```
