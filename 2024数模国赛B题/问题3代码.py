import numpy as np
# 直接在代码中提取表2的相关数值列出矩阵
# 零配件数据
parts_data = np.array([
    [35, 2, 1],
    [35, 8, 1],
    [35, 12, 2],
    [35, 2, 1],
    [35, 8, 1],
    [35, 12, 2],
    [35, 8, 1],
    [35, 12, 2]
])
# 半成品数据
semi_data = np.array([
    [35, 8, 4, 6],
    [35, 8, 4, 6],
    [35, 8, 4, 6]
])
# 成品数据
finished_data = np.array([
    [35, 8, 6, 20, 200, 40]
])
# 状态转移概率函数的定义
def define_transition_probs(parts_data, semi_data, finished_data):  #装配过程中各状态作为函数参数
    transition_probs = {}  #转移概率函数
    for i in range(1, 9):  # 8个零配件
        part_key = f'零配件{i}'
        transition_probs[part_key] = {
            '检测': {
                '合格': 1 - parts_data[i - 1, 0] / 100,
                '不合格': parts_data[i - 1, 0] / 100  # 给前面矩阵列表中的次品率除以100得到真正的次品率
            },
            '不检测': {
                '合格': 1 - parts_data[i - 1, 0] / 100,
                '不合格': parts_data[i - 1, 0] / 100
            }
        }
    for j in range(1, 4):
        semi_key = f'半成品{j}'
        transition_probs[semi_key] = {
            '检测': {
                '合格': 1 - semi_data[j - 1, 0] / 100,
                '不合格': semi_data[j - 1, 0] / 100
            },
            '不检测': {
                '合格': 1 - semi_data[j - 1, 0] / 100,
                '不合格': semi_data[j - 1, 0] / 100
            }
        }
    finished_key = '成品'
    transition_probs[finished_key] = {
        '检测': {
            '合格': 1 - finished_data[0, 0] / 100,
            '不合格': finished_data[0, 0] / 100
        },
        '不检测': {
            '合格': 1 - finished_data[0, 0] / 100,
            '不合格': finished_data[0, 0] / 100
        }
    }
    return transition_probs  # 返回转移概率用于后续价值函数的计算

# 状态空间的定义
states = ['零配件1', '零配件2', '零配件3', '零配件4', '零配件5', '零配件6', '零配件7', '零配件8',
          '半成品1', '半成品2', '半成品3', '成品']

# 动作空间的定义
actions = ['不检测', '检测']

# 检测成本矩阵的定义
detection_costs = np.array([
    [parts_data[0, 2], parts_data[1, 2], parts_data[2, 2], parts_data[3, 2], parts_data[4, 2], parts_data[5, 2],
     parts_data[6, 2], parts_data[7, 2]],
    [semi_data[0, 3], semi_data[1, 3], semi_data[2, 3], 0, 0, 0, 0, 0],
    [finished_data[0, 4], 0, 0, 0, 0, 0, 0, 0]
])

# 装配成本矩阵的定义
assembly_costs = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0],
    [semi_data[0, 2], semi_data[1, 2], semi_data[2, 2], 0, 0, 0, 0, 0],
    [finished_data[0, 2], 0, 0, 0, 0, 0, 0, 0]
])

# 拆解费用矩阵的定义
dismantling_costs = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0],  # 聚焦关键环节，只考虑成品的拆解
    [0, 0, 0, 0, 0, 0, 0, 0],
    [finished_data[0, 5], 0, 0, 0, 0, 0, 0, 0]
])

# 调换损失矩阵的定义
replacement_losses = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0],  # 全零原因同上
    [0, 0, 0, 0, 0, 0, 0, 0],
    [finished_data[0, 5], 0, 0, 0, 0, 0, 0, 0]
])

# 调用函数来获取状态转移概率
transition_probs = define_transition_probs(parts_data, semi_data, finished_data)

