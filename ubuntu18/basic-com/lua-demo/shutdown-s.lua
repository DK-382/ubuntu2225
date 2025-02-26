-- 获取当前时间
local os = require("os")
local now = os.date("*t") -- 获取当前时间

-- 判断是否是晚上六点以后
if now.hour >= 18 then
    -- 执行关机命令
    print("关机进行中...")
    os.execute("shutdown -h now")
else
    print("It's not yet 18:00. No shutdown.")
end