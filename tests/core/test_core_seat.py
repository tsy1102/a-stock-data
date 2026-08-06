"""seat_db 席位识别测试（V16.3 E M13: 锁定 keywords_map 精简后的识别行为）。

覆盖三层匹配：
1. tiers 精确匹配（简称）
2. seat_aliases 别名匹配
3. keywords_map 独有兜底（6 个券商+营业部全称变体）
"""
import unittest


class TestIdentifySeatTier(unittest.TestCase):
    """identify_seat_tier 三层匹配行为锁定。"""

    def _identify(self, seat_name):
        from stock_common.seat_db import identify_seat_tier
        return identify_seat_tier(seat_name)

    def test_tiers_exact_match(self):
        # tiers 层：简称直接命中（如"赵老哥"）
        tier, short = self._identify("赵老哥")
        self.assertEqual(short, "赵老哥")

    def test_aliases_match(self):
        # aliases 层：别名命中（真实 alias"拉萨团结路" → 拉萨天团）
        tier, short = self._identify("拉萨团结路")
        self.assertEqual(short, "拉萨天团")

    def test_keywords_unique_match(self):
        # keywords_map 独有兜底：券商+营业部全称变体
        tier, short = self._identify("光大佛山")
        self.assertEqual(short, "佛山无影脚")
        tier, short = self._identify("银河绍兴")
        self.assertEqual(short, "赵老哥")
        tier, short = self._identify("中金财富南京")
        self.assertEqual(short, "小鳄鱼")

    def test_removed_keywords_still_work_via_aliases(self):
        # 已删除的 44 个 keyword 场景仍应被前两层识别（行为不变验证）
        cases = {
            "拉萨": "拉萨天团",
            "炒股养家": "炒股养家",
            "章建平": "章盟主",
            "溧阳路": "孙哥",
            "凯滨路": "呼家楼",
        }
        for seat, expect_short in cases.items():
            tier, short = self._identify(seat)
            self.assertEqual(short, expect_short, f"{seat} 应识别为 {expect_short}")

    def test_unknown_returns_unknown(self):
        tier, short = self._identify("某不知名营业部")
        self.assertEqual(tier, "unknown")
        self.assertEqual(short, "")

    def test_empty_input(self):
        tier, short = self._identify("")
        self.assertEqual(tier, "unknown")
        self.assertEqual(short, "")


if __name__ == "__main__":
    unittest.main()
