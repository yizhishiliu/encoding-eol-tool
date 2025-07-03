@echo off
echo 正在使用 Cython 编译 core_logic.py 为 core_logic.pyd ...
python setup.py build_ext --inplace
pause
