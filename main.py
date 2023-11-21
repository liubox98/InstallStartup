import os
import time
import logging
import subprocess
from airtest.core.api import connect_device, click, wait, Template
from multiprocessing import Process, Queue

class DevTool:
    def __init__(self) -> None:
        logging.getLogger("airtest").setLevel(logging.WARNING)
        self.parent_directory = os.path.dirname(os.path.abspath(__file__))

        self.APK_PATH = os.path.join(self.parent_directory, 'package', 'ggxc_20231107_2007_0903_ReleaseJudianGp_release_V472.apk')
        self.IMG_DIR = os.path.join(self.parent_directory, 'img')
        self.IMG_OK = os.path.join(self.IMG_DIR, 'OK.png')
        self.IMG_SKIP = os.path.join(self.IMG_DIR, 'Skip.png')
        self.IMG_HOME = os.path.join(self.IMG_DIR, 'Home.png')

        if os.name == 'nt':
            self.ADB = os.path.join(self.parent_directory, 'platform-tools', 'Windows', 'adb.exe')
        else:
            self.ADB = os.path.join(self.parent_directory, 'platform-tools', 'Darwin', 'adb')

        print('='*10, self.ADB, '='*10)

    def connect_dev(self) -> list:
        s = os.popen(f"{self.ADB} devices").read()
        devices = [line.split("\t")[0] for line in s.splitlines() if "\t" in line]
        return devices

    def run_adb_command(self, device, command):
        try:
            subprocess.run([self.ADB, '-s', device] + command, check=True)
        except subprocess.CalledProcessError:
            logging.error(f"执行ADB命令失败：{command}")

    def install(self, dev):
        logging.warning(f"安装应用：{dev}")
        self.run_adb_command(dev, ['install', '-g', self.APK_PATH])

    def start(self, dev):
        logging.warning(f"启动应用：{dev}")
        self.run_adb_command(dev, ['shell', 'am', 'start', '-n', 'com.gardenaffairs.affairsgp/com.tool.plugin.MainActivity'])

    def wait_obj(self, obj):
        obj = wait(Template(obj), timeout=300)
        if obj:
            logging.warning(f"识别到图像：{obj}")
        else:
            logging.error(f"未在指定时间内找到图像：{obj}")

    def click_obj(self, obj):
        obj = click(Template(obj))
        if not obj:
            logging.error(f"未成功点击图像：{obj}")
        else:
            time.sleep(10)

    def uninstall(self, dev):
        logging.warning(f"卸载应用从设备 {dev}")
        self.run_adb_command(dev, ['uninstall', 'com.gardenaffairs.affairsgp'])

def configure_logging():
    # Create a handler and set its formatter
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the root logger
    logging.getLogger().addHandler(handler)

def run_test(dev, dev_id, count=1000):
    device = connect_device(f'Android:///{dev_id}')
    try:
        for _ in range(count):
            logging.warning(f'第 {_ + 1} 次循环开始')
            
            logging.warning("开始安装中...")
            dev.install(dev_id)

            logging.warning("启动应用程序...")
            dev.start(dev_id)

            dev.wait_obj(dev.IMG_SKIP)
            dev.click_obj(dev.IMG_SKIP)

            dev.wait_obj(dev.IMG_OK)
            dev.click_obj(dev.IMG_OK)

            dev.wait_obj(dev.IMG_HOME)

            logging.warning("卸载应用程序...")
            dev.uninstall(dev_id)
            
            logging.warning(f'第 {_ + 1} 次循环结束')
    finally:
        # Disconnect the device when done
        device.disconnect()

if __name__ == '__main__':
    dev = DevTool()

    # Configure logging
    configure_logging()

    processes = []
    for dev_id in dev.connect_dev():
        p = Process(target=run_test, args=(dev, dev_id), )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()