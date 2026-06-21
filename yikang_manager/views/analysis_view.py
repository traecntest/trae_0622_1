"""
颐康管家 - 数据分析视图
利用 Matplotlib 绘制历年指标变化趋势折线图，用户可直观查看
某项指标在过去几年的变化趋势，辅助判断健康走向。
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QGroupBox, QFrame, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.font_manager as fm

from controllers.member_controller import MemberController
from controllers.record_controller import RecordController
from config import NORMAL_RANGES, INDICATOR_CATEGORIES


def _setup_chinese_font():
    """配置 Matplotlib 中文字体，自动注册系统中文字体文件。"""
    import os
    font_files = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for fp in font_files:
        if os.path.exists(fp):
            try:
                fm.fontManager.addfont(fp)
            except Exception:
                pass

    candidates = [
        "WenQuanYi Zen Hei", "WenQuanYi Micro Hei", "Droid Sans Fallback",
        "Noto Sans CJK SC", "SimHei", "Microsoft YaHei", "Arial Unicode MS",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            matplotlib.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            matplotlib.rcParams["axes.unicode_minus"] = False
            return name
    matplotlib.rcParams["axes.unicode_minus"] = False
    return None


_setup_chinese_font()


class TrendChartWidget(FigureCanvas):
    """指标趋势折线图组件。"""

    def __init__(self, parent=None, width=8, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor("#ffffff")
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.setParent(parent)

    def plot_trend(self, dates, values, indicator_name, ref_range, member_name=""):
        """绘制指标趋势折线图。"""
        self.ax.clear()

        valid = [(d, v) for d, v in zip(dates, values) if v is not None]
        if not valid:
            self.ax.text(0.5, 0.5, "暂无数据", ha="center", va="center",
                        transform=self.ax.transAxes, fontsize=16, color="#bdc3c7")
            self.draw_idle()
            return

        plot_dates = [d[:7] for d, _ in valid]
        plot_values = [v for _, v in valid]

        color = "#2980b9"
        self.ax.plot(plot_dates, plot_values, marker="o", markersize=8,
                     linewidth=2.5, color=color, label=indicator_name)

        self.ax.fill_between(plot_dates, plot_values, alpha=0.12, color=color)

        low, high, unit = ref_range
        if low is not None and high is not None and low != high:
            self.ax.axhspan(low, high, alpha=0.1, color="#27ae60", label="正常范围")
            self.ax.axhline(y=low, color="#27ae60", linestyle="--", linewidth=1, alpha=0.5)
            self.ax.axhline(y=high, color="#27ae60", linestyle="--", linewidth=1, alpha=0.5)
        elif low is not None and high is not None and low == high:
            self.ax.axhline(y=low, color="#27ae60", linestyle="--", linewidth=1,
                           alpha=0.5, label="正常值")

        for x, y in zip(plot_dates, plot_values):
            abnormal = (low is not None and high is not None and
                        low != high and (y < low or y > high))
            label_color = "#e74c3c" if abnormal else "#2c3e50"
            self.ax.annotate(f"{y}", (x, y), textcoords="offset points",
                            xytext=(0, 12), ha="center", fontsize=9,
                            color=label_color, fontweight="bold" if abnormal else "normal")
            if abnormal:
                self.ax.plot(x, y, "o", color="#e74c3c", markersize=10, zorder=5)

        title = f"{member_name} - {indicator_name} 趋势" if member_name else f"{indicator_name} 趋势"
        self.ax.set_title(title, fontsize=14, fontweight="bold", color="#1a5276")
        self.ax.set_xlabel("时间", fontsize=11, color="#7f8c8d")
        self.ax.set_ylabel(f"{indicator_name} ({unit})" if unit else indicator_name,
                           fontsize=11, color="#7f8c8d")
        self.ax.legend(loc="best", fontsize=9)
        self.ax.grid(True, alpha=0.3, linestyle="--")
        self.ax.set_facecolor("#fafbfc")

        self.fig.autofmt_xdate(rotation=30)
        self.fig.tight_layout()
        self.draw_idle()


class MultiIndicatorChartWidget(FigureCanvas):
    """多指标对比雷达图组件。"""

    def __init__(self, parent=None, width=6, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor("#ffffff")
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_radar(self, indicators_values, member_name=""):
        """绘制指标状态雷达图（正常率）。"""
        self.fig.clear()
        ax = self.fig.add_subplot(111, polar=True)

        if not indicators_values:
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center",
                    transform=ax.transAxes, fontsize=14, color="#bdc3c7")
            self.draw_idle()
            return

        names = [iv[0] for iv in indicators_values]
        normal_rates = [iv[1] for iv in indicators_values]
        angles = [n / float(len(names)) * 2 * 3.14159265358979 for n in range(len(names))]
        angles += angles[:1]
        normal_rates += normal_rates[:1]

        ax.plot(angles, normal_rates, "o-", linewidth=2, color="#2980b9")
        ax.fill(angles, normal_rates, alpha=0.25, color="#2980b9")
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(names, fontsize=9)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=8, color="#95a5a6")
        title = f"{member_name} - 指标正常率" if member_name else "指标正常率"
        ax.set_title(title, fontsize=13, fontweight="bold", color="#1a5276", pad=20)
        self.fig.tight_layout()
        self.draw_idle()


class AnalysisView(QWidget):
    """数据分析视图。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._member_ctrl = MemberController()
        self._record_ctrl = RecordController()
        self._current_member_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        ctrl_layout = QHBoxLayout()
        ctrl_layout.addWidget(QLabel("成员："))
        self.member_combo = QComboBox()
        self.member_combo.currentIndexChanged.connect(self._on_member_changed)
        ctrl_layout.addWidget(self.member_combo, 1)

        ctrl_layout.addWidget(QLabel("指标："))
        self.indicator_combo = QComboBox()
        self.indicator_combo.currentIndexChanged.connect(self._on_indicator_changed)
        ctrl_layout.addWidget(self.indicator_combo, 1)

        self.refresh_btn = QPushButton("刷新图表")
        self.refresh_btn.setObjectName("PrimaryButton")
        self.refresh_btn.clicked.connect(self._refresh_chart)
        ctrl_layout.addWidget(self.refresh_btn)
        layout.addLayout(ctrl_layout)

        splitter = QSplitter(Qt.Vertical)

        chart_group = QGroupBox("指标趋势分析")
        chart_group.setObjectName("CardBox")
        chart_layout = QVBoxLayout(chart_group)
        self.trend_chart = TrendChartWidget(self, width=8, height=4)
        chart_layout.addWidget(self.trend_chart)
        splitter.addWidget(chart_group)

        bottom_splitter = QSplitter(Qt.Horizontal)

        radar_group = QGroupBox("指标正常率")
        radar_group.setObjectName("CardBox")
        radar_layout = QVBoxLayout(radar_group)
        self.radar_chart = MultiIndicatorChartWidget(self, width=5, height=4)
        radar_layout.addWidget(self.radar_chart)
        bottom_splitter.addWidget(radar_group)

        detail_group = QGroupBox("指标明细")
        detail_group.setObjectName("CardBox")
        detail_layout = QVBoxLayout(detail_group)
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(5)
        self.detail_table.setHorizontalHeaderLabels(
            ["指标", "最新值", "参考范围", "状态", "历史均值"]
        )
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detail_table.setAlternatingRowColors(True)
        self.detail_table.setEditTriggers(QTableWidget.NoEditTriggers)
        detail_layout.addWidget(self.detail_table)
        bottom_splitter.addWidget(detail_group)

        splitter.addWidget(bottom_splitter)
        splitter.setSizes([300, 200])
        layout.addWidget(splitter, 1)

    def refresh(self, member_id=None):
        self._load_members()
        if member_id:
            idx = self.member_combo.findData(member_id)
            if idx >= 0:
                self.member_combo.setCurrentIndex(idx)
        elif self.member_combo.count() > 0:
            self._on_member_changed(0)

    def _load_members(self):
        self.member_combo.blockSignals(True)
        self.member_combo.clear()
        members = self._member_ctrl.get_all_members()
        for m in members:
            self.member_combo.addItem(f"{m.name}（{m.relation}）", m.id)
        self.member_combo.blockSignals(False)
        if members:
            self._on_member_changed(0)

    def _on_member_changed(self, index):
        if index < 0:
            return
        self._current_member_id = self.member_combo.itemData(index)
        self._load_indicators()
        self._refresh_chart()
        self._refresh_radar()
        self._refresh_detail()

    def _load_indicators(self):
        self.indicator_combo.blockSignals(True)
        self.indicator_combo.clear()
        if self._current_member_id:
            names = self._record_ctrl.get_indicator_names(self._current_member_id)
            self.indicator_combo.addItems(names)
        self.indicator_combo.blockSignals(False)

    def _on_indicator_changed(self):
        self._refresh_chart()

    def _refresh_chart(self):
        if not self._current_member_id:
            return
        ind_name = self.indicator_combo.currentText()
        if not ind_name:
            return
        dates, values, ref_range = self._record_ctrl.get_trend_data(
            self._current_member_id, ind_name
        )
        member = self._member_ctrl.get_member(self._current_member_id)
        member_name = member.name if member else ""
        self.trend_chart.plot_trend(dates, values, ind_name, ref_range, member_name)

    def _refresh_radar(self):
        if not self._current_member_id:
            return
        ind_names = self._record_ctrl.get_indicator_names(self._current_member_id)
        indicators_values = []
        for name in ind_names:
            dates, values, ref_range = self._record_ctrl.get_trend_data(
                self._current_member_id, name
            )
            low, high, unit = ref_range
            valid_vals = [v for v in values if v is not None]
            if not valid_vals or low is None or high is None or low == high:
                continue
            normal_count = sum(1 for v in valid_vals if low <= v <= high)
            rate = normal_count / len(valid_vals) if valid_vals else 0
            indicators_values.append((name, rate))
        member = self._member_ctrl.get_member(self._current_member_id)
        member_name = member.name if member else ""
        self.radar_chart.plot_radar(indicators_values, member_name)

    def _refresh_detail(self):
        if not self._current_member_id:
            return
        ind_names = self._record_ctrl.get_indicator_names(self._current_member_id)
        self.detail_table.setRowCount(len(ind_names))
        for i, name in enumerate(ind_names):
            dates, values, ref_range = self._record_ctrl.get_trend_data(
                self._current_member_id, name
            )
            low, high, unit = ref_range
            valid_vals = [v for v in values if v is not None]
            latest = valid_vals[-1] if valid_vals else None
            avg = sum(valid_vals) / len(valid_vals) if valid_vals else None
            ref_str = f"{low}~{high} {unit}" if low is not None and low != high else "—"
            status = "正常"
            if latest is not None and low is not None and high is not None and low != high:
                status = "⚠异常" if (latest < low or latest > high) else "正常"

            self.detail_table.setItem(i, 0, QTableWidgetItem(name))
            self.detail_table.setItem(i, 1, QTableWidgetItem(
                f"{latest} {unit}" if latest is not None else "—"))
            self.detail_table.setItem(i, 2, QTableWidgetItem(ref_str))
            status_item = QTableWidgetItem(status)
            if "异常" in status:
                status_item.setForeground(Qt.red)
            self.detail_table.setItem(i, 3, status_item)
            self.detail_table.setItem(i, 4, QTableWidgetItem(
                f"{avg:.2f}" if avg is not None else "—"))
