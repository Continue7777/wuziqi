[TOC]

# 五子棋AI实现



## 里程碑

+ 2018.1.3 - 给出不含神经网络评估的需求函数，重点：代码重构、性能考虑、评估考虑、搜索树max-min/mcts、最佳逻辑的完善、测试方案、输出报告，给出一份详细可操作可评审的报告。设计思路中考虑面向对象的思路。
+ 2018.1.7 - 完成编码、调试、测试、总结工作
+ 2018.1.12 - 完成rl和cnn模块的试水探索
+ 2018.1.14 - 完成包含rl和cnn模块的需求整理、代码重构、性能考虑、评估考虑、测试方案、输出报告
+ 2018.1.21 - 完成rl和cnn的编码工作并发现新问题
+ 2018.1.28 - 总结、博客整个工程。



## 需求

### 场景逻辑

+ 单步对弈 one_step
+ 可视化单局对弈 one_game_visual
+ 评估 evalution
+ 细节评估 类似一个开关，打开后可以看到后续的选择思路
+ 把下棋的思路抽象成一个player的类，先抽出来吧。

### 性能需求

+ 需要一个服务器来跑，考虑如果高效的使用服务器资源以及结合本地展示。
+ 需要把控每个模块的大致时间

### 模块需求

+ 动态的选择搜索树


+ mcts和max-min搜索的两部分对比设计
+ 基于神经网络的设计实现
+ 评估报表
+ 基于神经网络的评估数据

### 算法需求

+ 搜索树模块：max-min,mcts
+ 策略选择模块：base_line_logic / better_logic / value_net(cnn)


### 详细文档

#### 耗时->1.5h

#### 变量说明

state:整个棋盘的状态，目前为原始图

self.qipu():本局的棋谱状态

qipan_width,qipan_height: 棋盘的宽和高

#### 整体函数

#### def step_score(state,player_name)：(统一接口,充当配置函数的功能,所有场景下都过这个函数配置，不能直接调用之后的函数)

​	input -> state 输入当前状态函数 

​	内部配置mode  ->   'single'单步、’max-min‘最大最小树、'mcts'蒙特卡洛搜索

​	output -> narray 每个可能状态的得分值，合法的地方为正分数，其余为-1 （确保分数算出来没负的）

#### def best_step(state,player_name) :  (统一接口)  

​	relation -> step_score(state) : 调用整个评估，max就ok.

​	input ->state  输入当前状态函数

​		  -> player_name 为某个策略的算法命名

​	output -> (x,y )输出当前决策下最优的动作的坐标tuple

​	thoughts -> 仍然是每个算法对应一个函数，然后统一封装接口对外调用，这样在evalution中就可以使用名字来调用函数了，简化评估函数中逻辑。

#### def evalution(player_name_list,num)：

​	relation -> best_step(state,player_name)

​	input  -> player( ['name1','name2'] ) 

​		    -> num 互博次数

​	output -> result_dict['1-2'] = "10:5" ,这个看后续的处理，暂时只有看结果的需求

#### def one_step(state,player_name):

​	output	->  best_step(state,player_name) ,调用一步函数，返回，单纯的意义封装。

#### def one_game_visual(player_name1,player_name2):

​	relation ->  best_step(state,player_name)

### 特征提取与评估

#### def feature_model(x,y): 

​	//评判函数模板，除双3，活3/4以外都有用。

​	4个方向分别表示出来，然后0表示黑旗，1表示白旗，2表示空，-1表示边界，以下所有的条件判断都需要额外考虑边界情况。

​	for one_direciton_state one_direciton_states_list:

​		if feature_one_direction_model(one_direciton_state):

​			return True

​	return False

#### def win5(x,y) #胜5

#### def against_win5(x,y) #防守对方胜5

#### def live4(x,y) #活4

#### def against_live4(x,y) #防守对方活4

#### def live3(x,y) #活三

#### def against_live3(x,y) # 防守对方活三

#### def die_state(x,y)  #4方向不可能赢，被封死的点

#### def only1(x,y) #孤点

​	需求 -> 方圆2个没点，1个距离孤点也考虑进来

​	relation -> feature_model

​	input -> x,y

​	output -> True/False

#### def double3(x,y) #活双三

#### def against_double3(x,y) #防守对方双三

#### def double34(x,y) #活三加4

#### def against_double34(x,y) # 防守对方活3加4

