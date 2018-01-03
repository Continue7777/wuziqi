[TOC]

# 五子棋AI实现

## 架构设计

### 里程碑

+ 2018.1.3 - 给出不含神经网络评估的需求函数，重点：代码重构、性能考虑、评估考虑、搜索树max-min/mcts、最佳逻辑的完善、测试方案、输出报告，给出一份详细可操作可评审的报告。
+ 2018.1.7 - 完成编码、调试、测试、总结工作
+ 2018.1.12 - 完成rl和cnn模块的试水探索
+ 2018.1.14 - 完成包含rl和cnn模块的需求整理、代码重构、性能考虑、评估考虑、测试方案、输出报告
+ 2018.1.21 - 完成rl和cnn的编码工作并发现新问题
+ 2018.1.28 - 总结、博客整个工程。

### 需求

#### 场景逻辑

+ 单步对弈 one_step
+ 可视化单局对弈 one_game_visual
+ 评估 evalution
+ 细节评估 类似一个开关，打开后可以看到后续的选择思路

#### 性能需求

+ 需要一个服务器来跑，考虑如果高效的使用服务器资源以及结合本地展示。
+ 需要把控每个模块的大致时间

#### 模块需求

+ 动态的选择搜索树


+ mcts和max-min搜索的两部分对比设计
+ 基于神经网络的设计实现
+ 评估报表
+ 基于神经网络的评估数据

#### 算法需求

+ 搜索树模块：max-min,mcts
+ 策略选择模块：base_line_logic / better_logic / value_net(cnn)


### 详细文档

耗时：1.5h

#### 变量

state:整个棋盘的状态，目前为原始图

qipan_width,qipan_height: 棋盘的宽和高

#### 整体函数

##### def step_score(state,player_name)：(统一接口,充当配置函数的功能,所有场景下都过这个函数配置，不能直接调用之后的函数)

​	input -> state 输入当前状态函数 

​	内部配置mode  ->   'single'单步、’max-min‘最大最小树、'mcts'蒙特卡洛搜索

​	output -> narray 每个可能状态的得分值，合法的地方为正分数，其余为-1 （确保分数算出来没负的）

##### def best_step(state,player_name) :  (统一接口)  

​	relation -> step_score(state) : 调用整个评估，max就ok.

​	input ->state  输入当前状态函数

​		  -> player_name 为某个策略的算法命名

​	output -> (x,y )输出当前决策下最优的动作的坐标tuple

​	thoughts -> 仍然是每个算法对应一个函数，然后统一封装接口对外调用，这样在evalution中就可以使用名字来调用函数了，简化评估函数中逻辑。

##### def evalution(player_name_list,num)：

​	relation -> best_step(state,player_name)

​	input  -> player( ['name1','name2'] ) 

​		    -> num 互博次数

​	output -> result_dict['1-2'] = "10:5" ,这个看后续的处理，暂时只有看结果的需求

##### def one_step(state,player_name):

​	output	->  best_step(state,player_name) ,调用一步函数，返回，单纯的意义封装。

##### def one_game_visual(player_name1,player_name2):

​	relation ->  best_step(state,player_name)

#### 特征提取与评估

##### def feature_model(state): 

​	//评判函数模板，除双3，活3/4以外都有用。

​	for one_direciton_state one_direciton_states_list:

​		if feature_one_direction_model(one_direciton_state):

​			return True

​	return False

##### def win5(state) #胜5

##### def against_win5(state) #防守对方胜5

##### def live4(state) #活4

##### def against_live4(state) #防守对方活4

##### def live3(state) #活三

##### def against_live3(state) # 防守对方活三

##### def die_state(state)  #4方向不可能赢，被封死的点

##### def only1(state) #孤点

​	需求 -> 方圆2个没点，1个距离孤点也考虑进来

​	relation -> feature_model

​	input -> state

​	output -> True/False

##### def double3(state) #活双三

##### def against_double3(state) #防守对方双三

##### def double34(state) #活三加4

##### def against_double34 # 防守对方活3加4

##### 。。。。。

##### def get_features_score(x,y,player):

​	需求 -> 根据当前的落子打分,该分数包括对我双方的操作，这样可以简化之前best_step里面乱七八糟的逻辑。

​	主要内容 -> 对所有judge的feature进行判断True/False并且给出相应的分数，给出兜底的分数。

​	input -> x,y坐标，player当前子的一方

​	output -> score

#### 逻辑1版本逻辑思路

评估逻辑：分数出现在进攻防守状态都是合理的，这里只看优先级，感觉防守和进攻的分数会影响max-min的思路。

我-胜5  : 100

敌-胜5  : 99

我-活4  :  98

我-活34: 97

敌-活34:96

敌-活4  : 95

我-活双3:94

敌方活双3:93

我-活3:92

我-三角无挡:91

我-三角1边挡：90

敌-活3:89

我-斜角成2:3

我-横竖成2:2

我-可行点:1

我-死子: -2

##### def step_score_logic1(state):

​	主要内容：遍历搜索的点，给出分数

​	relation -> get_feature_score(x,y,player)

##### def best_step_logic1(state):

​	主要内容 -> 搜索出最大	

#### base_line版本

##### def step_score_logic0(player): ->修改接口 

​	output -> 每个坐标的值，与其他保持一致。

##### def best_step_logic1(state):  ->修改接口 

#### max-min搜索

##### def step_score_maxmin_search(n):

​	relation ->  get_feature_score(x,y,player)