# 奖励函数的定义
rewards = np.zeros((len(states), len(actions)))
for i, state in enumerate(states):
    if state in ['零配件1', '零配件2', '零配件3', '零配件4', '零配件5', '零配件6', '零配件7', '零配件8']:
        if i < len(actions) and actions[i] == '检测':  # 防止actions[i]中的索引i超出了actions列表的范围
            rewards[i, 1] = -detection_costs[0, i]
        else:
            rewards[i, 0] = 0
    elif state in ['半成品1', '半成品2', '半成品3']:
        if i < len(actions) and actions[i] == '检测':
            rewards[i, 1] = -detection_costs[1, i - 8] - assembly_costs[1, i - 8]
        else:
            rewards[i, 0] = 0
    elif state == '成品':
        if i < len(actions) and actions[i] == '检测':
            rewards[i, 1] = -detection_costs[2, 0] - assembly_costs[2, 0]
            if transition_probs[state]['检测']['不合格'] > 0:
                # 分析拆解的情况
                # 假设拆解后重新加工的成本为 reprocess_cost
                reprocess_cost = 150
                # 如果拆解后重新加工成本小于调换损失，则选择拆解
                if reprocess_cost + dismantling_costs[2, 0] < replacement_losses[2, 0]:
                    rewards[i, 1] -= dismantling_costs[2, 0]
        else:
            rewards[i, 0] = 0
            if transition_probs[state]['不检测']['不合格'] > 0:
                rewards[i, 0] -= replacement_losses[2, 0]

# 初始化价值函数
values = np.zeros(len(states))

# 用贝尔曼法进行迭代更新价值函数
for _ in range(100):
    new_values = np.zeros(len(states))
    for i, state in enumerate(states):
        max_value = float('-inf')
        for j, action in enumerate(actions):
            reward = rewards[i, j]
            if state in ['半成品1', '半成品2', '半成品3'] and actions[j] == '检测':
                reward += -assembly_costs[1, i - 8]
            elif state == '成品' and actions[j] == '检测':
                reward += -assembly_costs[2, 0]
            if state == '成品' and actions[j] == '不检测' and transition_probs[state][action]['不合格'] > 0:
                reward += -replacement_losses[2, 0]
            if state == '成品' and actions[j] == '检测' and transition_probs[state][action]['不合格'] > 0:
                reward += -dismantling_costs[2, 0]
            prob = transition_probs[state][action]['合格']
            next_value = prob * values[i] + (1 - prob) * values[i]
            value = reward + next_value
            if value > max_value:  # 与目前记录的最大价值进行比较
                max_value = value
        new_values[i] = max_value  # 价值更大则进行替换
    values = new_values

# 输出最佳决策
best_decisions = []
for i, state in enumerate(states):
    max_value = float('-inf')  # 对最大价值初始化为负无穷大
    best_action = None  #初始化
    for j, action in enumerate(actions):
        reward = rewards[i, j]
        if state in ['半成品1', '半成品2', '半成品3'] and actions[j] == '检测':
            reward += -assembly_costs[1, i - 8]
        elif state == '成品' and actions[j] == '检测':
            reward += -assembly_costs[2, 0]
        if state == '成品' and actions[j] == '不检测' and transition_probs[state][action]['不合格'] > 0:
            reward += -replacement_losses[2, 0]
        if state == '成品' and actions[j] == '检测' and transition_probs[state][action]['不合格'] > 0:
            reward += -dismantling_costs[2, 0]
        prob = transition_probs[state][action]['合格']
        next_value = prob * values[i] + (1 - prob) * values[i]  # 计算考虑状态转移概率下与当前状态价值相关的下一个状态的价值
        value = reward + next_value  # 总的价值
        if value > max_value:  # 计算出的value和当前记录的最大价值max_value进行比较
            max_value = value
            best_action = action
    best_decisions.append(best_action)

print("最佳决策方案：", best_decisions)

