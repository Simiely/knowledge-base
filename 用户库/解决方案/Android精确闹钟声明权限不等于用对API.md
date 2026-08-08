---
tags: [android, alarm, lifecycle]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/meituan-bike-reminder/blob/main/DEVELOPMENT.md
---
# Android 精确闹钟：声明权限 ≠ 用对 API

**TL;DR**：需要「到点准时触发」的提醒，Manifest 声明 `SCHEDULE_EXACT_ALARM` 后还必须 `canScheduleExactAlarms()` 判断 + 显式调 `setExactAndAllowWhileIdle()`；用 `set()`（非精确）在厂商省电策略下会被延迟数分钟。

## 问题
Manifest 声明了 `SCHEDULE_EXACT_ALARM`，但倒计时兜底用了 `AlarmManager.set()`（非精确），厂商省电策略下提醒被延迟数分钟，到点严重不准。

## 根因
声明权限 ≠ 用对 API。精确闹钟要显式调用 `setExactAndAllowWhileIdle`（可穿透 Doze），且 Android 12+ 精确闹钟受管控，需先 `canScheduleExactAlarms()` 判断能力。

## 解决
```kotlin
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && alarm.canScheduleExactAlarms()) {
    alarm.setExactAndAllowWhileIdle(RTC_WAKEUP, triggerAt, pi)   // 精确，可穿透 Doze
} else {
    alarm.setAndAllowWhileIdle(RTC_WAKEUP, triggerAt, pi)       // 降级：近似但能穿透 Doze
    // 引导用户去开「精确闹钟」权限
    startActivity(Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM))
}
```

## 预防
- 所有需要到点准时触发的闹钟/提醒：先判断能力（canScheduleExactAlarms）再选 API，并降级 + 引导
- 三层兜底思路：系统时钟（ACTION_SET_TIMER）→ AlarmManager → 手动设置提示

## 来源
提炼自 [meituan-bike-reminder](https://github.com/Simiely/meituan-bike-reminder)：
[DEVELOPMENT.md ③](https://github.com/Simiely/meituan-bike-reminder/blob/main/DEVELOPMENT.md)（精确闹钟）
