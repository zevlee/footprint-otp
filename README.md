# Footprint OTP
Footprint OTP is an encryption program that uses a simple stream cipher. It uses the Python [secrets](https://docs.python.org/3/library/secrets.html) module for key generation.

Work is currently being done to implement a hardware random number generator for key generation in order to use truly random bytes.

### Signing Key
[Download my signing key here.](https://zevlee.me/sign.txt)

### Building on Windows
1. MSYS2 is needed to build on Windows. [Get it from the MSYS2 website.](https://www.msys2.org/)
2. Go to your folder for MSYS2 and run ``mingw64.exe``. The following commands will be executed in the console that appears.
3. Install git.
```
pacman -S git
```
4. Clone this repository.
```
git clone https://github.com/zevlee/footprint-otp.git
```
5. Enter the ``windows`` directory.
```
cd footprint-otp/windows
```
6. Run ``bootstrap.sh`` to install any missing dependencies.
```
chmod +x bootstrap.sh && ./bootstrap.sh
```
7. Run ``build.sh``.
```
chmod +x build.sh && ./build.sh
```

### Building on macOS
1. Homebrew is needed to install PyGObject. [Get it from the Homebrew website.](https://brew.sh)
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
Enable code signing by adding the Common Name of the certificate as the first argument. Without this, adhoc signing will be used.
```
./build.sh "Developer ID Application: Name Here (TEAMIDHERE)"
```
Enable notarization by also adding the name of a stored keychain profile.
```
./build.sh "Developer ID Application: Name Here (TEAMIDHERE)" "keychain-profile-here"
```
Notarization can alternatively be enabled by adding Apple ID, Team ID, and an app-specific password as subsequent arguments.
```
./build.sh "Developer ID Application: Name Here (TEAMIDHERE)" "appleid@here.com" "TEAMIDHERE" "pass-word-goes-here"
```

### Building on Linux
1. Ensure PyGObject is installed.
2. Clone this repository.
```
git clone https://github.com/zevlee/footprint-otp.git
```
3. Enter the ``linux`` directory.
```
cd footprint-otp/linux
```
4. Run ``bootstrap.sh`` to install any missing dependencies.
```
chmod +x bootstrap.sh && ./bootstrap.sh
```
5. Run ``build.sh``.
```
chmod +x build.sh && ./build.sh
```
