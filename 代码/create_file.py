def mkdir(path):
    # 引入模块
    import os
    import shutil
 
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
 
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)
 
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        　# 创建目录操作函数
        os.makedirs(path)
        os.system("sudo reboot")
        
    else:
        # 如果目录存在则不创建，并提示目录已存在
        shutil.rmtree(path)
 
# 定义要创建的目录
mkpath="/home/pi/Desktop/test"
# 调用函数
mkdir(mkpath)