# 华人清洗·销售BU分润小程序

## 项目评估报告

**文档版本**：V1.0
**编制日期**：2026年5月20日
**建设单位**：PU经营委员会
**项目代号**：HUAXIN-BU-2026-APP

---

## 一、项目概述

### 1.1 项目背景

华人清洗已制定《N级BU/SU双轨裂变收益制度》，对标ASEA成熟商业模型，核心包括：
- **双轨制架构**：一级BU可以无限，二级BU及以后每人仅左、右两条线，实现二二复制与无限深度
- **复杂收益模型**：包含直推奖、对碰奖、无限代代数奖、滑落奖、职级分红等5大奖金
- **自动滑落机制**：超出2人的点位自动向下填充至最深空位

目前依赖Excel手工核算与钉钉有成业财系统的半自动流程，亟需开发专用分润小程序。

### 1.2 建设目标

| 目标 | 说明 |
|------|------|
| **自动化** | 业绩数据从有成CRM自动同步，奖金自动计算、自动发放 |
| **可视化** | 为每位BU/SU提供个人双轨树形图（无限代）、收益看板 |
| **合规化** | 所有计算逻辑严格对齐制度文件，内置风控与封顶规则 |
| **生态化** | 完全基于钉钉微应用开发，使用有成CRM开放API进行数据读写 |

### 1.3 技术栈定性

| 项目 | 内容 |
|------|------|
| **系统类型** | 钉钉H5微应用（小程序），不是Web系统 |
| **基于勾股OA开发？** | ❌ 否，勾股OA是PHP Web系统，无法做钉钉小程序集成 |
| **复用率** | 仅约5%（权限模型思路可借鉴） |
| **建议方案** | 新建Python项目开发 |

---

## 二、业务规则核心

### 2.1 双轨架构

| 规则 | 说明 |
|------|------|
| 一级BU | 无限推荐，直推数量不限 |
| 二级BU及以后 | 每人仅左、右两条主线 |
| 自动滑落 | 第3人及以后自动向下滑落至最深空位 |
| 深度 | 无限代 |

### 2.2 积分体系

| 积分 | 说明 | 计算方式 |
|------|------|---------|
| **PV** | 个人业绩 | 合同回款（不含税） |
| **RV左/右线** | 团队业绩 | 左/右线所有下级PV之和 |
| **GV** | 组织业绩 | 所有下级PV之和（无限代） |
| **PGV** | 晋升业绩 | 达成职级条件的GV |

### 2.3 身份体系

```
SU销售经理 → N级BU（1级、2级...） → 高级BU（白金/钻石/总统钻石）
```

| 职级 | 晋升条件 |
|------|---------|
| SU | 预备合伙人 |
| N级BU | 注册即得 |
| 白金BU | PGV达标 |
| 钻石BU | PGV达标 |
| 总统钻石BU | PGV达标 |

### 2.4 五大奖金

| 奖金类型 | 计算方式 | 发放对象 |
|---------|---------|---------|
| **直推奖** | 直推BU首年利润×5% + 次年利润×2% | 所有BU/SU |
| **对碰奖** | MIN(左线RV, 右线RV) × 2%，月封顶=PV×30% | BU及以上 |
| **代数奖** | 1-10代×1%，11-20代×0.5%，21代+×0.2% | BU及以上 |
| **滑落奖** | 滑落BU首年利润×1% | 安置人 |
| **职级分红** | 白金/钻石/总统钻石按季度瓜分奖金池 | 高职级BU |

### 2.5 风控规则

- 个人月度裂变收益总额 ≤ 本BU PV × 30%（月封顶）
- 无入门费
- 无囤货
- 无保证金

---

## 三、技术架构方案

### 3.1 技术选型