#### def angle_free(x,y) #我-三角无挡

#### def angle_not_free(x,y)我-三角1边挡

#### def lean2(x,y)#我-斜角成2

#### def flat2(x,y)#我-横竖成2

#### def available(x,y) #我-可行点

#### def get_features_score(x,y,qipu):(需要预测和评估公用，所以不能使用self.qipu)

​	需求 -> 根据当前的落子打分,该分数包括对我双方的操作，这样可以简化之前best_step里面乱七八糟的逻辑。

​		-> 该函数调用的子函数都不能和self.qipu相关。

​	主要内容 -> 对所有judge的feature进行判断True/False并且给出相应的分数，给出兜底的分数。

​	input -> x,y坐标

​	output -> score

### 逻辑1版本逻辑思路

#### 评估逻辑

只看当前对我的有利程度。

我-胜5  : 100  win5()

敌-胜5  : 99    against_win5()

我-活4  :  98 live4()

我-活34: 97 double34()

敌-活34:96 agianst_double34()

敌-活4  : 95 against_live4()

我-活双3:94 double3()

敌方活双3:93 against_double3()

我-活3:92 live3()

我-三角无挡:91 angle_free()

我-三角1边挡：90 angle_not_free()

敌-活3:89 against_live3()

我-斜角成2:3 lean2()

我-横竖成2:2 flat2()

我-可行点:1 available()

我-死子: -2 die_state()

#### def step_score_logic1(state):

​	主要内容：遍历搜索的点，给出分数

​	relation -> get_feature_score(x,y,player,self.qipu)

#### def best_step_logic1(state):

​	主要内容 -> 搜索出最大	

### base_line版本

#### def step_point_score_logic0(x,y):

​	output -> 单步返回值

#### def step_score_logic0(): ->修改接口 

​	relation -> get_feature_score(x,y,player,self.qipu)

​	output -> 每个坐标的值，与接口保持格式一致。

#### def best_step_logic1():  ->修改接口 

​	output -> 每个坐标的值，与接口保持格式一致。

### max-min搜索树

#### def step_score_maxmin_search(n):

​	relation ->  get_feature_score(x,y,player,qipu)

​	output -> 输出每个点的分数，路径，最后一层max的个数

#### def best_step_maxmin_search()： (敌我双方的判断需要区别)

​	-> output 最大的那个

​	->考虑点：

+ 搜索深度问题：相同分数，搜索越短越好，搜索返回相同分值时如何处理
  + 结束局迅速返回
  + 分数优先级>深度（正最大，负最小）>最后层max/min个数(正max,负min)>random      max个数的判断可以促进最优，防止放弃防守
  + 如果判断敌方优势后，需要找min，我方优势，需要max
+ 敌方胜利后如何返回
  + 比较敌我双方分数，相同步数mine>=enemy则选择我方正数，否则返回负数。因为这里优先级比较明显，所以我方分数高时则表示胜利的分数，如果敌方分数高则表明敌方胜利的分数，就是我输的分数。这里分数只代表大小，没有绝对值的大小相关性。

### mcts搜索(思路待完善，重构mcts函数，并考虑五子棋中的需求点)

蒙特卡洛这边暂时不考虑存储中间状态来换时间。

#### def uct(state,itermax):

​	input ->  当前状态和最大迭代次数

​	主要内容 -> 创建一个Node节点，迭代（select，expland，simulate，backpro）

​	output -> 看会node

#### def step_score_mcts_search(n):

​	relation -> uct(state,itermax)

​	思路 -> 处理uct反馈node的子节点visit,当做分数。

#### def best_step_mcts_search()：

​	

## 测试方案

### 时间测试

不同阶段best_step()的耗时情况。

+ 单步
+ max-min

### mcts开放测试

+ 自己去测试效果性能——给出3局博弈图
+ 看机器自对弈性能——给出3局博弈图

### 不同算法之间的博弈和参数测评

+ 单步、max-min、mcts相互博弈矩阵结果（其中max-min/mcts选择适中参数）
+ 使用max-min、mtcs单独和单步进行博弈，选取合适的参数，给出参数测评结果

### mtcs不同策略的测评

+ available情况下随机测评  
+ available下按照棋子评分select

### 预测

+ mtcs的时间会非常长
+ 以value来添加选择的方法会如果探索不够会很接近max-min
+ 不确定mcts会超过max-min - 希望mcts探索出超出我们想象的方案。

