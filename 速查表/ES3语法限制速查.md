---
tags: [ae, es3, javascript]
date: 2026-08-03
status: stable
related: []
---
# ExtendScript ES3 语法红线（AE .jsx）

**TL;DR**：AE 脚本引擎是 ExtendScript（ES3），**不能用** `const` / `let`、模板字符串、箭头函数、`class`。用 `var`、字符串拼接、`function` 声明。

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

## 注意

- 写代码时打开「语法检查」或直接用 ES3 习惯写，避免后期大量返工
- 回调、`.map` 等一律用 `function(){}` 匿名函数
- ScriptUI 布局注意：`alignChildren="fill"` + `edittext alignment="fill"` 叠加会导致宽度失控（参考 解决方案/ 内 scriptui 标签条目）
