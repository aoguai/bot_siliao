"""私聊转发"""
from botoy import GroupMsg, FriendMsg, Picture, Text
from botoy.collection import MsgTypes
from botoy.decorators import ignore_botself, startswith
from botoy.parser import group as gp# 群消息(GroupMsg)相关解析
from botoy.parser import friend as fp # 好友消息(FriendMsg)相关解析
from botoy import jconfig, logger
from botoy import Action
import demjson,httpx,re,time

action = Action(qq=botQQ)

#黑名单
arr = [
    	"123456"
      ]

#检测到以下内容不转发
arr2 = [
    	"赞我",
        "B站",
    	"答案之书",
        "历史上的今天",
    	"翻译",
        "签到",
    	"天气",
        "豆瓣排行榜",
    	"毒鸡汤",
        "舔狗日记",
    	"土味情话",
        "一言",
    	"佛系语录",
        "诗词",
    	"渣男语录",
        "nmsl",
    	"彩虹屁",
        "网易云热评",
    	"唱首歌",
        "微博热榜",
    	"吃点啥",
        "垃圾分类",
    	"查",
        "表情包",
    	"是啥梗",
        "二维码生成"
      ]

#转发到的QQ
boss_uin=123456

@ignore_botself#忽略机器人自身的消息
def receive_friend_msg(ctx: FriendMsg):
    #当uin为boss时
    if(ctx.FromUin==boss_uin):
        if ctx.Content =="打开私聊转发":
            Text(switch('0'))
        elif ctx.Content =="关闭私聊转发":
            Text(switch('1'))
        elif ctx.MsgType=="ReplayMsg":  # 回复消息
            reply_Pic=""
            data_text=demjson.decode(ctx.Content)
            SrcContent_text=data_text['SrcContent'] #回复的消息的内容
            try:
                reply_Pic=data_text['FriendPic'][0]['Url'] #实际需要回复的内容
                try:
                    reply_text=data_text['Content'] # 实际需要回复的内容
                except Exception as e:
                    reply_text="" # 没有需要回复的内容
            except Exception as e: #没有需要回复的图像
                reply_text=data_text['Content'] # 实际需要回复的内容
            Uin=getReplyUin(SrcContent_text,reply_text) # 获取回复人UIN
            if Uin == boss_uin:  # 如果为boss
                return
            # 用于判断是否为图文消息时候手动指定回复人
            if len(re.findall("(\(.*\))",reply_text))>0:  # 真
                if reply_Pic == "": #没有图片时
                    action.sendFriendText(Uin,reply_text.replace(re.findall("(\(.*\))",reply_text)[0], ""))
                else:
                    try:
                        #文本和图片同时存在
                        action.sendFriendPic(user=Uin,picUrl=reply_Pic,content=reply_text.replace(re.findall("(\(.*\))",reply_text)[0], ""))
                    except Exception as e:
                        #仅为图片
                        action.sendFriendPic(user=Uin,picUrl=reply_Pic)
            else:
                if reply_Pic == "": #没有图片时
                    action.sendFriendText(Uin,reply_text)
                else:
                    try:
                        #文本和图片同时存在
                        action.sendFriendPic(user=Uin,picUrl=reply_Pic,content=reply_text)
                    except Exception as e:
                        #仅为图片
                        action.sendFriendPic(user=Uin,picUrl=reply_Pic)
    else:
        #其他人，判断是否需要转发
        if switch('2') == "0" :  # 转发功能打开时
            Uin=str(ctx.FromUin)  # 获取回复人UIN
            for i in range(len(arr)):  # 判断是否黑名单
                if arr[i] == Uin :
                    return
            cont=ctx.Content  # 获取待转发消息
            for i in range(len(arr2)):  # 判断是否为不需要回复消息
                if cont.find(arr2[i])!=-1:
                    return
            time_text=time.strftime("%Y/%m/%d %H:%M:%S")  # 获取消息时间
            if ctx.MsgType=="TextMsg":  # 当为文本消息时
                action.sendFriendText(boss_uin,"收到一条私聊\n来自："+getTou(Uin)+"("+Uin+") "+ time_text+"\n“"+cont+"”")
            elif ctx.MsgType=="PicMsg":  # 当为图文消息时
                data_text=demjson.decode(ctx.Content)  # 回复的消息的内容
                FriendPic_text=data_text['FriendPic'][0]
                picUrl_text=FriendPic_text['Url']  # 图片url
                try:
                    #文本和图片同时存在
                    cont_text=data_text['Content']
                    action.sendFriendPic(user=boss_uin,picUrl=picUrl_text,content="收到一条私聊\n来自："+getName(Uin)+"("+Uin+") "+ time_text+"\n“"+cont_text+"”")
                except Exception as e:
                    #仅为图片
                    action.sendFriendPic(user=boss_uin,picUrl=picUrl_text,content="收到一条私聊\n来自："+getName(Uin)+"("+Uin+") "+ time_text)


#打开关闭功能
def switch(text):
    filename = './plugins/bot_siliao/switch.txt'
    if text == "0":
        with open(filename, "w+") as f:  # 打开文件
            f.write("0")
            return "打开私聊转发成功"
    elif text == "1":
        with open(filename, "w+") as f:  # 打开文件
            f.write("1")
            return "关闭私聊转发成功"
    else:
        with open(filename, "r") as f:  # 打开文件
            data = f.read()  # 读取文件
            return data

#获取QQ昵称
def getName(uin):
    url = "https://api.usuuu.com/qq/"+uin
    try:
        res = httpx.get(url).json()
    except Exception as e:
        logger.warning(f"昵称请求失败\r\n {e}")
        return
    logger.success(f"昵称请求: {res}")
    return res['data']['name']
   
#获取回复人UIN
def getReplyUin(text,reply_text):
    result=re.findall("(\(.*\))", text)
    if len(result)<1:
        result=re.findall("(\(.*\))",reply_text)
    try:
        return int(result[0].replace("(", "").replace(")", ""))
    except Exception as e:
        return 1340219674