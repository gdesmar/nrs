# WARNING: WORK IN PROGRESS
Use this at your own risks

# Source of the code
This code was mostly reused from https://sourceforge.net/projects/nsidis/. It is not the most pythonic library, but it was possible to adapt it to nrs.

# Next steps
The current status is a best-effort level, where a fair bit of cases works, and gives a good idea of the resulting nsi script. Found in the 7z1505-src.7z file under https://sourceforge.net/projects/sevenzip/files/7-Zip/15.05/ is a file named CPP/7zip/Archive/Nsis/NsisIn.cpp which contains close to 6000 lines of code, which explain how to parse the entries to recover the rest of the nsi script. There is a lot of work to be done if this library wants to mimic what 7z had.
