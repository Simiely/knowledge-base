---
tags: [ae, audio, expression]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/AudioScale/blob/main/DEVELOPMENT.md
---
# AE 音频驱动图层方案

**TL;DR**：ExtendScript **没有 API 直接读音频采样**——用 AE 内置命令 `Convert Audio to Keyframes` 把振幅烘焙成 Slider 关键帧，脚本只调度命令 + 挂表达式。表达式引擎**不能做 FFT**：频段分离用「复制 N 个音频层 + 各自 Bass & Treble 滤波 + 分别烘焙」，目标层 `index % bandCount` 轮询分配。

## 音频获取（烘焙方案）

```javascript
// 1. 调用 AE 内置命令（提供中英文菜单名候选）
app.executeCommand(...);  // Convert Audio to Keyframes
// 2. 找生成的 Audio Amplitude 层：diff 前后图层引用（不靠名字，跨语言安全）
// 3. 表达式读振幅：effect(3)(1) 索引
```

- **约束**：烘焙的关键帧是"死的"——**替换音频后必须重跑脚本**，无实时方案

## 频段分离（复制 + 离线滤波）

1. 复制 N 个音频层
2. 每层加不同增益的 `Bass & Treble` 效果（粗略分频：低/中/高）
3. 各自烘焙成独立 Audio Amplitude 图层
4. 目标层按 `index % bandCount` 轮询分配（如低频驱动文字、高频驱动粒子）

- **代价**：图层数 ×N，工程体积和烘焙时间线性增长
- **更精确**：可换 `Parametric EQ` 设置频率/带宽

## 预防

- 需要"音频反应"动画时，优先考虑烘焙关键帧方案，不要试图在表达式里实时解析音频
- 分频需求先想清楚精度要求：粗略用 Bass & Treble，精确用 Parametric EQ
- 烘焙层跨语言识别用 diff 引用（见 AE表达式跨语言兼容条目）
