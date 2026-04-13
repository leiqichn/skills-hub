---
name: lte-cell-creation-huawei
description: |
  通过华为MML命令创建和配置LTE小区。提供完整的MML命令模板和工作流程，指导用户完成小区创建、参数配置、邻区配置等操作。适用于华为LTE基站(BSC/RNC/eNodeB)的开局和调试场景。
  **触发场景**：创建小区、配置LTE小区、MML命令、华为基站开局、小区参数配置、邻区配置、创建eNodeB。
triggers:
  - "创建小区"
  - "华为LTE.*MML"
  - "MML.*小区"
  - "eNodeB.*配置"
  - "创建.*邻区"
  - "LTE.*开局"
  - "华为基站.*配置"
  - "cell.*creation"
  - "MML.*command"
  - "Huawei.*LTE.*config"
---

# 华为 LTE 小区创建工具

本 skill 提供通过 MML (Man Machine Language) 命令创建和配置华为 LTE 小区的完整工作流程。

## MML 命令基础

### 连接方式

```bash
# 1. SSH 连接基站
ssh operator@<基站IP>

# 2. 进入MML模式
MML

# 3. 执行MML命令
ADD CELL
```

### 常用操作模式

| 模式 | 说明 | 进入命令 |
|------|------|----------|
| Configuration | 配置模式 | `CONF` |
| MML | 人机命令模式 | `MML` |
| Diagnosis | 诊断模式 | `DIAG` |

## 小区创建完整流程

```
准备工作 → 创建基带资源 → 创建小区 → 配置邻区 → 激活小区 → 验证
```

### 步骤 1：准备工作 - 查询基站信息

```mml
# 查询基站基本信息
ADD BRD

# 查询小区状态
ADD CELL

# 查询设备版本
ADD VER
```

### 步骤 2：创建基带资源

```mml
; ============================================================
; 创建基带单元 (BBU)
; ============================================================

; 查询可用的基带板
ADD BRD:;

; 创建基带资源组
ADD BRDRESGRP:RN=0,BRDRESGRPID=0;

; ============================================================
; 配置射频单元 (RRU/RRH)
; ============================================================

; 添加射频单元
ADD RRU:RN=0,SRN=0,PN=0,RRUTYPE=RRU3804S,PSID=0;

; 配置射频单元参数
MOD RRU:RN=0,SRN=0,PN=0,TXATTEN=300,RXATTEN=0;
```

### 步骤 3：创建小区

```mml
; ============================================================
; 创建 LTE FDD 小区
; ============================================================

; 基础小区参数
ADD CELL: CELLID=0, CELLNAME="LTE_FDD_0001", 
        RNCID=0, RAC=0, SAC=0,
        BAND=3, UARFCN=1650, EARFCN=1850,
        BANDWIDTH=20MHz, MAXTXPOWER=20,
        CELLTYPE=FDD_CELL;

; 详细小区配置
ADD CELL: CELLID=0, CELLNAME="CELL_SH_PARK_01",
        RAT=LTE, BAND=3,
        EARFCN_DL=1850, EARFCN_UL=24150,
        BANDWIDTH=20, MAXTXPOWER=43,
        TAC=10001, RAC=1,
        PCC_RELTXMODE=TM3, PCC_RLTXMIMO=2X2,
        DL_256QAM=1, UL_64QAM=1;

; 配置小区标识
MOD CELLID: CELLID=0, LOCALCELLID=0, ECELLID=460001234567890;
```

### 步骤 4：配置小区参数

```mml
; ============================================================
; 配置小区基本参数
; ============================================================

; 配置小区选择参数
MOD CELLSTX: CELLID=0, 
            QRXLEVMIN=-64, 
            QUALTHRESH=3,
            MAXVALLOWEDRXLEV=-62;

; 配置功率参数
MOD CELLPOWER: CELLID=0,
              DLPCCPOWER=-10,
              DLPBCCHPOWER=0,
              DLPWRAMP=43,
              ULPWRAMP=24;

; 配置天线模式
MOD ANTENNA: CELLID=0,
            ANTENNATYPE=2T2R,
            ANTENNAID=0,
            RETSUPPORT=1,
            AZIMUTH=0,
            TILT=3,
            HEIGHT=25;
```

