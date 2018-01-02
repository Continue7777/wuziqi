#coding=utf-8
from Tkinter import *
import random
import time
import numpy as np
import copy

dogFall_constant = 2
outboard_constant = -1
black_constant = 0
white_constant = 1
null_constant = 2

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

    def clear_window(self):
        self.now, self.step, self.over, self.qipu = 0, 0, -1, {}
        self.qipan(True)
        self.zhuangtai()

    def key(self,e):
        if e.keycode==116 and self.over!=-1: #F5 重新开局
            self.clear_window()
        if e.keycode == 117:
            self.feature_model(2, 3)

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
            self.C.pack()

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

    def auto_step(self,is_record=True,is_visual=True):
        x, y = self.best_step0()
        if x<0 or y<0 or x>=self.g_width or y>=self.g_height or str(x)+"-"+str(y) in self.qipu or self.over!=-1:return
        self.qipu[str(x)+"-"+str(y)]=self.now
        self.over=self.is_win(x,y)
        x,y=x*self.dw+self.dw/2,y*self.dw+self.dw/2
        color="white" if self.now==1 else "black"
        self.C.create_oval(x,y+self.z_height,x,y+self.z_height,width=self.dw-    self.dw/8,outline=color)
        self.C.create_text(x, y + self.z_height,text = str(self.step), fill="red")
        self.C.update()
        self.now = 0 if self.now == 1 else 1
        self.step += 1
        self.zhuangtai()

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
        self.C.update()
        # self.auto_step()


    def step_score(self,player_name):
        if player_name == 'one_step_logic':
            return self.step_score_logic1()

    def best_step(self,player_name):
        if player_name == "noob_logic":
            return self.best_step0()
        if player_name == "one_step_logic":
            return self.best_step_logic1()

    def feature_model(self,x,y):
        """
        describe:the model for the feature extract
        :return: True/False
        """
        horizontal_state = np.zeros(9)
        vertical_state = np.zeros(9)
        leanleft_state = np.zeros(9)
        leanright_state = np.zeros(9)
        for i in range(-4,5):  #水平
            if x+i < 0 or x+i >= self.g_width: #出界
                horizontal_state[i+4] = outboard_constant
            elif str(x+i) + "-" + str(y) not in self.qipu: #空
                horizontal_state[i+4] = null_constant
            else:
                horizontal_state[i+4] = self.qipu[str(x+i) + "-" + str(y)]
        for i in range(-4,5): # 垂直
            if y+i < 0 or y+i >= self.g_height: #出界
                vertical_state[i+4] = outboard_constant
            elif str(x) + "-" + str(y+i) not in self.qipu: #空
                vertical_state[i+4] = null_constant
            else:
                vertical_state[i+4] = self.qipu[str(x) + "-" + str(y+i)]
        for i in range(-4,5): #左上-右下
            if x+i < 0 or x+i >= self.g_width or y+i < 0 or y+i >= self.g_height: #出界
                leanleft_state[i+4] = outboard_constant
            elif str(x+i) + "-" + str(y+i) not in self.qipu: #空
                leanleft_state[i+4] = null_constant
            else:
                leanleft_state[i+4] = self.qipu[str(x+i) + "-" + str(y+i)]
        for i in range(-4,5): #左下-右上
            if x+i < 0 or x+i >= self.g_width or y-i < 0 or y-i >= self.g_height: #出界
                leanright_state[i+4] = outboard_constant
            elif str(x+i) + "-" + str(y-i) not in self.qipu: #空
                leanright_state[i+4] = null_constant
            else:
                leanright_state[i+4] = self.qipu[str(x+i) + "-" + str(y-i)]



        return False

    def step_score_logic1(self):
        """
        describe:  get score for each point
        :return:shape(w,h) narray
        """

    def best_step_logic1(self):
        """

        :return:
        """

    def best_step0(self):
        if self.step == 0:
            return self.g_width / 2, self.g_height / 2

        step_score = np.zeros((self.g_width, self.g_height, 2))
        for i in range(self.g_width):
            for j in range(self.g_height):
                for k in range(2):
                    if str(i) + "-" + str(j) not in self.qipu:
                        step_score[i, j, k] = self.step_score_logic0(i, j, player=k)

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

    def step_score_logic0(self, x, y, player):
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

    def is_win(self,x,y):
        #平局判断
        if  self.step > self.g_height * self.g_width - 5:
            return dogFall_constant

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




if __name__ == '__main__':
    game=GAME(30,20,20)
    #这三个数字分别代表个棋盘每个小块的长度，棋盘高多少个小块，宽多少个小块