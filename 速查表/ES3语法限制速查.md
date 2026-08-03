---
tags: [ae, es3, javascript]
date: 2026-08-03
status: stable
related: []
---
# ExtendScript ES3 语法红线（AE .jsx）

**TL;DR**：AE 脚本引擎是 ExtendScript（ES3），**不能用** `const` / `let`、模板字符串、箭头函数、`class`、**也没有内置 `JSON` 对象**。用 `var`、字符串拼接、`function` 声明；做持久化先注入 JSON polyfill。

## 可用

| 语法 | 示例 |
|---|---|
| `var` 声明 | `var a = 1;` |
| 字符串拼接 | `"a" + b` |
| 函数声明 | `function f(x) { return x; }` |
| 数组/对象字面量 | `[1,2]`、`{k: 1}` |
| try/catch | 标准写法 |

## 禁用（会报错）

| 语法 | 报错示例 |
|---|---|
| `const` / `let` | `Unexpected token` |
| 模板字符串 `` `...` `` | `Unexpected token` |
| 箭头函数 `=>` | `Unexpected token` |
| `class` | `Unexpected token` |
| 展开运算符 `...` | 部分版本不支持 |

## JSON 对象（重点坑）

ExtendScript 引擎**没有内置 `JSON`**，`JSON.stringify()` 直接 `ReferenceError: "JSON" is not defined`。做文件/设置持久化前必须注入 polyfill：

```javascript
if (typeof JSON === "undefined") { JSON = {}; }
if (typeof JSON.stringify !== "function") {
    JSON.stringify = function(obj) { /* 手动序列化 string/number/bool/array/object */ };
}
if (typeof JSON.parse !== "function") {
    JSON.parse = function(text) { return eval("(" + text + ")"); };
}
```

> 注意：`JSON.parse` 用 `eval` 实现（ES3 环境安全），polyfill 需在存储模块前注入。

## 其他注意

- 写代码时用 `node --check 脚本.jsx` 做语法检查（Node 验证 ES3 语法，不能运行 AE API）
- 回调、`.map` 等一律用 `function(){}` 匿名函数