| 层级 | 推荐方案 | 说明 |
|------|---------|------|
| **前端** | 钉钉H5微应用（Vue3/uni-app） | 可内嵌钉钉，调用dd.*原生能力 |
| **后端** | Python FastAPI | 适合高并发、复杂计算 |
| **数据库** | MySQL 8.0 + Redis | MySQL存业务，Redis缓存树结构 |
| **定时任务** | Celery + Redis | 月度核算、CRM同步 |
| **部署** | 阿里云ECS + Docker | 对接钉钉服务器白名单 |

### 3.2 核心数据模型

```sql
-- 会员节点（无限代二叉树）
CREATE TABLE member_node (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(64) UNIQUE NOT NULL,      -- 钉钉UserID
    name VARCHAR(64),
    member_code VARCHAR(32),                   -- BU/SU编号
    
    -- 关系字段
    parent_id BIGINT,                          -- 安置人ID
    recommend_id BIGINT,                       -- 推荐人ID
    position ENUM('left','right'),            -- 安置线
    generation INT DEFAULT 1,                 -- 代数
    
    -- 职级与PV
    rank_level ENUM('su','bu1','bu_n','platinum','diamond','president') DEFAULT 'su',
    pv DECIMAL(15,2) DEFAULT 0,              -- 个人PV
    gv DECIMAL(15,2) DEFAULT 0,              -- 组织业绩（无限代）
    left_rv DECIMAL(15,2) DEFAULT 0,         -- 左线RV
    right_rv DECIMAL(15,2) DEFAULT 0,         -- 右线RV
    
    -- 路径（用于快速祖先查询）
    lineage_path VARCHAR(4000),               -- 格式：/,1,5,23,/
    
    status ENUM('pending','active','frozen') DEFAULT 'pending',
    created_at DATETIME,
    updated_at DATETIME,
    
    INDEX idx_parent (parent_id),
    INDEX idx_recommend (recommend_id),
    INDEX idx_lineage (lineage_path(255))
);

-- 业绩记录
CREATE TABLE performance_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    member_id BIGINT NOT NULL,
    pv DECIMAL(15,2),                         -- 个人业绩
    profit DECIMAL(15,2),                     -- 利润
    source ENUM('crm_auto','manual'),         -- 数据来源
    crm_order_id VARCHAR(128),                -- 有成CRM订单ID
    period VARCHAR(7),                         -- YYYY-MM
    created_at DATETIME,
    
    INDEX idx_member_period (member_id, period)
);

-- 奖金记录
CREATE TABLE commission_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    member_id BIGINT NOT NULL,
    commission_type ENUM('direct','match','generation','slip','rank'),
    amount DECIMAL(15,2),                     -- 应发金额
    tax DECIMAL(15,2),                        -- 个税
    net_amount DECIMAL(15,2),                 -- 实发金额
    period VARCHAR(7),                         -- YYYY-MM
    
    status ENUM('pending','approved','paid') DEFAULT 'pending',
    operator VARCHAR(64),                     -- 操作人
    remark VARCHAR(256),                       -- 备注
    
    created_at DATETIME,
    INDEX idx_member_period (member_id, period)
);

-- 操作日志（合规审计）
CREATE TABLE audit_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    operator VARCHAR(64),
    action VARCHAR(64),
    target_table VARCHAR(64),
    target_id BIGINT,
    before_value JSON,
    after_value JSON,
    created_at DATETIME
);
```

### 3.3 自动滑落算法