### 步骤 5：配置邻区关系

```mml
; ============================================================
; 配置邻区关系 (外部邻区 + 小区邻区)
; ============================================================

; 添加外部小区
ADD EXTCELL: CELLID=100, EXTERNALCELLID=100,
            MCC=460, MNC=01,
            CELLNAME="NEIGHBOR_CELL_01",
            RAT=LTE, BAND=3,
            EARFCN=1850, ECELLID=460001234567891,
            TAC=10002;

; 添加小区邻区关系
ADD NRN: SOURCE=CELLID=0, TARGETCELL=100, NRTYPE=RTN;

; 配置邻区参数
MOD NRTX: CELLID=0, TARGETCELL=100,
         NOFFSET=10, QOFFSET=-3;

; ============================================================
; 配置X2接口邻区
; ============================================================

; 添加X2邻区
ADD X2NRCELL: CELLID=0, X2CELLID=100,
             X2IP="10.1.1.100",
             X2STATE=ACTIVE;
```

### 步骤 6：配置传输和接口

```mml
; ============================================================
; 配置S1/X2接口
; ============================================================

; 配置S1接口
ADD S1: CELLID=0, S1_IP="10.1.1.1",
       MME_IP="10.1.2.1",
       S1_LINK=0;

; 配置X2接口IP
ADD X2IP: CELLID=0, X2_IP="10.1.1.2",
         PEER_IP="10.1.1.100";

; 配置VLAN
ADD VLAN: VLANID=100, PORT=0, CVID=100;
```

### 步骤 7：激活小区

```mml
; ============================================================
; 激活小区
; ============================================================

; 开小区
ACT CELL: CELLID=0;

; 激活基带单元
ACT BRD: RN=0, BRDID=0;

; 激活传输
ACT S1: CELLID=0;

; 验证小区状态
DSP CELL: CELLID=0;
DSP BRD: RN=0;
```

## 常用 MML 命令速查

### 小区操作

| 操作 | 命令 | 说明 |
|------|------|------|
| 创建小区 | `ADD CELL` | 添加新小区 |
| 删除小区 | `RMV CELL` | 删除小区 |
| 修改小区 | `MOD CELL` | 修改小区参数 |
| 激活小区 | `ACT CELL` | 激活小区 |
| 去激活小区 | `DEA CELL` | 去激活小区 |
| 查询小区 | `DSP CELL` | 显示小区状态 |

### 基带/射频操作

| 操作 | 命令 | 说明 |
|------|------|------|
| 添加基带板 | `ADD BRD` | 添加基带单元 |
| 配置RRU | `ADD RRU` | 添加射频单元 |
| 配置天线 | `MOD ANTENNA` | 修改天线参数 |
| 查询RRU状态 | `DSP RRU` | 显示RRU状态 |

### 邻区操作

| 操作 | 命令 | 说明 |
|------|------|------|
| 添加外部邻区 | `ADD EXTCELL` | 添加外部小区 |
| 添加邻区关系 | `ADD NRN` | 添加邻区关系 |
| 删除邻区 | `RMV NRN` | 删除邻区关系 |
| 配置CIO | `MOD NRTX` | 修改邻区偏置 |

## 完整示例

### 创建 20MHz 带宽的 FDD 小区

