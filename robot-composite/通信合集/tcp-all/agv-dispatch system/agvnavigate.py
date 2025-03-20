import socket
import logging
import random
import string
from MessageManager import MessageManager

# AGV 配置
AGV_IP = '192.168.1.101'
AGV_NAVIGATION_PORT = 19206

# 配置日志记录
logging.basicConfig(level=logging.INFO)

class AgvNavigation:
    def __init__(self):
        self.messagemanager = MessageManager()
        self.socket_navigation = None
        self.max_retries = 3  # 最大重连次数
        self.task_id_set = set()  # 存储已使用的 task_id

    def _connect_navigation_socket(self):
        # """尝试连接 AGV 导航 socket"""
        self.close_navigation_socket()  # 先关闭可能存在的连接
        for attempt in range(self.max_retries):
            try:
                # 创建 socket 连接
                self.socket_navigation = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_navigation.connect((AGV_IP, AGV_NAVIGATION_PORT))
                self.socket_navigation.settimeout(5)  # 设置超时
                logging.info("成功连接到 AGV 导航 socket。")
                return
            except (OSError, socket.error) as e:
                logging.error(f"连接 AGV 导航 socket 失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                self.socket_navigation = None
                if attempt == self.max_retries - 1:
                    logging.critical("所有尝试均失败，无法连接导航 socket。")

    def close_navigation_socket(self):
        # """关闭导航 socket 连接"""
        if self.socket_navigation:
            try:
                self.socket_navigation.close()
                logging.info("导航 socket 已成功关闭。")
            except Exception as e:
                logging.error(f"关闭 socket 时发生错误: {e}")
            finally:
                self.socket_navigation = None

    # def _generate_task_id(self):
    #     # """生成唯一的随机 task_id"""
    #     while True:
    #         task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    #         if task_id not in self.task_id_set:
    #             self.task_id_set.add(task_id)  # 添加到集合中，确保唯一性
    #             logging.info(f"生成新的 task_id: {task_id}")
    #             return task_id

    # 生成一个纯数字的8位字符串
    def _generate_task_id(self):
        # """生成唯一的随机 task_id"""
        while True:
            task_id = ''.join(random.choices('0123456789', k=8))  # 生成8位纯数字字符串

            if task_id not in self.task_id_set:
                self.task_id_set.add(task_id)  # 添加到集合中，确保唯一性
                logging.info(f"生成新的 task_id: {task_id}")
                return task_id
            
#########################################################################
          
    # 路径导航--纯路径导航--基本okok
    def nav_go_target(self, source_id, target_id):
        # """导航到目标点"""
        self._connect_navigation_socket()
        if not self.socket_navigation:
            return  # 如果连接失败，直接返回
        try:
            task_id = self._generate_task_id()  # 生成随机 task_id
            message = self.messagemanager.PackMessage(1, 3051, {"source_id": source_id, "id": target_id, "task_id": task_id})
            self.socket_navigation.send(message)
            logging.info(f"发送普通导航指令，从 {source_id} 到 {target_id}，任务 ID: {task_id}。")
            self.task_id_set.remove(task_id)  # 导航完成后移除 task_id
        except Exception as e:
            logging.error(f"发送导航指令时发生错误: {e}")
            self.close_navigation_socket()  # 发送失败后关闭 socket

#########################################################################

    # 路径导航--完整的路径导航
    def nav_go_target_all(self, source_id, target_id):
        # 导航到目标点
        self._connect_navigation_socket()  # 连接导航socket
        if not self.socket_navigation:
            logging.error("导航socket连接失败。")
            return  # 如果连接失败，直接返回
        try:
            task_id = self._generate_task_id()  # 生成随机的task_id
            # 打包导航指令消息
            #  # "source_id": source_id, "id": target_id, "task_id": task_id
            message = self.messagemanager.PackMessage(
                1, 3051, {
                    "source_id": source_id,
                    "id": target_id,
                    # "angle": 1.57,  # 目标方向角度
                    "method": "backward",  # 移动方式只有forward and backward
                    "max_speed": 0.2,  # 最大线速度
                    "max_wspeed": 0.2,  # 最大角速度
                    "max_acc": 0.1,  # 最大线加速度
                    "max_wacc": 0.1,  # 最大角加速度
                    "duration": 100,  # 持续时间
                    # "orientation": 90,  # 目标朝向
                    # "spin": True,  # 是否旋转spin需要激活功能
                    "task_id": task_id  # 任务ID
                }
            )
            self.socket_navigation.send(message)  # 发送导航指令
            logging.info(f"发送普通导航指令，从 {source_id} 到 {target_id}，任务 ID: {task_id}。")
            self.task_id_set.remove(task_id)  # 导航完成后移除task_id
        except Exception as e:
            logging.error(f"发送导航指令时发生错误: {e}")
            self.close_navigation_socket()  # 发送失败后关闭socket


#########################################################################

    # 指定路径导航--两段式
    def nav_go_targetlist(self, source_id_1, source_id_2,target_id):
        # """导航到目标点列表，生成随机的 task_id"""
        self._connect_navigation_socket()  # 连接导航socket
        if not self.socket_navigation:
            logging.error("导航socket连接失败")
            return

        task_id_1 = self._generate_task_id()  # 生成第一个 task_id
        task_id_2 = self._generate_task_id()  # 生成第二个不同的 task_id

        try:
            move_task_list = [
                {
                    "id": source_id_2,
                    "source_id": source_id_1,
                    "task_id": task_id_1
                },
                {
                    "id": target_id,
                    "source_id": source_id_2,
                    "task_id": task_id_2,  # 使用不同的 task_id
                }
            ]
            
            message = self.messagemanager.PackMessage(1, 3066, {"move_task_list": move_task_list})
            self.socket_navigation.send(message)  # 发送导航指令
            logging.info(f"发送指定导航指令，从 {source_id_1} 到 {target_id}，任务 ID: {task_id_1} 和 {task_id_2}。")
            
            # 导航完成后移除 task_id
            self.task_id_set.remove(task_id_1)  
            self.task_id_set.remove(task_id_2)  # 移除第二个 task_id
        except Exception as e:
            logging.error(f"发送指定导航指令时发生错误: {e}")
        finally:
            self.close_navigation_socket()  # 确保在结束时关闭 socket

#########################################################################

    # 指定列表顺序导航okok
    def nav_go_targetlistAll(self, list_ids):
        # """导航到目标点，处理多个源点和目标点"""
        self._connect_navigation_socket()
        if not self.socket_navigation:
            logging.error("导航socket连接失败")
            return

        try:
            for i in range(len(list_ids) - 1):  # 迭代直到倒数第二个元素
                task_id = self._generate_task_id()  # 为每个任务生成唯一的 task_id
                move_task = {
                    "id": list_ids[i + 1],  # 目标点
                    "source_id": list_ids[i],  # 源点
                    "task_id": task_id,
                }

                # 发送导航指令
                message = self.messagemanager.PackMessage(1, 3066, {"move_task_list": [move_task]})
                self.socket_navigation.send(message)
                logging.info(f"发送导航指令，从 {list_ids[i]} 到 {list_ids[i + 1]}，任务 ID: {task_id}。")
                
                # 移除完成的 task_id
                self.task_id_set.remove(task_id)

        except Exception as e:
            logging.error(f"发送指定导航指令时发生错误: {e}")
        finally:
            self.close_navigation_socket()

#########################################################################
    # 平动，以固定速度直线运动固定距离
    def nav_go_line(self, dist,vx,vy):
        # """导航到目标点"""
        self._connect_navigation_socket()
        if not self.socket_navigation:
                logging.error("导航套接字连接失败。")
                return  # 连接失败，直接返回
            # 可选：参数验证
        if dist < 0 or vx < 0 or vy < 0:
            raise ValueError("距离和速度必须为非负值。")
        try:

            message = self.messagemanager.PackMessage(1, 3055,{"dist":dist,"vx":vx,"vy":vy} )
            self.socket_navigation.send(message)

        except Exception as e:
            logging.error(f"发送导航指令时发生错误: {e}. 参数: dist={dist}, vx={vx}, vy={vy}")
        finally:
            self.close_navigation_socket()  # 确保套接字被关闭

#########################################################################
    # 转动, 以固定角速度旋转固定角度
    # mode :0 = 里程模式(根据里程进行运动), 1 = 定位模式, 若缺省则默认为里程模式
    def nav_go_turn(self, angle,vw,mode):
        # """导航到目标点"""
        self._connect_navigation_socket()
        if not self.socket_navigation:
                logging.error("导航套接字连接失败。")
                return  # 连接失败，直接返回
            # 可选：参数验证
        if angle < 0 or vw < 0 :
            raise ValueError("距离和速度必须为非负值。")
        try:
            message = self.messagemanager.PackMessage(1, 3056, {"angle": angle, "vw": vw, "mode": mode})
            self.socket_navigation.send(message)
        except Exception as e:
            logging.error(f"发送转动指令时发生错误: {e}. 参数: angle={angle}, vw={vw}, mode={mode}")
        finally:
            self.close_navigation_socket()  # 确保套接字被关闭

#########################################################################