```python
def auto_slip(parent_id: int, target_line: str) -> int:
    """
    核心：找到最深空位
    1. 检查目标线上级节点是否满员（左右各2人）
    2. 若满，递归向下找空位
    3. 返回最终安置节点ID
    """
    parent = db.get_node(parent_id)
    
    # 获取左右子节点
    left_child = db.get_node(parent.left_child_id) if parent.left_child_id else None
    right_child = db.get_node(parent.right_child_id) if parent.right_child_id else None
    
    # 检查目标线是否为空
    if target_line == 'left' and left_child is None:
        return parent_id  # 左线空位，直接返回
    
    # 左右都满了，递归滑落
    if left_child and right_child:
        # 优先滑落到较浅的子树（保持平衡）
        left_depth = get_max_depth(left_child.id)
        right_depth = get_max_depth(right_child.id)
        
        if left_depth <= right_depth:
            return auto_slip(left_child.id, 'left')
        else:
            return auto_slip(right_child.id, 'right')
    
    return parent_id


def get_max_depth(node_id: int) -> int:
    """获取某节点下的最大深度"""
    node = db.get_node(node_id)
    children = [node.left_child_id, node.right_child_id]
    children = [c for c in children if c]
    
    if not children:
        return 1
    
    return 1 + max(get_max_depth(c) for c in children)


def get_subtree_pv(node_id: int) -> Decimal:
    """
    递归计算子树PV总和（用于GV/RV计算）
    """
    node = db.get_node(node_id)
    total = node.pv
    
    if node.left_child_id:
        total += get_subtree_pv(node.left_child_id)
    if node.right_child_id:
        total += get_subtree_pv(node.right_child_id)
    
    return total
```

### 3.4 奖金核算引擎

```python
from decimal import Decimal
from datetime import datetime


class CommissionEngine:
    """奖金核算引擎"""
    
    # 代数奖梯度
    GEN_GRADIENT = [
        (10, Decimal('0.01')),   # 1-10代: 1%
        (20, Decimal('0.005')),   # 11-20代: 0.5%
        (float('inf'), Decimal('0.002'))  # 21代+: 0.2%
    ]
    
    # 月封顶系数
    MONTHLY_CAP_RATE = Decimal('0.30')
    
    def calc_direct_bonus(self, member_id: int) -> Decimal:
        """
        直推奖：直推BU首年利润×5% + 次年利润×2%
        """
        member = self.get_member(member_id)
        direct_referrals = self.get_direct_children(member_id)  # 推荐人=member_id
        
        bonus = Decimal('0')
        for child in direct_referrals:
            bonus += child.first_year_profit * Decimal('0.05')
            bonus += child.second_year_profit * Decimal('0.02')
        
        return bonus
    
    def calc_match_bonus(self, member_id: int, period: str) -> Decimal:
        """
        对碰奖：MIN(左线RV, 右线RV) × 2%，月封顶=PV×30%
        """
        member = self.get_member(member_id)
        
        # 递归计算左右线RV（无限代）
        left_rv = self.get_line_rv(member.left_child_id) if member.left_child_id else Decimal('0')
        right_rv = self.get_line_rv(member.right_child_id) if member.right_child_id else Decimal('0')
        
        # 小区业绩 × 2%
        small_rv = min(left_rv, right_rv)
        gross = small_rv * Decimal('0.02')
        
        # 月封顶 = PV × 30%
        pv = self.get_period_pv(member_id, period)
        cap = pv * self.MONTHLY_CAP_RATE
        
        return min(gross, cap)
    
    def calc_generation_bonus(self, member_id: int) -> Decimal:
        """
        代数奖：沿路径向上遍历所有祖先节点，按代数梯度计算
        """
        ancestors = self.get_ancestors(member_id)  # [(depth, node), ...]
        bonus = Decimal('0')
        
        for depth, ancestor in ancestors:
            # 查找当前代数对应的梯度
            rate = self._get_generation_rate(depth)
            bonus += ancestor.profit * rate
        
        return bonus
    
    def _get_generation_rate(self, generation: int) -> Decimal:
        """获取代数对应的奖金比例"""
        for max_gen, rate in self.GEN_GRADIENT:
            if generation <= max_gen:
                return rate
        return self.GEN_GRADIENT[-1][1]
    
    def calc_slip_bonus(self, member_id: int) -> Decimal:
        """
        滑落奖：推荐人是A，但安置在当前用户树下的BU，首年利润×1%
        """
        slip_children = self.get_slip_children(member_id)  # 推荐人≠安置人
        return sum(node.first_year_profit * Decimal('0.01') for node in slip_children)
    
    def calc_rank_bonus(self, member_id: int, period: str) -> Decimal:
        """
        职级分红：按季度，根据个人GV占比分配奖金池
        """
        member = self.get_member(member_id)
        
        # 检查职级
        if member.rank_level not in ['platinum', 'diamond', 'president']:
            return Decimal('0')
        
        # 获取奖金池
        pool = self.get_rank_pool(period, member.rank_level)
        
        # 获取同职级总GV和个人GV
        total_gv = self.get_rank_total_gv(period, member.rank_level)
        personal_gv = member.gv
        
        if total_gv == 0:
            return Decimal('0')
        
        # 按GV占比分配
        return pool * (personal_gv / total_gv)
    
    def calc_all_commission(self, member_id: int, period: str) -> dict:
        """计算某会员某期间所有奖金"""
        return {
            'direct': self.calc_direct_bonus(member_id),
            'match': self.calc_match_bonus(member_id, period),
            'generation': self.calc_generation_bonus(member_id),
            'slip': self.calc_slip_bonus(member_id),
            'rank': self.calc_rank_bonus(member_id, period),
        }
```

