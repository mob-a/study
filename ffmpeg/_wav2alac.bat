@echo off

set FFMPEG_PATH="c:\MY_Program_Files\ffmpeg-4.0.2-win64-static\bin\ffmpeg.exe"
pushd %0\..
cls

mkdir m4a

for %%f in ( *wav ) do (   
   %FFMPEG_PATH% -i "%%f" -acodec alac "m4a\%%~nf.m4a"
)
