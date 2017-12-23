#coding=utf-8
from Tkinter import *
import random
import time
import copy
import numpy as np
import pickle
import copy

PINGJU = 2
MINE = 1
ENEMY = 2
SHUANGSAN = 98
class GAME():#游戏类
    z_height=30
    now,step,over,qipu,qipu_predict=0,0,-1,{},{}
    C,Z=0,0
    black_score = 0
    white_score = 0
    def __init__(self,dw,g_height,g_width):
        self.dw,self.g_height,self.g_width=dw,g_height,g_width
        self.height,self.width=self.g_height*self.dw+self.z_height,self.g_width*self.dw
        self.window = Tk()
        self.window.title(u'五子棋')
        self.center_window()
        self.window.bind('<Key>', self.key)
        self.qipan()
        self.zhuangtai()
        self.window.mainloop()

    def center_window(self):
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        x = (ws/2) - (self.width/2)
        y = (hs/2) - (self.height/2)
        self.window.minsize(self.width,self.height)
        self.window.maxsize(self.width,self.height)
        self.window.geometry('%dx%d+%d+%d' % (self.width, self.height, x, y))

    #每局结束后调用这个开启新的一局
    def clear_window(self):
        self.now, self.step, self.over, self.qipu = 0, 0, -1, {}
        self.qipan(True)
        self.zhuangtai()

    #按键响应
    def key(self,e):
        print e.keycode
        if e.keycode==116 and self.over!=-1: #F5 重新开局
            self.clear_window()
        if e.keycode == 32 and self.over == -1: #空格 自动下棋
            self.auto_compete(10)
        if e.keycode == 81: #Q - 显示最后一步棋谱
            self.clear_window()
            self.show_final_qipu()
        if e.keycode == 84: #T - 自动训练局
            self.train_compete(100)

    #画棋盘
    def qipan(self,z=False):
        if z==False:
            self.C = Canvas(self.window, bg="#009900", height=self.height, width=self.width)
        else:
            self.C.delete("all")

        for i in xrange(self.g_width+1):
            self.C.create_line((i-1)*self.dw,0+self.z_height,(i-1)*self.dw,self.height,fill="#333333")
        for i in xrange(self.g_height+1):
            self.C.create_line(0,(i-1)*self.dw+self.z_height,self.width,(i-1)*self.dw+self.z_height,fill="#333333")
        if z==False:
            self.C.bind("<Button-1>", self.click)
            self.C.bind('<Button-3>', self.visual_input)
            self.C.pack()

    #状态栏更新
    def zhuangtai(self):
        text=u"黑：白 = "+ str(self.black_score) + u":" + str(self.white_score) + u"   游戏状态:"
        if self.step==0:
            text+=u" 游戏开始,黑棋先走"
        elif self.over==2:
            text+=u" 游戏平局，按F5重新开始"
        elif self.over!=-1:
            text+=u" 游戏结束 "+(u"黑棋" if self.over==0 else u"白棋")+u"胜利! 按F5重新开始"
            if self.now==1:self.black_score+=1
            else:self.white_score+=1
        elif self.step==self.g_width*self.g_height:
            text+=u" 游戏结束 和棋! 按F5重新开始"
        else:
            text+=u" 当前"+(u"黑棋" if self.now==0 else u"白棋")+u"走棋 总共"+str(self.step)+u"步"
        self.Z = Label( self.C, text=" "*len(text)*4+text,justify="right",width=self.width*2)
        self.Z.place(anchor="n",height=self.z_height)

    #自动对局N盘，状态栏可以看到对战结果
    def auto_compete(self,num):
        for i in range(num):
            self.visual_input(is_sleep=False)
            self.clear_window()


    # 下一步最优落子点
    def best_step0(self):
        if self.step == 0:
            return self.g_width / 2, self.g_height / 2

        step_score = np.zeros((self.g_width, self.g_height, 2))
        for i in range(self.g_width):
            for j in range(self.g_height):
                for k in range(2):
                    if str(i) + "-" + str(j) not in self.qipu:
                        step_score[i, j, k] = self.get_logic_score0(i, j, player=k)

        # 情况相同优先攻击
        max_score = step_score.max()
        l = np.where(step_score == max_score)
        if 1 in l[2] and 0 in l[2]:
            l1 = np.where(l[2] == 1)[0]
            i = random.choice(l1)
            x = l[0][i]
            y = l[1][i]
        else:
            i = random.randint(0, len(l[0]) - 1)
            x = l[0][i]
            y = l[1][i]
        return x, y
    # 逻辑规则的落子法,
    def get_logic_score0(self, x, y, player):
        '''
        成5, 1000分
        活4、双死4、死4活3， 90分
        双活3， 80分
        死3活3， 70分
        死4， 60分
        活3， 50分
        双活2， 40分
        死3， 30分
        活2， 20分
        死2， 10分
        单子 0分
        '''
        n = player
        continues_num = [1, 1, 1, 1]  # 对应4个方向
        again_exist = [0, 0, 0, 0]  # 对应4个方向被阻拦值

        # 竖
        for j in xrange(2):
            for i in range(1, 5):
                temp = y - i if j == 0 else y + i
                # 越界或者空
                if temp < 0 or temp >= self.g_height or str(x) + "-" + str(temp) not in self.qipu:
                    break
                # 被对方挡住
                if self.qipu[str(x) + "-" + str(temp)] != n:
                    again_exist[0] += 1
                    break
                continues_num[0] += 1
        # 横
        for j in xrange(2):
            for i in range(1, 5):
                temp = x - i if j == 0 else x + i
                if temp < 0 or temp >= self.g_width or str(temp) + "-" + str(y) not in self.qipu: break
                if self.qipu[str(temp) + "-" + str(y)] != n:
                    again_exist[1] += 1
                    break
                continues_num[1] += 1

        # 左斜
        for j in xrange(2):
            for i in range(1, 5):
                temp1 = x - i if j == 0 else x + i
                temp2 = y - i if j == 0 else y + i
                if temp1 < 0 or temp1 >= self.g_width or temp2 < 0 or temp2 >= self.g_height or str(temp1) + "-" + str(
                        temp2) not in self.qipu: break
                if self.qipu[str(temp1) + "-" + str(temp2)] != n:
                    again_exist[2] += 1
                    break
                continues_num[2] += 1

        # 右斜
        for j in xrange(2):
            for i in range(1, 5):
                temp1 = x + i if j == 0 else x - i
                temp2 = y - i if j == 0 else y + i
                if temp1 < 0 or temp1 >= self.g_width or temp2 < 0 or temp2 >= self.g_height or str(temp1) + "-" + str(
                        temp2) not in self.qipu: break
                if self.qipu[str(temp1) + "-" + str(temp2)] != n:
                    again_exist[2] += 1
                    break
                continues_num[3] += 1

        print continues_num, again_exist
        # 评分系统
        continues_num_sort = copy.deepcopy(continues_num)
        if max(continues_num) >= 5:
            return 7  # 成5
        elif max(continues_num) == 4 and again_exist[continues_num.index(4)] == 0:
            return 6  # 活四
        elif continues_num_sort[-2] >= 3:
            return 5  # 双三
        elif max(continues_num) == 4:
            return 4  # 有四
        elif max(continues_num) == 3:
            return 3
        elif max(continues_num) == 2:
            return 2
        elif max(continues_num) == 1:
            return 1

    # 走n步探索
    def _get_score(self,x,y,n):
        qipu_predict = copy.deepcopy(self.qipu)

        return 1

    # 下一步最优落子点
    def best_step_n(self,n):
        if self.step == 0:
            return self.g_width / 2, self.g_height / 2

        best_x,best_y = 0,0
        best_score = -1
        for i in range(self.g_width):
            for j in range(self.g_height):
                if str(i) + "-" + str(j) not in self.qipu:
                    if self.get_logic_score(i, j, player=self.now) > 0:
                        if self._get_score(i,j,n) > best_score:
                            best_x,best_y=i,j

        return best_x,best_y
    def best_step(self):
        if self.step == 0:
            return self.g_width / 2, self.g_height / 2

        step_score = np.zeros((self.g_width, self.g_height, 2))
        step_score[:,:,:] = -99
        for i in range(self.g_width):
            for j in range(self.g_height):
                for k in range(2):
                    if str(i) + "-" + str(j) not in self.qipu:
                        step_score[i, j, k] = self.get_logic_score(i, j, player=k)

        # 情况相同优先攻击
        if self.now == 1:
            enemy = 0
        else:
            enemy = 1
        max_score_now = step_score[:,:,self.now].max()
        max_score_enemy = step_score[:,:,enemy].max()

        if max_score_enemy > 95:
            if max_score_now >= max_score_enemy:
                l = np.where(step_score[:,:,self.now] == max_score_now)
                print "进攻,我方分数%d,敌方分数%d"%(max_score_now,max_score_enemy)
            else:
                l = np.where(step_score[:,:,enemy] == max_score_enemy)
                print "防守,我方分数%d,敌方分数%d" % (max_score_now, max_score_enemy)
        elif max_score_now < 0:
            l = np.where(step_score[:, :, enemy] == max_score_enemy)
            print "防守,我方分数%d,敌方分数%d" % (max_score_now, max_score_enemy)
        else:
            print "进攻,我方分数%d,敌方分数%d" % (max_score_now, max_score_enemy)
            l = np.where(step_score[:,:,self.now] == max_score_now)

        print l
        i = random.randint(0, len(l[0]) - 1)
        x = l[0][i]
        y = l[1][i]
        print x,y
        return x, y

    # 逻辑规则的落子法,每次该点黑子和白字的各自分数
    def get_logic_score(self, x, y, player):
        '''
        成5, 1000分
        活4、双死4、死4活3， 90分
        双活3， 80分
        死3活3， 70分
        死4， 60分
        活3， 50分
        双活2， 40分
        死3， 30分
        活2， 20分
        死2， 10分
        单子 0分
        '''
        n = player
        state_array = np.zeros((4, 5))  # 4个方向，5个状态值，连续长度，两边的被封距离，被封总距离，之后被连接的可能
        state_array[:, 0] = 1

        # 竖
        stop1, stop2 = 0, 0
        outter1, outter2 = 0, 0
        connect_flag = 0
        for j in xrange(2):
            continue_flag = True
            connect_flag = 0  # 判断可连接性：空了又接上
            for i in range(1, 5):
                temp = y - i if j == 0 else y + i
                # 越界
                if temp < 0 or temp >= self.g_height:
                    if j == 0:
                        stop1 = -i
                    else:
                        stop2 = i
                    break
                elif str(x) + "-" + str(temp) not in self.qipu:
                    continue_flag = False  # 空但要继续走看阻挡
                # 被对方挡住
                elif self.qipu[str(x) + "-" + str(temp)] != n:
                    connect_flag = -1
                    if j == 0:
                        stop1 = -i
                    else:
                        stop2 = i
                    break
                elif continue_flag:  # 未打断
                    if j == 0:
                        outter1 = -i
                    else:
                        outter2 = i
                    if continue_flag == True:  # 连续计数
                        state_array[0, 0] += 1
                    else:
                        continue_flag = 1  # 可连接倾向
        if stop1 == 0:
            state_array[0, 1] = 99 #99表示没有阻挡
        else:
            state_array[0, 1] = abs(outter1 - stop1 )- 1
        if stop2 == 0:
            state_array[0, 2] = 99
        else:
            state_array[0, 2] = abs(outter2 - stop2 )- 1
        if stop1 == 0 or stop2 == 0 or abs(stop1 - stop2) - 1 >= 5:
            state_array[0, 3] = 1
        else:
            state_array[0, 3] = 0  # 无用子
        state_array[0, 4] = connect_flag

        # 横
        stop1, stop2 = 0, 0
        outter1, outter2 = 0, 0
        connect_flag = 0
        for j in xrange(2):
            continue_flag = True
            connect_flag = 0  # 判断可连接性：空了又接上
            for i in range(1, 5):
                temp = x - i if j == 0 else x + i
                # 越界
                if temp < 0 or temp >= self.g_width:
                    if j == 0:
                        stop1 = -i
                    else:
                        stop2 = i
                    break
                elif str(temp) + "-" + str(y) not in self.qipu:
                    continue_flag = False  # 空但要继续走看阻挡
                # 被对方挡住
                elif self.qipu[str(temp) + "-" + str(y)] != n:
                    connect_flag = -1
                    if j == 0:
                        stop1 = -i
                    else:
                        stop2 = i
                    break
                elif continue_flag:  # 未打断
                    if j == 0:
                        outter1 = -i
                    else:
                        outter2 = i
                    if continue_flag == True:  # 连续计数
                        state_array[1, 0] += 1
                    else:
                        continue_flag = 1  # 可连接倾向
        if stop1 == 0:
            state_array[1, 1] = 99 #99表示没有阻挡
        else:
            state_array[1, 1] = abs(outter1 - stop1 )- 1
        if stop2 == 0:
            state_array[1, 2] = 99
        else:
            state_array[1, 2] = abs(outter2 - stop2 )- 1
        if stop1 == 0 or stop2 == 0 or abs(stop1 - stop2) - 1 >= 5:
            state_array[1, 3] = 1
        else:
            state_array[1, 3] = 0  # 无用子
        state_array[1, 4] = connect_flag

        # 右斜
        stop1, stop2 = 0, 0
        outter1, outter2 = 0, 0
        connect_flag = 0
        for j in xrange(2):
            continue_flag = True
            connect_flag = 0  # 判断可连接性：空了又接上
            for i in range(1, 5):
                temp1 = x - i if j == 0 else x + i
                temp2 = y - i if j == 0 else y + i
                # 越界
                if temp1 < 0 or temp1 >= self.g_width or temp2 < 0 or temp2 >= self.g_height:
                    if j == 0:
                        stop1 = -i
                    else:
                        stop2 = i
                    break
                elif str(temp1) + "-" + str(temp2) not in self.qipu:
                    continue_flag = False  # 空但要继续走看阻挡
                # 被对方挡住
                elif self.qipu[str(temp1) + "-" + str(temp2)] != n:
                    connect_flag = -1
                    if j == 0:
                        stop1 = -i
                    else:
                        stop2 = i
                    break
                elif continue_flag:  # 未打断
                    if j == 0:
                        outter1 = -i
                    else:
                        outter2 = i
                    if continue_flag == True:  # 连续计数
                        state_array[2, 0] += 1
                    else:
                        continue_flag = 1  # 可连接倾向
        if stop1 == 0:
            state_array[2, 1] = 99 #99表示没有阻挡
        else:
            state_array[2, 1] = abs(outter1 - stop1 )- 1
        if stop2 == 0:
            state_array[2, 2] = 99
        else:
            state_array[2, 2] = abs(outter2 - stop2 )- 1
        if stop1 == 0 or stop2 == 0 or abs(stop1 - stop2) - 1 >= 5:
            state_array[2, 3] = 1
        else:
            state_array[2, 3] = 0  # 无用子
        state_array[2, 4] = connect_flag

        # 左斜
        stop1, stop2 = 0, 0
        outter1, outter2 = 0, 0
        connect_flag = 0
        for j in xrange(2):
            continue_flag = True
            connect_flag = 0  # 判断可连接性：空了又接上
            for i in range(1, 5):
                temp1 = x + i if j == 0 else x - i
                temp2 = y - i if j == 0 else y + i
                # 越界
                if temp1 < 0 or temp1 >= self.g_width or temp2 < 0 or temp2 >= self.g_height:
                    if j == 0:
                        stop1 = -i
                    else:
                        stop2 = i
                    break
                elif str(temp1) + "-" + str(temp2) not in self.qipu:
                    continue_flag = False  # 空但要继续走看阻挡
                # 被对方挡住
                elif self.qipu[str(temp1) + "-" + str(temp2)] != n:
                    connect_flag = -1
                    if j == 0:
                        stop1 = -i
                    else:
                        stop2 = i
                    break
                elif continue_flag:  # 未打断
                    if j == 0:
                        outter1 = -i
                    else:
                        outter2 = i
                    if continue_flag == True:  # 连续计数
                        state_array[3, 0] += 1
                    else:
                        continue_flag = 1  # 可连接倾向
        if stop1 == 0:
            state_array[3, 1] = 99 #-1表示没有阻挡
        else:
            state_array[3, 1] = abs(outter1 - stop1 )- 1
        if stop2 == 0:
            state_array[3, 2] = 99
        else:
            state_array[3, 2] = abs(outter2 - stop2 )- 1
        if stop1 == 0 or stop2 == 0 or abs(stop1 - stop2) - 1 >= 5:
            state_array[3, 3] = 1
        else:
            state_array[3, 3] = 0  # 无用子
        state_array[3, 4] = connect_flag

        # 评分系统
        result = 0
        if state_array[:, 3].sum() == 0:
            result = -1  # 无用子0分
        elif state_array[:, 0].max() == 1:
            result = -2
        elif state_array[:, 0].max() > 4:
            result = 100  # 胜子高分
        elif self.judge_live4(state_array):
            result = 99
        elif self.judge_live_double3(state_array):  # 活双三
            result = SHUANGSAN
        elif self.judge_live3(state_array):
            result = 96
        elif state_array[:, 0].max() > 3:
            result = 95
        elif state_array[:, 0].max() == 3:
            result = 94
        else:  # 最大子数和子数和的平均，有3
            result = self.judge_state(state_array)
        return result

    #斜角优先
    def judge_state(self,state_array):
        continue_max = state_array[:,0].max()
        angle_sum = state_array[[2,3],0].sum()
        return continue_max + angle_sum * 2

    #判断活4
    def judge_live4(self,state_array):
        if state_array[:,0].max() == 4:
            index_list = np.where(state_array[:,0] == 4)[0]
            for index in index_list:
                if state_array[index,1] > 0 and state_array[index,2] > 0:
                    return True
        else:
            return False

    # 判断活3
    def judge_live3(self, state_array):
        if state_array[:, 0].max() == 3:
            index_list = np.where(state_array[:, 0] == 3)[0]
            for index in index_list:
                if state_array[index, 1] > 0 and state_array[index, 2] > 0:
                    return True
        else:
            return False

    #判断活双三
    def judge_live_double3(self,state_array):
        if state_array[:,0].max() ==3:
            index_list = np.where(state_array[:,0] == 4)[0]
            if len(index_list) > 1:
                for index in index_list:
                    if (state_array[index,1] < 1 and state_array[index,2] < 2) or (state_array[index,1] < 2 and state_array[index,2] < 1):
                        return False
                return True
            else:
                return False
        else:
            return False

    #训练用，非可视化
    def train_compete(self,num):
        for i in range(num):
            while self.over == -1 :
                self.auto_step(is_record=True,is_visual=False)
            self.clear_window()

    #可视化一局对局，右键激活
    def visual_input(self,is_sleep=True):
        while self.over == -1 :
            self.auto_step(is_record=True,is_visual=True)
            if is_sleep:
                time.sleep(1.5)


    #自动执行下一步，这个比较怪的接口，暂时这样吧。
    def auto_step(self,is_record=True,is_visual=True):
        # if self.now == 0:
        #     x, y = self.best_step0()
        # else:
        x, y = self.best_step()
        if x<0 or y<0 or x>=self.g_width or y>=self.g_height or str(x)+"-"+str(y) in self.qipu or self.over!=-1:return
        self.qipu[str(x)+"-"+str(y)]=self.now
        self.over=self.is_win(x,y)

        #最后落子
        if self.over != -1 and self.over != PINGJU and is_record:
            self.get_final_qipu(x,y,self.now)

        x,y=x*self.dw+self.dw/2,y*self.dw+self.dw/2
        color="white" if self.now==1 else "black"
        self.C.create_oval(x,y+self.z_height,x,y+self.z_height,width=self.dw-    self.dw/8,outline=color)
        self.C.create_text(x, y + self.z_height,text = str(self.step), fill="red")
        self.C.update()
        self.now = 0 if self.now == 1 else 1
        self.step += 1
        self.zhuangtai()

    #获取棋谱
    def get_final_qipu(self,x,y,player):
        n = player
        final_qipu = np.zeros((12,12))
        center = 6

        final_qipu[center,center] = MINE
        # 竖
        for j in xrange(2):
            for i in range(1, 5):
                temp = y - i if j == 0 else y + i
                if temp < 0 or temp >= self.g_height:final_qipu[center, center+temp-y] = ENEMY           #越界
                elif str(x) + "-" + str(temp) not in self.qipu: pass  #无子
                elif self.qipu[str(x) + "-" + str(temp)] != n:final_qipu[center, center+temp-y] = ENEMY  #对方的子
                else:final_qipu[center, center+temp-y] = MINE                                            #自己的子

        # 横
        for j in xrange(2):
            for i in range(1, 5):
                temp = x - i if j == 0 else x + i
                if temp < 0 or temp >= self.g_width:final_qipu[center+temp-x, center] = ENEMY           #越界
                elif str(temp) + "-" + str(y) not in self.qipu:pass  #无子
                elif self.qipu[str(temp) + "-" + str(y)] != n:final_qipu[center+temp-x, center] = ENEMY  #对方的子
                else:final_qipu[center+temp-x, center] = MINE

        # 左斜
        for j in xrange(2):
            for i in range(1, 5):
                temp1 = x - i if j == 0 else x + i
                temp2 = y - i if j == 0 else y + i
                if temp1 < 0 or temp1 >= self.g_width or temp2 < 0 or temp2 >= self.g_height:final_qipu[center+temp1-x, center+temp2-y] = ENEMY
                elif str(temp1) + "-" + str(temp2) not in self.qipu:pass  # 无子
                elif self.qipu[str(temp1) + "-" + str(temp2)] != n:final_qipu[center+temp1-x, center+temp2-y] = ENEMY  # 对方的子
                else:final_qipu[center+temp1-x, center+temp2-y] = MINE

        # 右斜
        for j in xrange(2):
            for i in range(1, 5):
                temp1 = x + i if j == 0 else x - i
                temp2 = y - i if j == 0 else y + i
                if temp1 < 0 or temp1 >= self.g_width or temp2 < 0 or temp2 >= self.g_height:final_qipu[center+temp1-x, center+temp2-y] = ENEMY
                elif str(temp1) + "-" + str(temp2) not in self.qipu:pass  # 无子
                elif self.qipu[str(temp1) + "-" + str(temp2)] != n:final_qipu[center+temp1-x, center+temp2-y] = ENEMY  # 对方的子
                else:final_qipu[center+temp1-x, center+temp2-y] = MINE

        with open('final_qipu.pickle', 'ab') as f:  # 此处需指定模式为写入字节流，因为pickle是将object转换为二进制字节流
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(final_qipu, f, pickle.HIGHEST_PROTOCOL)  # 采用最新的协议，扩展性较好
            print "write pickle over"
            f.close()
            print "close the pickle"
        return

    #可视化棋谱
    def show_final_qipu(self):
        with open('final_qipu.pickle', 'rb') as f:  # 读入时同样需要指定为读取字节流模式
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            final_qipu = pickle.load(f)
            for xx in range(final_qipu.shape[0]):
                for yy in range(final_qipu.shape[1]):
                    if final_qipu[xx,yy] == MINE:
                        x, y = xx * self.dw + self.dw / 2, yy * self.dw + self.dw / 2
                        self.C.create_oval(x, y + self.z_height, x, y + self.z_height, width=self.dw - self.dw / 8,
                                       outline="white")
                    elif final_qipu[xx,yy] == ENEMY:
                        x, y = xx * self.dw + self.dw / 2, yy * self.dw + self.dw / 2
                        self.C.create_oval(x, y + self.z_height, x, y + self.z_height, width=self.dw - self.dw / 8,
                                       outline="black")
                    else:
                        pass
            self.C.update()
            f.close()
            print "close the read pickle"

    def click(self,e):
        x,y=e.x/self.dw,(e.y-self.z_height)/self.dw
        if x<0 or y<0 or x>=self.g_width or y>=self.g_height or str(x)+"-"+str(y) in self.qipu or     self.over!=-1:return
        # print self.get_logic_score(x,y,self.now)
        self.qipu[str(x)+"-"+str(y)]=self.now
        self.over=self.is_win(x,y)
        x,y=x*self.dw+self.dw/2,y*self.dw+self.dw/2
        color="white" if self.now==1 else "black"
        self.C.create_oval(x,y+self.z_height,x,y+self.z_height,width=self.dw-    self.dw/8,outline=color)
        self.C.create_text(x, y + self.z_height, text=str(self.step), fill="red")
        self.now=0 if self.now==1 else 1
        self.step+=1
        self.zhuangtai()
        self.auto_step()

    #根据当前输入判断是否赢
    def is_win(self,x,y):
        #平局判断
        if  self.step > self.g_height * self.g_width - 5:
            return PINGJU

        n=self.qipu[str(x)+"-"+str(y)]
        r=1
        #竖
        for j in xrange(2):
            for i in range(1,5):
                temp=y-i if j==0 else y+i
                if temp<0 or temp>=self.g_height or str(x)+"-"+str(temp) not in self.qipu:break
                if self.qipu[str(x)+"-"+str(temp)]!=n:break
                r+=1
        if r>=5:return n


        r=1
        #横
        for j in xrange(2):
            for i in range(1,5):
                temp=x-i if j==0 else x+i
                if temp<0 or temp>=self.g_width or str(temp)+"-"+str(y) not in self.qipu:break
                if self.qipu[str(temp)+"-"+str(y)]!=n:break
                r+=1
        if r>=5:return n


        r=1
        #左斜
        for j in xrange(2):
            for i in range(1,5):
                temp1=x-i if j==0 else x+i
                temp2=y-i if j==0 else y+i
                if temp1<0 or temp1>=self.g_width or temp2<0 or temp2>=self.g_height or str(temp1)+"-"+str(temp2) not in self.qipu:break
                if self.qipu[str(temp1)+"-"+str(temp2)]!=n:break
                r+=1
        if r>=5:return n


        r=1
        #右斜
        for j in xrange(2):
            for i in range(1,5):
                temp1=x+i if j==0 else x-i
                temp2=y-i if j==0 else y+i
                if temp1<0 or temp1>=self.g_width or temp2<0 or temp2>=self.g_height or str(temp1)+"-"+str(temp2) not in self.qipu:break
                if self.qipu[str(temp1)+"-"+str(temp2)]!=n:break
                r+=1
        if r>=5:return n
        return -1 #-1表示没结束

    #



if __name__ == '__main__':
    game=GAME(30,20,20)
    #这三个数字分别代表个棋盘每个小块的长度，棋盘高多少个小块，宽多少个小块