### 3.5 个税计算（7级超额累进）

```python
def calc_tax(amount: Decimal) -> Decimal:
    """个税计算 - 7级超额累进税率"""
    if amount <= 5000:
        return Decimal('0')
    elif amount <= 36000:
        return amount * Decimal('0.03') - Decimal('0')
    elif amount <= 144000:
        return amount * Decimal('0.10') - Decimal('210')
    elif amount <= 300000:
        return amount * Decimal('0.20') - Decimal('1410')
    elif amount <= 420000:
        return amount * Decimal('0.25') - Decimal('2660')
    elif amount <= 660000:
        return amount * Decimal('0.30') - Decimal('4410')
    elif amount <= 960000:
        return amount * Decimal('0.35') - Decimal('7160')
    else:
        return amount * Decimal('0.45') - Decimal('15160')
```

---

## 四、功能模块规划

### 4.1 功能列表

| 模块 | 功能点 | 优先级 |
|------|--------|--------|
| **钉钉集成** | SSO登录、钉钉消息通知 | P0 |
| **有成CRM对接** | OAuth2.0授权、回款数据同步 | P0 |
| **会员管理** | 注册审批、邀请码、身份升级 | P0 |
| **双轨树** | 树形展示（无限代）、滑落算法 | P0 |
| **业绩系统** | PV/RV/GV录入与自动同步 | P0 |
| **奖金引擎** | 5大奖金自动计算 | P0 |
| **收益看板** | 奖金明细、趋势图、发放单 | P1 |
| **PU后台** | 全司树、参数配置、核算任务 | P1 |
| **第三方打款** | 钉钉薪资/支付宝批量发放 | P2 |

### 4.2 页面清单

| 页面 | 角色 | 说明 |
|------|------|------|
| 登录页 | 全部 | 钉钉SSO授权 |
| 会员注册 | 外部 | 填写邀请码、提交资料 |
| 个人中心 | BU/SU | 个人信息、职级、邀请码 |
| 双轨树 | BU/SU | 树形图（左右线分离） |
| 收益看板 | BU/SU | 5大奖金明细、趋势图 |
| 业绩录入 | PU | 手动录入/修正业绩 |
| 全司树 | PU | 查看所有节点 |
| 奖金核算 | PU | 触发核算、查看日志 |
| 参数配置 | PU | 奖金比例、封顶系数 |
| 发放管理 | PU | 奖金审核、发放 |

---

## 五、Excel公式分析

### 5.1 Sheet说明

| Sheet | 用途 |
|-------|------|
| **业绩数据录入表** | 月度PV、利润录入 |
| **双轨关系表** | 树形关系（推荐人、代数、所属线） |
| **个人收益核算表** | 5大奖金计算公式 |
| **整体核算表** | 全公司奖金池汇总 |
| **奖金发放表** | 发放清单+个税计算 |