```mml
; ============================================================
; 华为 LTE 小区创建脚本
; 小区名称: LTE_SH_CELL_01
; 频段: Band 3 (1800MHz)
; 带宽: 20MHz
; ============================================================

; ---------- 1. 基带配置 ----------
ADD BRDRESGRP:RN=0,BRDRESGRPID=0,BRDTYPE=3902;

; ---------- 2. 射频配置 ----------
ADD RRU:RN=0,SRN=0,PN=0,RRUTYPE=RRU3804S,PSID=0;
MOD RRU:RN=0,SRN=0,PN=0,TXATTEN=300;

; ---------- 3. 小区参数 ----------
ADD CELL: 
    CELLID=0, 
    CELLNAME="LTE_SH_CELL_01",
    RAT=LTE, 
    BAND=3,
    EARFCN_DL=1850,      ; 下行频点
    EARFCN_UL=24150,    ; 上行频点
    BANDWIDTH=20,        ; 带宽20MHz
    MAXTXPOWER=43,      ; 最大发射功率43dBm
    TAC=10001,           ; 跟踪区域码
    PCC_RELTXMODE=TM3,   ; TM3传输模式
    CELLTYPE=FDD_CELL;

; ---------- 4. 小区选择 ----------
MOD CELLSTX: 
    CELLID=0,
    QRXLEVMIN=-64,      ; 最小接入电平
    QUALTHRESH=3;

; ---------- 5. 邻区配置 ----------
ADD EXTCELL: 
    CELLID=100, 
    EXTERNALCELLID=100,
    MCC=460, MNC=01,
    CELLNAME="NEIGHBOR_A",
    RAT=LTE, BAND=3,
    EARFCN=1850,
    ECELLID=460001234567891,
    TAC=10002;

ADD NRN: SOURCE=0, TARGETCELL=100, NRTYPE=RTN;

; ---------- 6. 传输配置 ----------
ADD S1: 
    CELLID=0, 
    S1_IP="10.1.1.1",
    MME_IP="10.1.2.1";

; ---------- 7. 激活 ----------
ACT CELL: CELLID=0;

; ---------- 8. 验证 ----------
DSP CELL: CELLID=0;
```

### 创建双模小区 (F+D)

```mml
; ============================================================
; 创建 LTE FDD + LTE TDD 双模小区
; ============================================================

; FDD小区
ADD CELL: CELLID=0, CELLNAME="LTE_FDD_01",
        RAT=LTE, BAND=3, 
        EARFCN_DL=1850, BANDWIDTH=20;

; TDD小区
ADD CELL: CELLID=1, CELLNAME="LTE_TDD_01",
        RAT=LTE, BAND=41,
        EARFCN_DL=41000, BANDWIDTH=20,
        SUBCARRIER=15KHz,
        SFFRAME=SF_DL_UL_2_2;

; 配置双模小区参数
MOD DUALMODE: CELLID=0, CELLID1=1,
              DUALMODEEN=1;
```

## 常见问题处理

### 小区激活失败

```
错误: "Cell active failed, hardware alarm"
可能原因:
  1. 基带板未激活
  2. RRU链路故障
  3. 功率超限

处理:
  1. 检查基带板状态: DSP BRD
  2. 检查RRU链路: DSP RRU
  3. 检查天线驻波比: DSP VSW
```

### S1接口故障

```
错误: "S1 link down"
可能原因:
  1. IP地址配置错误
  2. VLAN配置错误
  3. MME连接异常

处理:
  1. 验证IP配置: DSP S1
  2. 检查VLAN: DSP VLAN
  3. 测试MME连通性: PING MME_IP
```

### 邻区配置失败

```
错误: "External cell already exists"
处理:
  RMV EXTCELL: CELLID=100;
  ADD EXTCELL: ... (重新添加)

错误: "Neighbor relation already exists"
处理:
  RMV NRN: SOURCE=0, TARGETCELL=100;
  ADD NRN: ... (重新添加)
```

## 参数检查清单

创建小区前检查：

- [ ] 频点 (EARFCN) 是否在 Band 范围内
- [ ] 带宽 (Bandwidth) 是否支持
- [ ] TAC 是否与 MME 配置一致
- [ ] 邻区 ECGI 是否唯一
- [ ] S1 IP 是否与传输网络可达
- [ ] 功率参数是否在允许范围内

## 注意事项

1. **先配置后激活**：确保所有参数配置完成后再激活小区
2. **备份配置**：重要操作前先备份当前配置
3. **逐步验证**：每步配置后查询状态确认
4. **邻区顺序**：先添加外部小区，再添加邻区关系
5. **功率安全**：确保天线连接正确后再开功率

## 相关 Skill

- `lte-testcase-generator` - LTE 测试用例生成
- `lte-testcase-debugger` - LTE 测试用例调试
