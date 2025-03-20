
# AGV 的 IP 和 API 配置
AGV_IP = '192.168.1.101'
AGV_STATUS_PORT = 19204  # 机器人状态端口
AGV_CONTROL_PORT = 19205  # 机器人控制端口
AGV_NAVIGATION_PORT = 19206  # 机器人导航端口
AGV_CONFIG_PORT = 19207  # 机器人配置端口
AGV_OTHER_PORT = 19210  # 其他端口
AGV_PUSHDATA_PORT = 19301  # 机器人推送端口

BATCH_SIZE=10

import socket
import logging
from MessageManager import MessageManager
import json
import os
import time

# 确保日志配置
logging.basicConfig(level=logging.INFO)

#########################################################################
#########################################################################

    # def get_status(self): # 查询机器人信息，编号1000
    #     self._connect_socket()
    #     message = self.messagemanager.PackMessage(1, 1000, {"simple": False})
    #     info_dict = self._send_message(message)
    #     # return info_dict.get("task_status") if info_dict else None
        # if info_dict:
        #     # 输出所有返回的数据
        #     for key, value in info_dict.items():
        #         logging.info(f"{key}: {value}")
        #     return info_dict
        # else:
        #     logging.warning("未能获取 AGV 状态信息。")
        #     return None

        # return info_dict if info_dict else None
           
    # def get_battery_status(self):
    #     self._connect_socket()
    #     message = self.messagemanager.PackMessage(1, 1007, {"charging": True})
    #     info_dict = self._send_message(message)
    #     return info_dict.get("charging") if info_dict else None

    # def get_battery_level(self):
    #     self._connect_socket()
    #     message = self.messagemanager.PackMessage(1, 1007, {"battery_level": True})
    #     info_dict = self._send_message(message)
    #     return info_dict.get("battery_level") if info_dict else None
        # 参考：https://seer-group.feishu.cn/wiki/F5UZw9yorisYgsk92sdcccdQnUd
    # def get_run_req(self): # # 查询机器人的运行状态信息，编号1002
        # self._connect_socket() 
        # message = self.messagemanager.PackMessage(1, 1002)
        # info_dict = self._send_message(message)
        # return info_dict.get(info_dict) if info_dict else None
        # if info_dict:
        #     # 输出所有返回的数据
        #     for key, value in info_dict.items():
        #         logging.info(f"{key}: {value}")
        #     return info_dict
        # else:
        #     logging.warning("未能获取 AGV 状态信息。")
        #     return None

        # return info_dict if info_dict else None

#########################################################################

class AgvStatus:
    def __init__(self):
        self.messagemanager = MessageManager()  # 假设这是定义好的类
        self.socket_status = None
        self.max_retries = 3  # 最大重连次数
        self.agv_ip = '127.0.0.1'  # 修改为实际的 IP
        self.agv_status_port = 12345  # 修改为实际的端口
        self.output_dir = "D:\\46-aubo-agv\\agv-api-seer\\"  # 输出目录
        # self.output_dir = "F:\\02-aubo\\003-文件备份\\AUBOprogram程序\\robot_test\\agv-api-seer\\"  # 输出目录
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

    def _connect_socket(self):
        # 清除上次的 socket 记录
        # self._close_socket()

        for attempt in range(self.max_retries):
            try:
                self.socket_status = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_status.connect((AGV_IP, AGV_STATUS_PORT))
                self.socket_status.settimeout(5)
                return
            except (OSError, socket.error) as e:
                logging.error(f"连接 AGV 状态 socket 失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                self.socket_status = None
        logging.error("所有尝试均失败，无法连接状态 socket。")

    def _send_message(self, message):
        if not self.socket_status:
            logging.error("无法发送消息，因为 socket 未连接。")
            return None
        try:
            self.socket_status.send(message)
            info_dict = self.messagemanager.UnpackMessage(self.socket_status)
            return info_dict
        except Exception as e:
            logging.error(f"发送消息失败: {e}")
            return None

    # 关闭socket连接
    def _close_socket(self):
        if self.socket_status:
            try:
                self.socket_status.close()
                logging.info("Socket 连接已关闭。")
            except Exception as e:
                logging.error(f"关闭 socket 连接时发生错误: {e}")
            finally:
                self.socket_status = None
                
#########################################################################
#########################################################################
    def _write_results_to_file(self, results):
        """将结果写入指定目录的 JSON 文件，分批处理"""
        output_file = os.path.join(self.output_dir, 'method_results101.json')
        BATCH_SIZE = 10  # 每批写入的大小
        for i in range(0, len(results), BATCH_SIZE):
            batch = dict(list(results.items())[i:i + BATCH_SIZE])
            with open(output_file, 'a', encoding='utf-8') as json_file:  # 追加写入
                json.dump(batch, json_file, ensure_ascii=False, indent=4)
                json_file.write("\n")  # 每个批次之间换行
#########################################################################
#########################################################################
    def _call_all_methods(self):
        # self._connect_socket()  # 只连接一次
        results = {}
        
        # 获取所有可调用的方法，排除以 _ 开头的方法
        methods = [
            method for method in dir(self) 
            if callable(getattr(self, method)) 
            and not method.startswith("_")  # 过滤掉以 _ 开头的方法
        ]

        for method_name in methods:
            try:
                result = getattr(self, method_name)()
                
                # 仅在返回值不为 None 时写入结果
                if result is not None:
                    results[method_name] = result
                    print(f"{method_name} 返回: {result}")  # 输出每个方法的返回值

            except Exception as e:
                print(f"{method_name} 调用失败: {e}")  # 输出调用失败的信息
            
            time.sleep(0.1)  # 等待 100 毫秒

        self._close_socket()  # 所有调用完成后关闭连接

        # 将成功的结果写入 JSON 文件
        if results:
            self._write_results_to_file(results)
        return results

#########################################################################
#########################################################################

#########################################################################

    def get_status_info(self): # # 查询机器人状态信息，编号1000
        self._connect_socket() 
        message = self.messagemanager.PackMessage(1, 1000)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def get_status_run(self): # # 查询机器人的运行信息，编号1002
        self._connect_socket() 
        message = self.messagemanager.PackMessage(1, 1002)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_req_location(self): # # 查询机器人的位置状态信息，编号1004
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1004)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_req_speed(self):  # # 查询机器人的速度状态信息，编号1005
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1005)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def get_req_block(self):  # # 查询机器人的被阻挡状态，编号1006
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1006)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
        
    def get_req_battery(self): # # 查询机器人的电池状态，编号1007
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1007)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_req_laser(self):# # 查询激光点云数据 ，编号1009
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1009)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_req_area(self):# # 查询当前所在的区域信息 ，编号1011
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1011)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def get_req_emergency(self):# # 查询机器人急停按钮的状态 ，编号1012
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1012)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_req_io_status(self):# # 查询机器人IO的状态 ，编号1013
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1013)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def get_req_imu_status(self):# # 查询机器人IMU的状态 ，编号1014
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1014)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_req_rfid(self):# # 查询机器人RFID的状态 ，编号1015
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1015)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_req_ultrasonic(self):# # 查询机器人超声传感器数据 ，编号1016
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1016)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def get_req_pgv(self):# # 查询机器人二维码数据 ，编号1017
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1017)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
      
    def get_req_encoder(self):  # # 查询机器人的编码器脉冲值，编号1018
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1018)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def get_nav_task(self):# # 查询机器人导航状态 ，编号1020
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1020)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def get_req_slam(self):# # 查询当前的扫图状态 ，编号1025
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1025)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None


    def get_req_motor(self):# # 查询电机状态信息 ，编号1040
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1040)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_req_alarm(self):# # 查询机器人报警信息 ，编号1050
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1050)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_cur_lock(self):# # 查询机器人当前控制权所有者信息 ，编号1060
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1060)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def get_req_modbus(self): # # 查询机器人的modbus数据，编号1071
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1071)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    

