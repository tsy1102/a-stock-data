#!/usr/bin/env python3
"""tests/test_report_runner.py — BaseReportRunner 单元测试"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_common.sc_report_runner import BaseReportRunner  # 直接导入（内部路径）
from stock_common import BaseReportRunner as BaseReportRunnerPublic  # 公开路径（曾经有 bug）


class DummyReportRunner(BaseReportRunner):
    """测试用 Dummy Runner 类"""

    def __init__(self):
        super().__init__("test_script", "test", "测试报告生成引擎")
        self.pipeline_called = False
        self.upload_called = False

    def execute_pipeline(self):
        self.pipeline_called = True
        return {"status": "ok", "data": [1, 2, 3]}

    def upload_reports(self, drive, folder_id, results):
        self.upload_called = True


class TestBaseReportRunner(unittest.TestCase):
    """BaseReportRunner 逻辑测试"""

    @patch("stock_common.sc_report_runner.parse_args")
    @patch("stock_common.sc_report_runner.init_gd")
    @patch("stock_common.sc_report_runner.cleanup_gd_proxy")
    @patch("stock_common.sc_report_runner.cleanup_tdx")
    def test_runner_execution_flow(self, mock_cleanup_tdx, mock_cleanup_gd, mock_init_gd, mock_parse_args):
        mock_args = MagicMock()
        mock_args.output = "./test_reports_dir"
        mock_args.no_upload = False
        mock_parse_args.return_value = mock_args

        mock_drive = MagicMock()
        mock_init_gd.return_value = (mock_drive, False, "folder_123", False)

        runner = DummyReportRunner()
        res = runner.run()

        self.assertTrue(runner.pipeline_called)
        self.assertTrue(runner.upload_called)
        self.assertEqual(res, {"status": "ok", "data": [1, 2, 3]})
        mock_cleanup_tdx.assert_called_once()
        mock_cleanup_gd.assert_called_once()

        if os.path.exists("./test_reports_dir"):
            os.rmdir("./test_reports_dir")

    @patch("stock_common.sc_report_runner.parse_args")
    @patch("stock_common.sc_report_runner.init_gd")
    def test_runner_no_upload(self, mock_init_gd, mock_parse_args):
        mock_args = MagicMock()
        mock_args.output = "./test_reports_dir"
        mock_args.no_upload = True
        mock_parse_args.return_value = mock_args

        runner = DummyReportRunner()
        res = runner.run()

        self.assertTrue(runner.pipeline_called)
        self.assertFalse(runner.upload_called)
        mock_init_gd.assert_not_called()

        if os.path.exists("./test_reports_dir"):
            os.rmdir("./test_reports_dir")


class TestImportPath(unittest.TestCase):
    """P2-修复验证：公开导入路径应返回同一类"""

    def test_public_import_returns_same_class(self):
        """from stock_common import BaseReportRunner 应能成功并与内部导入相同"""
        self.assertIs(BaseReportRunnerPublic, BaseReportRunner,
                      "stock_common 公开导入的 BaseReportRunner 应与 sc_report_runner 中的相同")

    def test_public_import_is_subclassable(self):
        """via 公开导入的类可正常继承"""
        class _TestChild(BaseReportRunnerPublic):
            def execute_pipeline(self):
                return "test"

        obj = _TestChild("test", "t", "desc")
        self.assertEqual(obj.script_name, "test")


class TestUploadHelpers(unittest.TestCase):
    """V12.5: 验证基类的 upload_single_report / upload_multi_reports 辅助方法"""

    def _make_runner(self):
        runner = DummyReportRunner()
        runner.args = MagicMock()
        runner.args.output = "/tmp"
        return runner

    def test_upload_single_report_success(self):
        """单文件上传成功路径"""
        runner = self._make_runner()
        with patch("stock_common.sc_report_runner.upload_type_reports") as mock_upload:
            mock_upload.return_value = 1
            with patch("os.path.exists", return_value=True):
                ok = runner.upload_single_report(MagicMock(), "folder_1", "/tmp/test.txt")
        self.assertTrue(ok)
        mock_upload.assert_called_once()

    def test_upload_single_report_file_missing(self):
        """单文件上传，文件不存在时应返回 False"""
        runner = self._make_runner()
        with patch("stock_common.sc_report_runner.upload_type_reports") as mock_upload:
            with patch("os.path.exists", return_value=False):
                ok = runner.upload_single_report(MagicMock(), "folder_1", "/tmp/missing.txt")
        self.assertFalse(ok)
        mock_upload.assert_not_called()

    def test_upload_single_report_upload_fails(self):
        """单文件上传，upload_type_reports 返回 0 时应返回 False"""
        runner = self._make_runner()
        with patch("stock_common.sc_report_runner.upload_type_reports") as mock_upload:
            mock_upload.return_value = 0
            with patch("os.path.exists", return_value=True):
                ok = runner.upload_single_report(MagicMock(), "folder_1", "/tmp/test.txt")
        self.assertFalse(ok)

    def test_upload_multi_reports_filters_failures(self):
        """多文件上传应仅处理 status=='成功' 的条目"""
        runner = self._make_runner()
        results = {
            "results": [
                {"code": "000001", "status": "成功", "path": "/tmp/a.txt"},
                {"code": "000002", "status": "数据失败", "path": "/tmp/b.txt"},
                {"code": "000003", "status": "成功", "path": "/tmp/c.txt"},
            ],
            "time_str": "20260722_1000",
            "report_type": "sht",
        }
        with patch("stock_common.sc_report_runner.upload_stock_report_by_code") as mock_upload:
            mock_upload.return_value = True
            with patch.object(runner, "_default_resolve_name", return_value="测试名"):
                runner.upload_multi_reports(MagicMock(), "folder_1", results)
        # 仅 2 个成功条目被上传
        self.assertEqual(mock_upload.call_count, 2)

    def test_upload_multi_reports_marks_failures(self):
        """upload_stock_report_by_code 返回 False 时，应将 status 标记为 'GD上传失败'"""
        runner = self._make_runner()
        results = {
            "results": [
                {"code": "000001", "status": "成功", "path": "/tmp/a.txt"},
            ],
            "time_str": "20260722_1000",
            "report_type": "med",
        }
        with patch("stock_common.sc_report_runner.upload_stock_report_by_code") as mock_upload:
            mock_upload.return_value = False
            with patch.object(runner, "_default_resolve_name", return_value="测试名"):
                runner.upload_multi_reports(MagicMock(), "folder_1", results)
        self.assertEqual(results["results"][0]["status"], "GD上传失败")

    def test_upload_multi_reports_handles_exception(self):
        """上传过程中出现异常时，应将 status 标记为 'GD上传异常'"""
        runner = self._make_runner()
        results = {
            "results": [
                {"code": "000001", "status": "成功", "path": "/tmp/a.txt"},
            ],
            "time_str": "20260722_1000",
            "report_type": "lng",
        }
        with patch("stock_common.sc_report_runner.upload_stock_report_by_code") as mock_upload:
            mock_upload.side_effect = RuntimeError("boom")
            with patch.object(runner, "_default_resolve_name", return_value="测试名"):
                runner.upload_multi_reports(MagicMock(), "folder_1", results)
        self.assertEqual(results["results"][0]["status"], "GD上传异常")

    def test_upload_multi_reports_custom_name_resolver(self):
        """自定义 name_resolver 应当被调用"""
        runner = self._make_runner()
        results = {
            "results": [{"code": "000001", "status": "成功", "path": "/tmp/a.txt"}],
            "time_str": "20260722_1000",
            "report_type": "sht",
        }
        resolver = MagicMock(return_value="自定义名")
        with patch("stock_common.sc_report_runner.upload_stock_report_by_code") as mock_upload:
            mock_upload.return_value = True
            runner.upload_multi_reports(MagicMock(), "folder_1", results, name_resolver=resolver)
        resolver.assert_called_once_with("000001")
        # 确认上传时使用了自定义名
        call_args = mock_upload.call_args
        self.assertEqual(call_args[0][3], "自定义名")  # 第四个位置参数是 q_name


class TestSubclassDuplication(unittest.TestCase):
    """V12.5 P0 回归测试：get_med_report / get_lng_report 不应再定义重复 Runner 类"""

    def test_get_med_report_has_single_runner(self):
        """get_med_report.py 中只允许存在一个 MedReportRunner 类"""
        import ast
        with open("get_med_report.py", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        runners = [node for node in ast.walk(tree)
                   if isinstance(node, ast.ClassDef) and node.name == "MedReportRunner"]
        self.assertEqual(len(runners), 1, f"发现 {len(runners)} 个 MedReportRunner，应为 1 个")

    def test_get_lng_report_has_single_runner(self):
        """get_lng_report.py 中只允许存在一个 LngReportRunner 类"""
        import ast
        with open("get_lng_report.py", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        runners = [node for node in ast.walk(tree)
                   if isinstance(node, ast.ClassDef) and node.name == "LngReportRunner"]
        self.assertEqual(len(runners), 1, f"发现 {len(runners)} 个 LngReportRunner，应为 1 个")

    def test_all_report_scripts_have_single_runner(self):
        """6 大报告脚本每个文件都只允许有 1 个 Runner 类（防退化守护）"""
        import ast
        scripts_and_classes = [
            ("get_val_report.py", "ValReportRunner"),
            ("get_sht_report.py", "ShtReportRunner"),
            ("get_med_report.py", "MedReportRunner"),
            ("get_lng_report.py", "LngReportRunner"),
            ("get_ful_report.py", "FulReportRunner"),
            ("get_mak_report.py", "MakReportRunner"),
        ]
        for script, class_name in scripts_and_classes:
            with open(script, encoding="utf-8") as f:
                tree = ast.parse(f.read())
            runners = [node for node in ast.walk(tree)
                       if isinstance(node, ast.ClassDef) and node.name == class_name]
            self.assertEqual(
                len(runners), 1,
                f"{script} 中发现 {len(runners)} 个 {class_name}，应为 1 个（V12.5 防退化）"
            )


class TestRunnerSubclassInstantiation(unittest.TestCase):
    """V12.5 防退化守护：6 大 Runner 子类应能正常实例化"""

    def _make_runner_class(self, module_name: str, class_name: str):
        """懒加载脚本以避免触发真实网络/数据获取。"""
        import importlib
        import sys
        if module_name not in sys.modules:
            importlib.import_module(module_name)
        return getattr(sys.modules[module_name], class_name)

    def test_all_six_runners_subclass_base(self):
        """6 大 Runner 都应继承 BaseReportRunner。"""
        from stock_common.sc_report_runner import BaseReportRunner
        runners = [
            ("get_val_report", "ValReportRunner"),
            ("get_sht_report", "ShtReportRunner"),
            ("get_med_report", "MedReportRunner"),
            ("get_lng_report", "LngReportRunner"),
            ("get_ful_report", "FulReportRunner"),
            ("get_mak_report", "MakReportRunner"),
        ]
        for module_name, class_name in runners:
            cls = self._make_runner_class(module_name, class_name)
            self.assertTrue(
                issubclass(cls, BaseReportRunner),
                f"{class_name} 必须继承 BaseReportRunner"
            )

    def test_all_six_runners_have_consistent_init(self):
        """6 大 Runner 实例化后应具备一致的属性（script_name, report_type, description）。"""
        runners = [
            ("get_val_report", "ValReportRunner", "val"),
            ("get_sht_report", "ShtReportRunner", "sht"),
            ("get_med_report", "MedReportRunner", "med"),
            ("get_lng_report", "LngReportRunner", "lng"),
            ("get_ful_report", "FulReportRunner", "ful"),
            ("get_mak_report", "MakReportRunner", "mak"),
        ]
        for module_name, class_name, expected_type in runners:
            cls = self._make_runner_class(module_name, class_name)
            instance = cls()
            self.assertTrue(hasattr(instance, "script_name"))
            self.assertTrue(hasattr(instance, "report_type"))
            self.assertTrue(hasattr(instance, "description"))
            self.assertTrue(hasattr(instance, "time_str"))
            self.assertTrue(hasattr(instance, "today_str"))
            self.assertEqual(
                instance.report_type, expected_type,
                f"{class_name}.report_type 应为 '{expected_type}'"
            )


if __name__ == "__main__":
    unittest.main()
