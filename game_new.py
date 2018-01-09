#coding=utf-8
from Tkinter import *
import random
import time
import numpy as np
import copy

dogFall_constant = 999
outboard_constant = -1
black_constant = 0
white_constant = 1
null_constant = 2
not_available_constant = -1000

class GAME():#游戏类
    z_height=30
    now,step,over,qipu,qipu_predict=0,0,-1,{},{}
    C,Z=0,0
    black_score = 0
    white_score = 0
    def __init__(self,dw,g_height,g_width,evalution_flag = False):
        self.dw,self.g_height,self.g_width=dw,g_height,g_width
        if evalution_flag == False:
            self.height, self.width = self.g_height * self.dw + self.z_height, self.g_width * self.dw
            self.window = Tk()
            self.window.title(u'五子棋')
            self.center_window()
            self.window.bind('<Key>', self.key)
            self.qipan()
            self.zhuangtai()
            self.window.mainloop()
        else:
            result_dict = self.evalution(["noob_logic","one_step_logic","max_min_search"], num =5)
            for key in result_dict:
                print key,result_dict[key]

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
            self.C.bind("<Button-3>",self.one_game_visul)
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

    def one_game_visul(self,e):
        player_name1 = "one_step_logic"
        player_name2 = "one_step_logic"
        player_name = player_name1
        while self.over == -1 :
            self.auto_one_visual(player_name=player_name)
            player_name = player_name1 if player_name == player_name2 else player_name2
            time.sleep(0.5)

    def auto_one_visual(self,player_name):
        x, y = self.best_step(player_name=player_name)
        if x<0 or y<0 or x>=self.g_width or y>=self.g_height or str(x)+"-"+str(y) in self.qipu or self.over!=-1:return
        self.qipu[str(x)+"-"+str(y)]=self.now
        self.over=self.is_win(x,y)
        # print self.get_features_score(x, y, self.qipu)
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
        self.qipu[str(x)+"-"+str(y)]=self.now
        self.over=self.is_win(x,y)
        # print self.get_features_score(x, y, self.qipu)
        x,y=x*self.dw+self.dw/2,y*self.dw+self.dw/2
        color="white" if self.now==1 else "black"
        self.C.create_oval(x,y+self.z_height,x,y+self.z_height,width=self.dw-    self.dw/8,outline=color)
        self.C.create_text(x, y + self.z_height, text=str(self.step), fill="red")
        self.now=0 if self.now==1 else 1
        self.step+=1
        self.zhuangtai()
        self.C.update()
        start = time.time()
        self.auto_one_visual(player_name="max_min_search")
        print time.time()-start

    def one_game_evalution(self,player1,player2):
        """
        :param player1:
        :param player2:
        :return: 0 player1 win ,1 player2 win ,0 dogfall
        """
        player = player1
        count = 0
        while self.over == -1:
            count += 1
            x,y = self.best_step(player_name=player)
            self.qipu[str(x) + "-" + str(y)] = self.now
            self.over = self.is_win(x, y)
            if self.over == dogFall_constant:
                return dogFall_constant
            self.now = 0 if self.now == 1 else 1
            self.step += 1
            player = player1 if player == player2 else player2
        #clear
        self.now, self.step, self.over, self.qipu = 0, 0, -1, {}

        print count
        if player == player1:
            return 1
        else:
            return 0

    def evalution(self,player_name_list, num):
        """
        without
        :param num:
        :return:
        """
        result_dict = {}
        for player1 in player_name_list:
            for player2 in player_name_list:
                if player1 != player2:
                    player1_win = 0
                    player2_win = 0
                    dog_win = 0
                    for i in range(num):
                        start = time.time()
                        t = self.one_game_evalution(player1=player1,player2=player2)
                        print "%s-%s result:%d  time:%f"%(player1,player2,t,time.time()-start)
                        if t == 0:
                            player1_win += 1
                        elif t == 1:
                            player2_win += 1
                        else:
                            dog_win += 1
                    result_dict[str(player1) + "-" + str(player2)] = str(player1_win) + " _ " + str(player2_win) + " _ " + str(dog_win)
        return result_dict

    def step_score(self,player_name):
        if player_name == "one_step_logic":
            return self.step_score_logic1(qipu=self.qipu)
        elif player_name == "mcts":
            return self.step_score_mcts(qipu=self.qipu)

    def best_step(self,player_name):
        if self.step == 0:
            return self.g_width / 2 -1 , self.g_height / 2 -1

        if player_name == "noob_logic":
            return self.best_step0()
        elif player_name == "one_step_logic":
            return self.best_step_logic1(qipu=self.qipu)
        elif player_name == "max_min_search":
            return self.best_step_maxmin_search(qipu=self.qipu,n=3)
        elif player_name == "mcts":
            return self.best_step_mcts(qipu=self.qipu)
        else:#不存在
            return None
    #—————————————value function—————————————————#
    def get_4direction_states(self,x,y,qipu):
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
            elif str(x+i) + "-" + str(y) not in qipu: #空
                horizontal_state[i+4] = null_constant
            else:
                horizontal_state[i+4] = qipu[str(x+i) + "-" + str(y)]
        for i in range(-4,5): # 垂直
            if y+i < 0 or y+i >= self.g_height: #出界
                vertical_state[i+4] = outboard_constant
            elif str(x) + "-" + str(y+i) not in qipu: #空
                vertical_state[i+4] = null_constant
            else:
                vertical_state[i+4] = qipu[str(x) + "-" + str(y+i)]
        for i in range(-4,5): #左上-右下
            if x+i < 0 or x+i >= self.g_width or y+i < 0 or y+i >= self.g_height: #出界
                leanleft_state[i+4] = outboard_constant
            elif str(x+i) + "-" + str(y+i) not in qipu: #空
                leanleft_state[i+4] = null_constant
            else:
                leanleft_state[i+4] = qipu[str(x+i) + "-" + str(y+i)]
        for i in range(-4,5): #左下-右上
            if x+i < 0 or x+i >= self.g_width or y-i < 0 or y-i >= self.g_height: #出界
                leanright_state[i+4] = outboard_constant
            elif str(x+i) + "-" + str(y-i) not in qipu: #空
                leanright_state[i+4] = null_constant
            else:
                leanright_state[i+4] = qipu[str(x+i) + "-" + str(y-i)]

        result = [horizontal_state,vertical_state,leanleft_state,leanright_state]
        return result

    def feature_model(self,x,y):
        """
        direciton_states_list = self.get_4direction_states(x,y)
        for one_direciton_state in direciton_states_list:
            if feature_one_direction_model(one_direciton_state):
                return True
        return False
        """
        pass

    def _win5(self,state,player):
        """
        describe:get True or False form one direciton
        :param player:
        :param state: the size of 9 state array in one direction
        :return:
        """
        count = 1
        for i in range(1,5):
            if state[4+i] == player:
                count += 1
            else:
                break
        for i in range(1,5):
            if state[4-i] == player:
                count += 1
            else:
                break
        if count >= 5:
            return True
        else:
            return False

    def _live4(self,state,player):
        """
        describe:get True or False form one direciton
        :param player:
        :param state: the size of 9 state array in one direction
        :return:
        """
        enemy = 0 if player == 1 else 1
        count = 1
        stop_flag = False
        for i in range(1,5):
            if state[4+i] == player:
                count += 1
            else:
                if state[4+i] == enemy or state[4+i] == outboard_constant:
                    stop_flag = True
                break
        for j in range(1,5):
            if state[4-j] == player:
                count += 1
            else:
                if state[4-j] == enemy or state[4-j] == outboard_constant:
                    stop_flag = True
                break
        if count == 4 and stop_flag == False:
            return True
        else:
            return False

    def _free4(self,state,player):
        """
        describe:one side or two side available 4
        :param player:
        :param state: the size of 9 state array in one direction
        :return:
        """
        enemy = 0 if player == 1 else 1
        count = 1
        stop_flag1 = False
        stop_flag2 = False
        for i in range(1,5):
            if state[4+i] == player:
                count += 1
            else:
                if state[4+i] == enemy or state[4+i] == outboard_constant:
                    stop_flag1 = True
                break
        for j in range(1,5):
            if state[4-j] == player:
                count += 1
            else:
                if state[4-j] == enemy or state[4-j] == outboard_constant:
                    stop_flag2 = True
                break

        stop_flag = stop_flag1 and stop_flag2
        if count == 4 and stop_flag == False:
            return True
        else:
            return False

    def _live3(self,state,player):
        """
        describe:get True or False form one direciton
        :param player:
        :param state: the size of 9 state array in one direction
        :return:
        """
        enemy = 0 if player == 1 else 1
        count = 1
        stop_flag = False
        for i in range(1,5):
            if state[4+i] == player:
                count += 1
            else:
                if state[4+i] == enemy or state[4+i] == outboard_constant:
                    stop_flag = True
                break
        for j in range(1,5):
            if state[4-j] == player:
                count += 1
            else:
                if state[4-j] == enemy or state[4-j] == outboard_constant:
                    stop_flag = True
                break
        if count == 3 and stop_flag == False:
            return True
        else:
            return False

    def _free3(self,state,player):
        """
        describe:one side or two side available 4
        :param player:
        :param state: the size of 9 state array in one direction
        :return:
        """
        enemy = 0 if player == 1 else 1
        count = 1
        stop_flag1 = False
        stop_flag2 = False
        for i in range(1,5):
            if state[4+i] == player:
                count += 1
            else:
                if state[4+i] == enemy or state[4+i] == outboard_constant:
                    stop_flag1 = True
                break
        for j in range(1,5):
            if state[4-j] == player:
                count += 1
            else:
                if state[4-j] == enemy or state[4-j] == outboard_constant:
                    stop_flag2 = True
                break

        stop_flag = stop_flag1 and stop_flag2
        if count == 3 and stop_flag == False:
            return True
        else:
            return False

    def _live2(self,state,player):
        """
        describe:get True or False form one direciton
        :param player:
        :param state: the size of 9 state array in one direction
        :return:
        """
        enemy = 0 if player == 1 else 1
        count = 1
        stop_flag = False
        for i in range(1,5):
            if state[4+i] == player:
                count += 1
            else:
                if state[4+i] == enemy or state[4+i] == outboard_constant:
                    stop_flag = True
                break
        for j in range(1,5):
            if state[4-j] == player:
                count += 1
            else:
                if state[4-j] == enemy or state[4-j] == outboard_constant:
                    stop_flag = True
                break
        if count == 2 and stop_flag == False:
            return True
        else:
            return False

    def _free2(self,state,player):
        """
        describe:one side or two side available 2
        :param player:
        :param state: the size of 9 state array in one direction
        :return:
        """
        enemy = 0 if player == 1 else 1
        count = 1
        stop_flag1 = False
        stop_flag2 = False
        for i in range(1,5):
            if state[4+i] == player:
                count += 1
            else:
                if state[4+i] == enemy or state[4+i] == outboard_constant:
                    stop_flag1 = True
                break
        for j in range(1,5):
            if state[4-j] == player:
                count += 1
            else:
                if state[4-j] == enemy or state[4-j] == outboard_constant:
                    stop_flag2 = True
                break

        stop_flag = stop_flag1 and stop_flag2
        if count == 2 and stop_flag == False:
            return True
        else:
            return False

    def _die_state(self,state):
        """
        describe:get True or False form one direciton
        :param player:
        :param state: the size of 9 state array in one direction
        :return:
        """
        enemy = 0 if self.now == 1 else 1
        count = 1

        for i in range(1,5):
            if state[4+i] != enemy and state[4+i] != outboard_constant:
                count += 1
            else:
                break
        for j in range(1,5):
            if state[4-j] == enemy or state[4-j] == outboard_constant:
                count += 1
            else:
                break

        if count < 5:
            return True
        else:
            return False

    def _available2(self,state):
        """
        describe:find the available state
        :param state:
        :return:
        """
        for i in range(-2,3):
            if state[4+i] == 0 or state[4+i] == 1 and i != 0:
                return True
        return False

    def _available1(self,state):
        """
        describe:find the available state
        :param state:
        :return:
        """
        for i in range(-1,2):
            if (state[4+i] == 0 or state[4+i] == 1) and i != 0:
                return True
        return False

    def win5(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._win5(one_direciton_state,player=self.now):
                return True
        return False

    def against_win5(self,x,y,qipu):
        enemy = 0 if self.now == 1 else 1
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._win5(one_direciton_state,player=enemy):
                return True
        return False

    def live4(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._live4(one_direciton_state,player=self.now):
                return True
        return False

    def free4(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._free4(one_direciton_state,player=self.now):
                return True
        return False

    def against_live4(self,x,y,qipu):
        enemy = 0 if self.now == 1 else 1
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._live4(one_direciton_state,player=enemy):
                return True
        return False

    def live3(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._live3(one_direciton_state,player=self.now):
                return True
        return False

    def free3(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._free3(one_direciton_state,player=self.now):
                return True
        return False

    def double3(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        count = 0
        for one_direciton_state in direciton_states_list:
            if self._live3(one_direciton_state,player=self.now):
                count += 1
        if count > 1:
            return True
        else:
            return False

    def double34(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        count1 = 0
        count2 = 0
        for one_direciton_state in direciton_states_list:
            if self._live3(one_direciton_state,player=self.now):
                count1 += 1
            if self._free4(one_direciton_state,player=self.now):
                count2 += 1
        count = count1 + count2
        if count > 1:
            return True
        else:
            return False

    def against_double34(self,x,y,qipu):
        enemy = 0 if self.now == 1 else 1
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        count1 = 0
        count2 = 0
        for one_direciton_state in direciton_states_list:
            if self._live3(one_direciton_state,player=self.now):
                count1 += 1
            if self._free4(one_direciton_state,player=self.now):
                count2 += 1
        count = count1 + count2
        if count > 1:
            return True
        else:
            return False

    def against_double3(self,x,y,qipu):
        enemy = 0 if self.now == 1 else 1
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        count = 0
        for one_direciton_state in direciton_states_list:
            if self._live3(one_direciton_state,player=enemy):
                count += 1
        if count > 1:
            return True
        else:
            return False

    def against_live3(self,x,y,qipu):
        enemy = 0 if self.now == 1 else 1
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._live3(one_direciton_state,player=enemy):
                return True
        return False

    def die_state(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._die_state(one_direciton_state) == False:
                return False
        return True

    def angle_live(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        count = 0
        for one_direciton_state in direciton_states_list:
            if self._live2(one_direciton_state,player=self.now):
                count += 1
        if count > 1:
            return True
        else:
            return False

    def angle_free(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        count = 0
        for one_direciton_state in direciton_states_list:
            if self._free2(one_direciton_state,player=self.now):
                count += 1
        if count > 1:
            return True
        else:
            return False

    def lean_live2(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        leanleft_state = direciton_states_list[2]
        leanright_state = direciton_states_list[3]
        if leanright_state[3] == self.now and leanright_state[2] == null_constant and leanright_state[5] ==null_constant:
            return True
        elif leanright_state[5] == self.now and leanright_state[2] == null_constant and leanright_state[3] ==null_constant:
            return True
        elif leanleft_state[3] == self.now and leanleft_state[2] == null_constant and leanleft_state[5] ==null_constant:
            return True
        elif leanleft_state[5] == self.now and leanleft_state[2] == null_constant and leanleft_state[3] ==null_constant:
            return True
        else:
            return False

    def flat_live2(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        horizontal_state= direciton_states_list[0]
        vertical_state = direciton_states_list[1]
        if horizontal_state[3] == self.now and horizontal_state[2] == null_constant and horizontal_state[5] ==null_constant:
            return True
        elif horizontal_state[5] == self.now and horizontal_state[2] == null_constant and horizontal_state[3] ==null_constant:
            return True
        elif vertical_state[3] == self.now and vertical_state[2] == null_constant and vertical_state[5] ==null_constant:
            return True
        elif vertical_state[5] == self.now and vertical_state[2] == null_constant and vertical_state[3] ==null_constant:
            return True
        else:
            return False

    def available2(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._available2(one_direciton_state):
                return True
        return False

    def available1(self,x,y,qipu):
        direciton_states_list = self.get_4direction_states(x,y,qipu)
        for one_direciton_state in direciton_states_list:
            if self._available1(one_direciton_state):
                return True
        return False

    def get_features_score(self,x, y, qipu):
        if self.win5(x,y,qipu):
            score = 100
        elif self.against_win5(x,y,qipu):
            score = -99
        elif self.live4(x,y,qipu):
            score = 98
        elif self.double34(x,y,qipu):
            score = 97
        elif self.against_live4(x,y,qipu):
            score = -96
        elif self.against_double34(x,y,qipu):
            score = -95
        elif self.double3(x,y,qipu):
            score = 94
        elif self.against_double3(x,y,qipu):
            score = -93
        elif self.live3(x,y,qipu):
            score = 92
        elif self.die_state(x,y,qipu):
            score = -2
        elif self.angle_live(x,y,qipu):
            score = 89
        elif self.free3(x,y,qipu):
            score = 88
        elif self.angle_free(x,y,qipu):
            score = 86
        elif self.against_live3(x,y,qipu):
            score = -85
        elif self.lean_live2(x,y,qipu):
            score = 84
        elif self.flat_live2(x,y,qipu):
            score = 83
        elif self.free4(x,y,qipu):
            score = 82
        elif self.available1(x,y,qipu):
            score = 80
        else:
            score = 0

        return score
    #——————————value function end——————————————————#
    def step_score_logic1(self,qipu):
        """
        describe:  get score for each point
        :return:shape(w,h) narray
        """
        score_array = np.zeros((self.g_width,self.g_height))
        score_array[:,:] = not_available_constant
        for x in range(self.g_width):
            for y in range(self.g_height):
                if self.available2(x,y,qipu) and str(x) + "-" + str(y) not in qipu:
                    score_array[x,y] = abs(self.get_features_score(x,y,qipu))
        return score_array

    def best_step_logic1(self,qipu):
        score_array = self.step_score_logic1(qipu=qipu)
        index_tuple = np.where(score_array == np.max(score_array))
        i = random.randint(0,len(index_tuple[0])-1)
        x = index_tuple[0][i]
        y = index_tuple[1][i]
        return x,y

    def get_features_score_n(self,x,y,n,qipu):
        """
        get the n step score with best_step_logic1
        :param x:
        :param y:
        :param qipu:
        :return:score/depth/maxnum  +means win -means lose
        """
        qipu_predict = copy.deepcopy(qipu)
        now_status = self.now
        for i in range(n):
            qipu_predict[str(x) + "-" + str(y)] = self.now
            my_score = self.get_features_score(x, y,qipu=qipu_predict)
            if my_score >= 100:
                self.now = now_status
                return 100,i+1,0
            self.now = 0 if self.now == 1 else 1
            print "my_temp (%d,%d) score = %d"%(x,y,my_score)
            enemy_x,enemy_y = self.best_step_logic1(qipu=qipu_predict)
            qipu_predict[str(enemy_x) + "-" + str(enemy_y)] = self.now
            enemy_score = self.get_features_score(enemy_x, enemy_y,qipu=qipu_predict)
            self.now = 0 if self.now == 1 else 1
            print "enemy_temp (%d,%d) score = %d" % (enemy_x, enemy_y, enemy_score)
            if enemy_score >= 100:
                self.now = now_status
                return -100,i+1,0
            x,y = self.best_step_logic1(qipu=qipu_predict)

        my_score_array = self.step_score_logic1(qipu=qipu_predict)
        max_num = len(np.where(my_score_array == np.max(my_score_array))[0])
        print my_score,enemy_score
        if my_score >= enemy_score: # 表示我优势大
            self.now = now_status
            return max(abs(my_score),abs(enemy_score)),n,max_num
        else: #对方优势大
            self.now = now_status
            return -max(abs(my_score),abs(enemy_score)),n,max_num  # 1表示敌方优势大

    def _step_score_maxmin_search(self,qipu,n):
        """

        :param qipu:
        :return:
        """
        score_array = np.zeros((self.g_width,self.g_height))
        score_array[:,:] = not_available_constant
        depth_array = np.zeros((self.g_width, self.g_height))
        max_num_array = np.zeros((self.g_width, self.g_height))
        count = 0
        for x in range(self.g_width):
            for y in range(self.g_height):
                if self.available1(x,y,qipu) and str(x) + "-" + str(y) not in qipu:
                    score,depth,max_num = self.get_features_score_n(x,y,n=n,qipu=qipu)
                    print "(%d,%d)score %d , depth %d , max_num %d"%(x,y,score,depth,max_num)
                    score_array[x,y] = score
                    depth_array[x,y] = depth
                    max_num_array[x,y] = max_num
                    count += 1
        # print "count %d"%count

        return score_array,depth_array,max_num_array

    def step_score_maxmin_search(self, qipu,n):
        score_array = np.zeros((self.g_width, self.g_height))
        score_array[:, :] = not_available_constant
        for x in range(self.g_width):
            for y in range(self.g_height):
                if self.available2(x, y, qipu) and str(x) + "-" + str(y) not in qipu:
                    score, depth, max_num = self.get_features_score_n(x, y, n=n,qipu=qipu)
                    score_array[x, y] = score
        return score_array

    def best_step_maxmin_search(self,qipu,n):
        """
        分数优先级>深度（正最大，负最小）>最后层max/min个数(正max,负min)>random
        :param qipu:
        :return:
        """
        score_array,depth_array,max_num_array = self._step_score_maxmin_search(qipu=qipu,n=n)
        print "step :" + str(self.step)
        index_tuple = np.where(score_array == np.max(score_array))
        if np.max(score_array) == 100: #最近取胜
            min_depth = np.min(depth_array[score_array == np.max(score_array)])
            mark = (depth_array == min_depth) & (score_array == np.max(score_array))
            index_tuple = np.where(mark)
        elif np.max(score_array) == -100:  # 最近取胜
            max_depth = np.max(depth_array[score_array == -100])
            mark = (depth_array == max_depth) & (score_array == -100)
            index_tuple = np.where(mark)
        elif np.max(score_array) < 0: #劣势情况下，最小化劣势
            min_num = np.min(max_num_array[score_array == np.max(score_array)])
            mark = (max_num_array == min_num) & (score_array == np.max(score_array))
            index_tuple = np.where(mark)
        elif np.max(score_array) > 0: #大于1时
            max_num = np.max(max_num_array[score_array == np.max(score_array)])
            mark = (max_num_array == max_num) & (score_array == np.max(score_array))
            index_tuple = np.where(mark)
        i = random.randint(0, len(index_tuple[0]) - 1)
        x = index_tuple[0][i]
        y = index_tuple[1][i]
        return x,y

    # def step_score_mcts(self, qipu ,itermax):
    #     """ Conduct a UCT search for itermax iterations starting from rootstate.
    #         Return the best move from the rootstate.
    #         Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""
    #
    #     untried_moves = []
    #     child_nodes = []
    #
    #     for i in range(itermax):
    #         # Select
    #         while untried_moves == [] and child_nodes != []:  # node is fully expanded and non-terminal
    #             node = node.UCTSelectChild()
    #             state.DoMove(node.move)
    #
    #         # Expand
    #         if node.untriedMoves != []:  # if we can expand (i.e. state/node is non-terminal)
    #             m = random.choice(node.untriedMoves)
    #             state.DoMove(m)
    #             node = node.AddChild(m, state)  # add child and descend tree
    #
    #         # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
    #         while state.GetMoves() != []:  # while state is non-terminal
    #             state.DoMove(random.choice(state.GetMoves()))
    #
    #         # Backpropagate
    #         while node != None:  # backpropagate from the expanded node and work back to the root node
    #             node.Update(state.GetResult(
    #                 node.playerJustMoved))  # state is terminal. Update node with result from POV of node.playerJustMoved
    #             node = node.parentNode
    #
    #     # Output some information about the tree - can be omitted
    #     if (verbose):
    #         print rootnode.TreeToString(0)
    #     else:
    #         print rootnode.ChildrenToString()
    #
    #     return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited


    def best_step_mcts(self,qipu):
        pass

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

        # print continues_num, again_exist
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