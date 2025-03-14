function addLists(list1, list2)
    -- 检查两个列表长度是否相等，如果不相等返回nil
    if #list1 ~= #list2 then
        return nil
    end

    -- 创建一个新的列表来存储结果
    local result = {}

    -- 使用for循环遍历列表，进行对应元素相加
    for i = 1, #list1 do
        result[i] = list1[i] + list2[i]
    end

    -- 返回结果列表
    return result
end

-------------------------------------------------------------
-- 变量清理
currentJointA={0}
currentJointDeg={0}
currentPosLine={0}
currentPoseOK={0}

dz=0.1

-- Get Current Point
currentPosLine=getTcpPose()
-- currentPosSend={currentPosLine[1]*1000,currentPosLine[2]*1000,currentPosLine[3]*1000,toDeg(currentPosLine[4]),toDeg(currentPosLine[5]),toDeg(currentPosLine[6])}

cpup=currentPosLine
cpup[3]=cpup[3]+dz

currentJointRad = getJointPositions()-- return rad
currentJointDeg=radToDegList(currentJointRad)

-- 自定义点位
P1JointDeg={-24.24,-11.48,-122.25,-20.81,-90.01,-48.94}
P1JointRad=degToRadList(P1JointDeg)

P1PosOri={-389.93,42.32,294.59,toRad(179.966),toRad(0.0573),toRad(-65.317)}
P1Pos={P1PosOri[1]/1000,P1PosOri[2]/1000,P1PosOri[3]/1000,P1PosOri[4],P1PosOri[5],P1PosOri[6]}

-- P2Pos=P1Pos
-- P2Pos[3]=P1Pos[3]+0.1

manualOffset={0.1,0.1,0.2,0,0,0}
P2Pos=addLists(P1Pos,manualOffset)

---------------------------主控部分--------------------------------
--机械臂移动控制区

-- moveJoint(currentJointRad, 1.0, 1.0, 0, 0)
-- moveJoint(P1JointRad, 1.0, 1.0, 0, 0)

-- moveLine(currentPosLine,1,1,0,0)
-- moveLine(cpup,1,1,0,0)
moveLine(P1Pos,1,1,0,0)
moveLine(P2Pos,1,1,0,0)

setTcpOffset({0,0,0,0,0,0})

moveJoint(inverseKinematics(currentJointRad, P1Pos), 1.0, 1.0, 0, 0)

CPJointRad=getJointPositions()
CPPose=getTcpPose()
pzjPos=forwardKinematics(degToRadList(P1JointRad))
pnjPos=inverseKinematics(currentJointRad, P1Pos)

textmsg("script running finish normally")