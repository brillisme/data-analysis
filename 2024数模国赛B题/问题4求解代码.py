import numpy as np
# 计算问题3中每种情况的风险和成本乘积，并找到最佳决策
def solve_problem3():
    # 表2中企业在生产中遇到的情况
   零配件_data = np.array([
        [0.1, 2, 1],
        [0.1, 8, 1],
        [0.1, 12, 2],
        [0.1, 2, 1],
        [0.1, 8, 1],
        [0.1, 12, 2],
        [0.1, 8, 1],
        [0.1, 12, 2]
    ])

   半成品_data = np.array([
        [0.1, 8, 4, 6],
        [0.1, 8, 4, 6],
        [0.1, 8, 4, 6]
    ])

   finished_data = np.array([
        [0.1, 8, 6, 10, 200, 40]
    ])

# 风险的权重
   risk_weight = 1 / 6
# 成本和利润的权重
   cost_profit_weight = 5 / 6

   best_decision = None
   min_risk_cost_product = float('inf')

# 遍历所有可能的检测决策组合
   for 零配件_detection_decisions in range(2 ** 8):
        for 半成品_detection_decisions in range(2 ** 3):
            for finished_detection_decision in range(2):
                # 将二进制表示的检测决策转换为数组
               零配件_detection_decisions_array = np.array(list(bin(零配件_detection_decisions)[2:].zfill(8)), dtype=int)
               半成品_detection_decisions_array = np.array(list(bin(半成品_detection_decisions)[2:].zfill(3)), dtype=int)
# 计算总成本
               total_cost = 0
               for i in range(8):
                    part_cost = 零配件_data[i, 1] * (1 - 零配件_data[i, 0])
                    if 零配件_detection_decisions_array[i] == 1:
                        part_cost += 零配件_data[i, 2]
                    total_cost += part_cost

               for j in range(3):
                    semi_cost = 半成品_data[j, 1] * (1 - 半成品_data[j, 0]) + 半成品_data[j, 2]
                    # 根据次品率计算半成品次品数量
                    semi_defective_count = int(半成品_data[j, 0] * 半成品_data[j, 1])
                    if 半成品_detection_decisions_array[j] == 1 and semi_defective_count > 0:
                        semi_cost += 半成品_data[j, 3]  # 加上检测成本
                    total_cost += semi_cost  # 计算总的花费

               finished_cost =  finished_data[0, 1] * (1 -  finished_data[0, 0]) +  finished_data[0, 2]
# 根据次品率计算成品次品数量
               finished_defective_count = int( finished_data[0, 0] *  finished_data[0, 1])
               if finished_detection_decision == 1 and finished_defective_count > 0:
                    finished_cost +=  finished_data[0, 3] +  finished_data[0, 5]  # 加上检测成本和拆解费用
               total_cost += finished_cost

# 计算总风险（次品率之和）
               total_risk = np.sum(零配件_data[:, 0]) + np.sum(半成品_data[:, 0]) +  finished_data[0, 0]

# 计算风险和成本的乘积
               risk_cost_product = total_risk * total_cost * risk_weight * cost_profit_weight

# 更新最佳决策
               if risk_cost_product < min_risk_cost_product:
                    min_risk_cost_product = risk_cost_product
                    best_decision = (零配件_detection_decisions_array, 半成品_detection_decisions_array,
                                     finished_detection_decision)

   print("问题3的最佳决策是：零配件检测决策为", best_decision[0], "，半成品检测决策为", best_decision[1],
         "，成品检测决策为", best_decision[2], "，风险和成本的乘积为：", min_risk_cost_product)

if __name__ == "__main__":
    # solve_problem2()
    solve_problem3()