### 5.2 公式解析

#### 直推奖
```excel
=SUM(利润×推荐人=A3×5%) + SUM(利润×推荐人=A3×3%)
```
- 第一部分：直推BU首年利润 × 5%
- 第二部分：直推BU次年利润 × 3%

#### 对碰奖
```excel
=MIN(左线总RV, 右线总RV) × 2%, 再与 PV×30% 取小
```

#### 代数奖
```excel
=SUM(利润×代数≤10×1%) + SUM(利润×代数≤20×0.5%) + SUM(利润×代数>20×0.2%)
```

#### 职级分红
```excel
=奖金池比例 × (个人GV / 同职级总GV)
```

### 5.3 Excel公式问题

| 问题 | 说明 | 严重度 |
|------|------|--------|
| 直推奖公式Bug | 推荐人=A3会匹配自身，应为匹配推荐人ID列 | 🔴 高 |
| 代数奖公式Bug | 3个SUM条件都基于同一利润列，无视代数筛选 | 🔴 高 |
| 代数奖梯度缺失 | 11-20代0.5%、21代+0.2%没有正确体现 | 🔴 高 |
| 无限代无法实现 | Excel SUM无法递归遍历，只能按代数列静态筛选 | 🟡 中 |
| 滑落无法验证 | Excel无法模拟自动滑落，只能预设数据 | 🟡 中 |

> **结论**：Excel只能作为数据模板，实际奖金计算必须由后端代码实现。

---

## 六、测试用例

### 6.1 双轨树数据（基于Excel示例）

```
PU001(唐奇，顶层PU)
└── BU001(张三) [左, 代数1, 一级BU, PV=500000, 利润=100000]
    ├── BU002(李四) [左, 代数2, 二级BU, PV=300000, 利润=60000]
    │   ├── BU003(赵六) [左, 代数3, 三级BU, PV=200000, 利润=40000]
    │   └── BU004(孙七) [右, 代数3, 三级BU, PV=? , 利润=?]
    └── SU001(王五) [右, 代数2, SU, PV=100000, 利润=20000]
```

### 6.2 验收测试用例

| 测试用例 | 计算逻辑 | 期望结果 |
|---------|---------|---------|
| **张三-直推奖** | 李四利润×5% + 王五利润×5% | 60000×5% + 20000×5% = 3000+1000 = 4000 |
| **张三-对碰奖** | MIN(左线RV, 右线RV)×2%, ≤PV×30% | 假设左右线数据后计算 |
| **张三-代数奖** | 李四利润×1% + 赵六利润×1% | 60000×1% + 40000×1% = 600+400 = 1000 |
| **王五-滑落奖** | 无滑落节点=0 | 0 |
| **李四-代数奖** | 赵六利润×1% + 孙七利润×1% | 待确认孙七数据 |

### 6.3 性能测试指标

| 指标 | 要求 |
|------|------|
| 树加载时间 | 5000节点 < 3秒 |
| 月度全量核算 | < 30秒 |
| 并发支持 | 100人同时访问 |
| 对碰奖误差 | < 0.01元 |

---

## 七、开发周期评估

### 7.1 工期估算

| 阶段 | 工作内容 | 人天 |
|------|---------|------|
| **P0** | 钉钉H5框架搭建、SSO登录 | 5天 |
| **P1** | 有成CRM API对接（OAuth2.0、回款同步） | 15天 |
| **P2** | 会员注册、审批、邀请码体系 | 8天 |
| **P3** | 双轨树结构（安置、滑落、推荐关系） | 15天 |
| **P4** | 业绩系统（PV/RV/GV录入与同步） | 8天 |
| **P5** | 奖金核算引擎（5大奖金算法） | 18天 |
| **P6** | 收益看板（图表、职级晋升、发放单） | 10天 |
| **P7** | PU后台管理（全司树、参数配置） | 10天 |
| **P8** | 单元测试 + 全流程联调 | 8天 |
| **P9** | 部署上线 + 性能优化 | 5天 |
| **合计** | | **~90天（4人并发约23天）** |

