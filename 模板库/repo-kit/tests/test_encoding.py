"""发行物编码：每个 .ps1 要么纯 ASCII，要么带 BOM。

为什么只测 .ps1：`tools/update-repo-kit.ps1` 声明了 `#Requires -Version 5.1`，
而无 BOM 的 UTF-8 中文脚本在 Windows PowerShell 5.1 下会被按 ANSI 代码页解码。
Microsoft Learn《about_Character_Encoding》的原话是
「if you need to use non-Ascii characters in your scripts, save them as UTF-8 with BOM」，
PSScriptAnalyzer 也有同口径的内置规则 `PSUseBOMForUnicodeEncodedFile`。

实测补充（2026-11-19）：中文全在注释里时 PS 5.1 **通常仍能解析**（解析错误 0 个），
但 `Get-Help` 的帮助文本一定是乱码，而且中文一旦进入字符串就可能真的报语法错误。
所以按最严的口径守：非 ASCII 就必须带 BOM。

为什么不下发给各仓去自查：这个文件在消费仓里同时被 `schema/kit.lock.json` 按字节锁定，
下游「加 BOM」会让 `KIT LOCK: FAIL`。发行物的属性只能在发行方这里保证。
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOM = b"\xef\xbb\xbf"


def offenders(paths, root: Path | None = None) -> list[str]:
    """返回「含非 ASCII 却缺 BOM」的文件名。

    判定分三档，只有第三档算错：
    - 带 BOM            → 任何字节都行（BOM 已声明编码）；
    - 无 BOM 且纯 ASCII → 可以，ANSI 与 UTF-8 对 ASCII 的解码完全一致；
    - 无 BOM 且含非 ASCII → 报。
    """
    bad = []
    for path in paths:
        path = Path(path)
        data = path.read_bytes()
        if data.startswith(BOM):
            continue
        try:
            data.decode("ascii")
        except UnicodeDecodeError:
            bad.append((path.relative_to(root) if root else path).as_posix())
    return bad


class ShippedEncodingTest(unittest.TestCase):
    """真实发行物：仓里现存每份 .ps1 都合规。"""

    def test_ps1_is_ascii_or_has_bom(self):
        files = sorted(ROOT.rglob("*.ps1"))
        # 兜底：rglob 一个都没找到时，下面的断言会因为 bad == [] 而「假绿」。
        self.assertTrue(files, "一个 .ps1 都没找到，说明测试自己失效了")
        bad = offenders(files, ROOT)
        self.assertEqual(
            bad, [],
            "以下 .ps1 含非 ASCII 却缺 BOM（加 3 字节 EF BB BF 即可）：%s" % bad,
        )


class PredicateTest(unittest.TestCase):
    """判定函数本身：两个方向各测一次，防止「规则写反了也全绿」。

    真实发行物里只有一份 .ps1，光靠它测不出「纯 ASCII 是否被误判」——
    所以这里用临时文件把两种合法/非法形态都摆出来。
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def make(self, name: str, data: bytes) -> Path:
        path = self.dir / name
        path.write_bytes(data)
        return path

    def test_ascii_without_bom_is_allowed(self):
        path = self.make("plain.ps1", b"Write-Output 'hi'\r\n")
        self.assertEqual(offenders([path]), [])

    def test_non_ascii_with_bom_is_allowed(self):
        path = self.make("bom.ps1", BOM + "Write-Output '中文'\r\n".encode("utf-8"))
        self.assertEqual(offenders([path]), [])

    def test_non_ascii_without_bom_is_rejected(self):
        path = self.make("bad.ps1", "Write-Output '中文'\r\n".encode("utf-8"))
        self.assertEqual(offenders([path]), [path.as_posix()])


if __name__ == "__main__":
    unittest.main()