​	output -> 输出每个点的分数，路径，最后一层max的个数

##### def best_step_maxmin_search()： (敌我双方的判断需要区别)

​	-> output 最大的那个

​	->考虑点：

+ 搜索深度问题：相同分数，搜索越短越好，搜索返回相同分值时如何处理
  + 结束局迅速返回
  + 分数优先级>深度（正最大，负最小）>最后层max/min个数(正max,负min)>random      max个数的判断可以促进最优，防止放弃防守
  + 如果判断敌方优势后，需要找min，我方优势，需要max
+ 敌方胜利后如何返回
  + 比较敌我双方分数，相同步数mine>=enemy则选择我方正数，否则返回负数。因为这里优先级比较明显，所以我方分数高时则表示胜利的分数，如果敌方分数高则表明敌方胜利的分数，就是我输的分数。这里分数只代表大小，没有绝对值的大小相关性。

#### mcts搜索(思路待完善，重构mcts函数，并考虑五子棋中的需求点)

##### def uct_score(x,y)

##### def step_score_mcts_search(n):

##### def best_step_mcts_search()：

​	





#### 



## 实践

### 思路

先不要参考网上的资料，把自己的思路先尝试。没有解决的问题再去查看。需要锻炼自己的工程能力和思考能力，不要老懒得想问题。

http://blog.csdn.net/syrchina/article/details/46698981 ：里面提到，根据搜索树，下输的时候给局面重新定义分数。等我的博弈树规则改好之后，重新定义分数，让电脑自学习。

自义定局势和分数—应该是终极目标。

-> 利用二分类问题判断概率并输出最大概率落子。利用cnn自动形成棋势特征抽取。



### 问题

现在的虽然很蠢可以写出更好的逻辑，但是并没有解决从baseline训练出更好能力的解决方案，现在是逻辑可以有很明显提升的时候，拿就用最有把握的思路去解题。

下一步骤建立在现在特征完善且参数给定的情况，希望能够自己训练出各个参数下的权重。

3 - 1 隔一个空构成的棋现在貌似是有bug的。

对于相同决策的返回处理不够优化。

​	-> 如果我已经100了，后续没有使用最小路径胜利。胜利偏向路径越小越好

​	-> 偏向我方路数最多越好

​	-> 终上所述，处理路径长短和整个局势的判断。（高分端的密集度）

​	-> 解决现在倾向于左上角的错误选择。需要修改get_logit_score（需要返回更多的信息，最高分的个数，交错情况。）

### 领任务

2017.12.10 修改特征逻辑、给定经验权重，并与之前的算法对抗看结果。 预计1个小时 2.5h了，bug还没调完。

2017.12.23 解决往后看步数的问题，思路如下：如果存在一条路径为：顺着这条路往下找，每一步敌人都必须防守，且最后我方能赢，走这条路。





### 2017.12.23

#### 感性需求：

向后探索n步，增强棋艺。根据现有对棋势的判断即可，在棋势的整体认知精度上并不会有提升。

#### 细化技术方案：

（以下两个问题都是性能和精度问题）

1. n的步数可调整，越多资源消耗远大，保证3步性能可靠。
2. 需要明确的几个问题
   1. 是否进行剪枝，根据中间过程的评分。  —— 暂时仅拿是否获胜。
   2. 对手的策略空间的确认问题、以及我方策略空间的确认。此处需要明确是所有可行空间还是高分空间  ——这里影响的也仅仅是效率问题，一个阈值就能搞定。
   3. 我方策略空间：第一个子尽可能大，后续均为现在最优判断。因为现在还不考虑最优解。不放过一定能赢的机会。

#### 流程图：

if 第一个点 -> 返回中心点

​		    ->	给棋盘设置虚拟棋谱，动态规划，单步走取最大的思路。return 最大对应的step1

#### 性能考虑：

估算每次30个step1,让对手做最可能发展的棋，不要走飞。O(n)。

#### 考虑工程实现方案：

1.需要想一种办法来估算分数，这里的评估和之前的冲突。

2.复制一份棋谱，qipu_predict={},每次在这张棋谱上判断。

#### 接口设计：

best_step_n(self)：—> x,y 判断n步探索模式下最优的坐标

->找到所有一次探索点

​	-> 可行点的判断条件：之前的打分0,1有一个>0即可

​	-> 如果没有点合适的话，切换成best_step

->找到该点路下的最优分数 _get_score(x,y) -> score 

​	->不同路径下返回的max是有区别的

​	->max(my_score,enemy_score)

->记录最大的score,并return x,y

​	-> 防止敌方最大化的时候，应该想办法优化我方棋局。

​	-> 敌方n步内最小

_get_score(x,y)->score： ————————————————ok
->新建立棋谱，添加x,y

->根据best_step1新增后续，来回5个回合，直到找到最优方案。

​	-> 返回的分数的含义需要直接指示我方棋子，所以和之前的分数不能混合max(my_score,enemy_score)，这个可以但是，my_score，enemy_score 的步数必须一样。如果我比敌方高，则取最高，如果都低则取最低，如果相等还是取自己。（这里博弈的思想就出来了）

​	



### 2017.12.24

1. 花30分钟把博弈的算法的得分再理一下。  ok
2. 1h写代码+debug   15:30 1步ok    ——————————1步存在的问题，全是活3的时候，变成了随机。活2和双三的交界一定会死。多看一步就 可以解决。——————我方存在很多96的时候，也会随便下。
3. 看博客里面怎么处理博弈树，以及其优化。