### 7.2 费用估算

#### 方案A：MVP精简版
*砍掉职级分红池、BI报表、第三方打款接口*

| 角色 | 人天 | 单价 | 小计 |
|------|------|------|------|
| Python后端 | 35天 | ¥1,800 | ¥63,000 |
| 前端H5开发 | 25天 | ¥1,500 | ¥37,500 |
| 钉钉/CRM集成 | 12天 | ¥2,000 | ¥24,000 |
| DBA + 运维 | 5天 | ¥1,800 | ¥9,000 |
| PM | 5天 | ¥1,500 | ¥7,500 |
| **合计** | **~82天** | | **¥141,000** |

#### 方案B：全功能版
*完整5大奖金 + 完整集成*

| 角色 | 人天 | 单价 | 小计 |
|------|------|------|------|
| Python后端 | 50天 | ¥1,800 | ¥90,000 |
| 前端H5开发 | 30天 | ¥1,500 | ¥45,000 |
| 钉钉/CRM集成 | 20天 | ¥2,000 | ¥40,000 |
| DBA + 运维 | 8天 | ¥1,800 | ¥14,400 |
| PM | 8天 | ¥1,500 | ¥12,000 |
| **合计** | **~116天** | | **¥201,400** |

> 💡 以上均含**6%增值税专票**
> 💰 首年运维费：每年¥20,000-36,000

---

## 八、供应商评审要点

### 8.1 必须能回答的问题

| 问题 | 考察点 |
|------|--------|
| 递归计算方案 | 无限代向上遍历祖先节点，SQL怎么写？递归CTE还是代码循环？ |
| 性能方案 | 5000节点双轨树，对碰奖全量核算如何在30秒内完成？ |
| 滑落算法 | 如何找到"最深空位"？并发注册时冲突如何处理？ |
| 数据一致性 | 并发注册时，两个用户同时绑定同一节点，如何处理？ |

### 8.2 技术方案评审表

| 评审项 | 权重 | 评审要点 |
|--------|------|---------|
| 双轨树实现方案 | 25% | 滑落算法、树查询性能 |
| 奖金核算方案 | 30% | 5大奖金算法、对碰封顶逻辑 |
| 有成CRM集成方案 | 20% | OAuth2.0、数据同步机制 |
| 性能保障方案 | 15% | 5000节点<3秒、核算<30秒 |
| 安全合规方案 | 10% | HTTPS、数据加密、操作日志 |

---

## 九、交付物清单

| 交付物 | 说明 |
|--------|------|
| 钉钉H5微应用 | 前端+后端完整包 |
| 源代码 | 含注释 |
| 数据库脚本 | 建表语句、初始化数据 |
| 部署手册 | 环境、步骤、备份 |
| 用户手册 | 分角色操作说明 |
| API文档 | 与钉钉、有成CRM交互接口 |
| 测试报告 | 功能测试、性能测试 |

---

## 十、验收标准

| 验收点 | 标准 |
|--------|------|
| CRM数据同步 | 成功从有成CRM拉取回款数据，自动生成PV |
| 双轨树准确 | 3层双轨树（1带2,2带3），滑落正确 |
| 直推奖 | 误差 < 0.01元 |
| 对碰奖 | 误差 < 0.01元，月封顶生效 |
| 代数奖 | 1-10代1%，11-20代0.5%，21代+0.2% |
| 滑落奖 | 滑落节点识别正确 |
| 性能 | 100并发访问双轨树，响应 < 2秒 |
| 日志 | 所有操作可追溯 |

---

**编制人**：CaySon AI助手
**联系方式**：hrqxcg@126.com
