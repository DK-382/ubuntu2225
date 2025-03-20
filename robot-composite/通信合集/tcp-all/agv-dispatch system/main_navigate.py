from agvnavigate import AgvNavigation
# https://seer-group.feishu.cn/wiki/F4oJw8UAtixR13kptt2cLehFnVg
def run_navigation():
    """运行 AGV 导航程序"""
    nav = AgvNavigation()
    try:
        # 执行普通路径导航okok
        # perform_normal_navigation(nav, source_id="2", target_id="1")
        # nav.nav_go_target(source_id="2", target_id="1")

        # 执行完整路径导航okok
        # nav.nav_go_target_all(source_id="1", target_id="2")
        # nav.nav_go_target_all(source_id="2", target_id="1")

#########################################################################
        # 执行三点路径导航okok
        # 执行指定路径导航LM1 -> LM5 -> LM2 
        # nav.nav_go_targetlist(source_id_1="1", source_id_2="5",target_id="2")

        # 执行指定路径导航LM5 -> LM2 -> LM1 
        # nav.nav_go_targetlist(source_id_1="5", source_id_2="2",target_id="1")

        # 执行指定路径导航LM2 -> LM1 -> LM3 
        # nav.nav_go_targetlist(source_id_1="2", source_id_2="1",target_id="3")

######################################################################### 
    
        # 指定列表顺序导航okok
        # 按照指定的列表顺序进行导航5-2-1
        # nav.nav_go_targetlistAll(list_ids=["5","2","1"])
        nav.nav_go_targetlistAll(list_ids=["1","5","2"])
        # nav.nav_go_targetlistAll(list_ids=["1","5","4"]) #第一个有时无效！

#########################################################################
        # 平动，以固定速度直线运动固定距离okok
        # nav.nav_go_line(dist=1.0,vx=0.3,vy=0)

#########################################################################

        # 转动, 以固定角速度旋转固定角度okok
        # nav.nav_go_turn(angle=1.57,vw=1,mode=0)
        # nav.nav_go_turn(angle=3.14,vw=1,mode=0) 
#########################################################################
    except ValueError as e:
        print(f"输入错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")
    finally:
        nav.close_navigation_socket()  # 确保 socket 最终被关闭
        print("导航 socket 已关闭。")

#########################################################################

def perform_normal_navigation(nav, source_id, target_id):
    # """执行普通路径导航"""
    print(f"开始普通路径导航，从 {source_id} 到 {target_id}...")
    nav.nav_go_target(source_id=source_id, target_id=target_id)

if __name__ == "__main__":
    run_navigation()
