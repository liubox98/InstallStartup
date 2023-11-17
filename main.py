import os
import time
import logging
import subprocess
from airtest.core.api import connect_device, click, wait, Template

class DevTool:
    def __init__(self) -> None:
        logging.getLogger("airtest").setLevel(logging.WARNING)
        self.parent_directory = os.path.dirname(os.path.abspath(__file__))
        self.ADB_PATH = os.path.join(self.parent_directory, 'platform-tools', 'adb.exe')
        self.APK_PATH = os.path.join(self.parent_directory, 'package', 'ggxc_20231107_2007_0903_ReleaseJudianGp_release_V472.apk')
        self.IMG_DIR = os.path.join(self.parent_directory, 'img')
        self.IMG_PATH = os.path.join(self.IMG_DIR, 'OK.png')

        connect_device(f'Android:///{dev}' for dev in self.connect_dev())

    def connect_dev(self) -> list:
        s = os.popen(f"{self.ADB_PATH} devices").read()
        devices = [line.split("\t")[0] for line in s.splitlines() if "\t" in line]
        return devices

    def run_adb_command(self, device, command):
        try:
            subprocess.run([self.ADB_PATH, '-s', device] + command, check=True)
        except subprocess.CalledProcessError:
            logging.error(f"执行ADB命令失败：{command}")

    def install(self):
        for dev in self.connect_dev():
            logging.info(f"安装应用到设备 {dev}")
            self.run_adb_command(dev, ['install', '-g', self.APK_PATH])

    def start(self):
        for dev in self.connect_dev():
            logging.info(f"启动应用在设备 {dev}")
            self.run_adb_command(dev, ['shell', 'am', 'start', '-n', 'com.gardenaffairs.affairsgp/com.tool.plugin.MainActivity'])

    def wait_obj(self):
        result = wait(Template(self.IMG_PATH, record_pos=(0.0, 0.077), resolution=(2400, 1080)), timeout=300)
        if not result:
            logging.error(f"未在指定时间内找到图像：{self.IMG_PATH}")

    def click_obj(self):
        result = click(Template(self.IMG_PATH, record_pos=(0.0, 0.077), resolution=(2400, 1080)))
        if not result:
            logging.error(f"未成功点击图像：{self.IMG_PATH}")
        else:
            time.sleep(10)

    def uninstall(self):
        for dev in self.connect_dev():
            logging.info(f"卸载应用从设备 {dev}")
            self.run_adb_command(dev, ['uninstall', 'com.gardenaffairs.affairsgp'])

# 创建 DevTool 实例
dev_tool = DevTool()
dev_tool.uninstall()

for i in range(1000):
    logging.warning(f'第 {i + 1} 次循环开始')
    
    logging.warning("开始安装中...")
    dev_tool.install()

    logging.warning("启动应用程序...")
    dev_tool.start()

    dev_tool.wait_obj()
    dev_tool.click_obj()

    logging.warning("卸载应用程序...")
    dev_tool.uninstall()
    
    logging.warning(f'第 {i + 1} 次循环结束')