#########################################################################

    def get_status_allA(self):# # 查询机器人批量数据状态 ，编号1100
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1100)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_status_allB(self):# # 查询机器人批量数据状态 ，编号1101
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1101)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_status_allC(self):# # 查询机器人批量数据状态 ，编号1102
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1102)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
         
    def get_package_task(self):# # 查询机器人任务状态 ，编号1110
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1110)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

#########################################################################
   
    def get_map_info(self):# # 查询机器人载入的地图以及储存的地图 ，编号1300
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1300)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_map_station(self):# # 查询机器人当前载入地图中的站点信息 ，编号1301
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1301)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_map_md5(self):# # 查询指定地图列表的MD5值 ，编号1302
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1302)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def get_map_path(self):# # 查询任意两点之间的路径 ，编号1303
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1303)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

#########################################################################

    def get_params_req(self):# # 查询机器人参数信息 ，编号1400
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1400)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None    
    
#########################################################################

    def load_down_model(self):# # 下载机器人模型文件 ，编号1500
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1500)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def script_info(self):# # 查询机器人脚本列表 ，编号1506
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1506)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def script_details_list(self):# # 查询机器人脚本详情列表 ，编号1507
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1507)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def script_args(self):# # 查询机器人脚本默认参数 ，编号1508
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1508)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def calib_support_list(self):# # 查询机器人支持标定列表 ，编号1509
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1509)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def calib_status(self):# # 查询机器人标定状态 ，编号1510
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1510)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def calib_data(self):# # 查询机器人标定文件 ，编号1511
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1511)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

#########################################################################

    def get_3dtag(self):# # 查询建图时的3D二维码 ，编号1665
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1665)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

     
#########################################################################

    def get_file_list(self):# # 查询机器人文件列表 ，编号1798
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1798)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def load_up_file(self):# # 上传机器人文件 ，编号1799
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1799)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
#########################################################################
   
    def load_down_file(self):# # 下载机器人文件 ，编号1800
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1800)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def get_req_bins(self):# # 查询机器人的库位状态信息 ，编号1803
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1803)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    def get_sound_name(self):# # 查询当前播放音频名称 ，编号1850
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1850)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None

    def load_joystick_keymap(self):# # 下载手柄自定义绑定事件 ，编号1852
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1852)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
#########################################################################
         
    def get_transparent_data(self):# # 查询透传的数据信息 ，编号1900
        self._connect_socket()
        message = self.messagemanager.PackMessage(1, 1900)
        info_dict = self._send_message(message)
        return info_dict if info_dict else None
    
    
#########################################################################
