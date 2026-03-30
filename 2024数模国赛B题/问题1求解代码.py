import numpy as np
import scipy.stats as stats
# 相关定量的定义
flawed_rate = 0.10   # 标称值
confidence_L_95 = 0.95  # 信度
confidence_L_90 = 0.90
tolerance = 0.05  # 容差
# 利用二项分布进行假设检验的函数
'''
以上常量根据计算公式得出，其中
Z：标准正态分布的临界值
p:次品率的假设值
T：误差允许值即容差'''
def binomial_test(sample_capacity, flawed_items, flawed_rate, confidence_L):
    alpha = 1 - confidence_L  # 假设次品率下的显著性水平计算
    # 计算显著性水平p值
    result = stats.binomtest(flawed_items, sample_capacity, flawed_rate, alternative='greater')
    if result.pvalue < alpha:  # 当p值小于显著性水平时，零假设不成立
        return f"不接收零配件(p值: {result.pvalue:.4f})"  # 返回p值
    else:
        return f"接收零配件(p值: {result.pvalue:.4f})"
# 计算最小样本容量的函数
def c_min_s_s(flawed_rate, confidence_L, tolerance):
    # 返回对应的标准正态分布分位数（即 Z 分数）
    z_score = stats.norm.ppf(1 - (1 - confidence_L) / 2)
    sample_capacity = (z_score**2 * flawed_rate * (1 - flawed_rate)) / (tolerance**2)
    return int(np.ceil(sample_capacity))

# 假设出的样本次品数
detected_flawed_items = 12

# 两种置信水平下的最小样本量代值计算
sample_capacity_95 = c_min_s_s(flawed_rate, confidence_L_95, tolerance)
sample_capacity_90 = c_min_s_s(flawed_rate, confidence_L_90, tolerance)
print(f"信度为95%的最小样本量:{sample_capacity_95}")
print(f"信度为90%的最小样本量:{sample_capacity_90}")

# 对两种信度下的结果进行二项分布的显著性假设检验
result_95 = binomial_test(sample_capacity_95, detected_flawed_items, flawed_rate, confidence_L_95)
result_90 = binomial_test(sample_capacity_90, detected_flawed_items, flawed_rate, confidence_L_90)
print(f"信度为95%的结果:{result_95}")
print(f"信度为90%的结果:{result_90}")

