@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib
@echo on

cd ..\..
C:\Python27\python generator.pyc "FritzBox_T064" UTF-8

xcopy .\projects\FritzBox_T064\src .\projects\FritzBox_T064\release

@echo Fertig.

@pause