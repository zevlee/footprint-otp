### Building on Windows
1. MSYS2 is needed to build on Windows. [Get it from the MSYS2 website.](https://www.msys2.org/)
2. Go to your folder for MSYS2 and run `mingw64.exe`. The following commands will be executed in the console that appears.
3. Install git.
```
pacman -S git
```
4. Clone this repository.
```
git clone https://github.com/zevlee/footprint-otp.git
```
5. Enter the `windows` directory.
```
cd footprint-otp/windows
```
6. Run `bootstrap.sh` to install any missing dependencies.
```
./bootstrap.sh
```
7. Run `build.sh`.
```
./build.sh
```
Build Options
Flag | Description
:-- | :--
`-b` | Build a portable binary (Without this flag, builds an installer)
`-h` | Display help dialog
