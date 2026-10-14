import math
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from load_analyzer import read_measurements


class LoadAnalyzerGui:
    def __init__(self, window: tk.Tk) -> None:
        self.window = window
        self.window.title("하중 분석기")
        self.window.geometry("800x560")
        self.window.minsize(640, 420)

        self.path_var = tk.StringVar()
        self.count_var = tk.StringVar(value="유효한 데이터 수: -")
        self.section_type_var = tk.StringVar(value="사각형")
        self.area_var = tk.StringVar(value="단면적 A = - mm²")
        self.result_var = tk.StringVar(value="최대 응력: -\n최대 응력 해당 시간: -")
        self.measurements: list[tuple[float, float]] = []
        self.dimension_vars: dict[str, tk.StringVar] = {}
        self.dimension_frame: ttk.Frame

        self._build_controls()
        self._build_plot()

    def _build_controls(self) -> None:
        file_frame = ttk.Frame(self.window, padding=(12, 12, 12, 6))
        file_frame.pack(fill=tk.X)

        ttk.Button(
            file_frame,
            text="CSV 찾아보기",
            command=self._select_csv,
        ).pack(side=tk.LEFT)
        ttk.Entry(
            file_frame,
            textvariable=self.path_var,
            state="readonly",
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        ttk.Label(
            self.window,
            textvariable=self.count_var,
            padding=(12, 0, 12, 6),
        ).pack(anchor=tk.W)

        section_frame = ttk.LabelFrame(
            self.window,
            text="단면 설정",
            padding=(12, 8, 12, 8),
        )
        section_frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        ttk.Label(section_frame, text="단면 종류").grid(
            row=0, column=0, padx=(0, 6), sticky=tk.W
        )
        section_type_combo = ttk.Combobox(
            section_frame,
            textvariable=self.section_type_var,
            values=("사각형", "원형봉", "원형관", "사각형관", "H형강"),
            state="readonly",
            width=10,
        )
        section_type_combo.grid(row=0, column=1, padx=(0, 12), sticky=tk.W)
        section_type_combo.bind("<<ComboboxSelected>>", self._on_section_type_changed)

        self.dimension_frame = ttk.Frame(section_frame)
        self.dimension_frame.grid(row=0, column=2, columnspan=4, sticky=tk.W)
        self._build_dimension_inputs()

        ttk.Label(section_frame, textvariable=self.area_var).grid(
            row=0, column=6, padx=(12, 12), sticky=tk.W
        )
        ttk.Button(
            section_frame,
            text="분석",
            command=self._analyze,
        ).grid(row=0, column=7, sticky=tk.E)

        ttk.Label(
            self.window,
            textvariable=self.result_var,
            padding=(12, 0, 12, 8),
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

    def _on_section_type_changed(self, _event: tk.Event) -> None:
        self._build_dimension_inputs()

    def _build_dimension_inputs(self) -> None:
        for child in self.dimension_frame.winfo_children():
            child.destroy()

        dimension_labels = {
            "사각형": (("b", "폭 b"), ("h", "높이 h")),
            "원형봉": (("d", "직경 d"),),
            "원형관": (("D", "외경 D"), ("d", "내경 d")),
            "사각형관": (
                ("B", "외부 폭 B"),
                ("H", "외부 높이 H"),
                ("t", "두께 t"),
            ),
            "H형강": (
                ("B", "플랜지 폭 B"),
                ("H", "전체 높이 H"),
                ("tf", "플랜지 두께 tf"),
                ("tw", "웹 두께 tw"),
            ),
        }[self.section_type_var.get()]
        self.dimension_vars = {
            key: tk.StringVar() for key, _ in dimension_labels
        }
        for column, (key, label_text) in enumerate(dimension_labels):
            ttk.Label(self.dimension_frame, text=f"{label_text} (mm)").grid(
                row=0, column=column * 2, padx=(0, 4), sticky=tk.W
            )
            ttk.Entry(
                self.dimension_frame,
                textvariable=self.dimension_vars[key],
                width=8,
            ).grid(row=0, column=column * 2 + 1, padx=(0, 10), sticky=tk.W)

    def _build_plot(self) -> None:
        plot_frame = ttk.Frame(self.window, padding=(12, 0, 12, 12))
        plot_frame.pack(fill=tk.BOTH, expand=True)

        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Stress (MPa)")
        self.axes.grid(True, alpha=0.3)
        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _select_csv(self) -> None:
        selected_path = filedialog.askopenfilename(
            title="하중 CSV 파일 선택",
            filetypes=(("CSV 파일", "*.csv"), ("모든 파일", "*.*")),
        )
        if not selected_path:
            return

        csv_path = Path(selected_path)
        try:
            measurements, invalid_rows = read_measurements(csv_path)
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror("CSV 읽기 오류", str(error))
            return

        self.path_var.set(str(csv_path))
        self.count_var.set(f"유효한 데이터 수: {len(measurements)}개")
        self.measurements = measurements
        self.result_var.set("최대 응력: -\n최대 응력 해당 시간: -")
        self._draw_measurements([])

        if invalid_rows:
            excluded_row_count = len({row_number for row_number, _, _ in invalid_rows})
            messagebox.showwarning(
                "일부 데이터 제외",
                f"유효하지 않은 값이 있는 {excluded_row_count}개 행을 제외했습니다.",
            )

        if not measurements:
            messagebox.showwarning(
                "유효한 데이터 없음",
                "그래프에 표시할 유효한 데이터가 없습니다.",
            )

    def _analyze(self) -> None:
        if not self.measurements:
            messagebox.showerror("분석 오류", "먼저 유효한 CSV 파일을 선택하세요.")
            return

        try:
            dimensions = {
                key: float(variable.get().strip())
                for key, variable in self.dimension_vars.items()
            }
        except ValueError:
            messagebox.showerror("단면 입력 오류", "모든 치수를 숫자로 입력하세요.")
            return

        if any(not math.isfinite(value) or value <= 0 for value in dimensions.values()):
            messagebox.showerror(
                "단면 입력 오류",
                "모든 치수는 0보다 큰 유한한 숫자여야 합니다.",
            )
            return

        try:
            area_mm2 = self._calculate_area(dimensions)
        except ValueError as error:
            messagebox.showerror("단면 입력 오류", str(error))
            return

        self.area_var.set(f"단면적 A = {area_mm2:g} mm²")
        stress_measurements = [
            (time_s, force_n / area_mm2)
            for time_s, force_n in self.measurements
        ]
        maximum_time_s, maximum_stress_mpa = max(
            stress_measurements,
            key=lambda item: item[1],
        )
        self.result_var.set(
            f"최대 응력: {maximum_stress_mpa:g} MPa\n"
            f"최대 응력 해당 시간: {maximum_time_s:g} s"
        )
        self._draw_measurements(stress_measurements)

    def _calculate_area(self, dimensions: dict[str, float]) -> float:
        section_type = self.section_type_var.get()
        if section_type == "사각형":
            return dimensions["b"] * dimensions["h"]
        if section_type == "원형봉":
            return math.pi * dimensions["d"] ** 2 / 4
        if section_type == "원형관":
            if dimensions["D"] <= dimensions["d"]:
                raise ValueError("원형관은 외경 D가 내경 d보다 커야 합니다.")
            return math.pi * (dimensions["D"] ** 2 - dimensions["d"] ** 2) / 4
        if section_type == "사각형관":
            if 2 * dimensions["t"] >= min(dimensions["B"], dimensions["H"]):
                raise ValueError("사각형관은 두께 t의 2배가 외부 폭과 높이보다 작아야 합니다.")
            return (
                dimensions["B"] * dimensions["H"]
                - (dimensions["B"] - 2 * dimensions["t"])
                * (dimensions["H"] - 2 * dimensions["t"])
            )
        if section_type == "H형강":
            if 2 * dimensions["tf"] >= dimensions["H"]:
                raise ValueError("H형강은 플랜지 두께의 2배가 전체 높이보다 작아야 합니다.")
            if dimensions["tw"] >= dimensions["B"]:
                raise ValueError("H형강은 웹 두께가 플랜지 폭보다 작아야 합니다.")
            return (
                2 * dimensions["B"] * dimensions["tf"]
                + (dimensions["H"] - 2 * dimensions["tf"]) * dimensions["tw"]
            )
        raise ValueError(f"지원하지 않는 단면 종류입니다: {section_type}")

    def _draw_measurements(self, measurements: list[tuple[float, float]]) -> None:
        self.axes.clear()
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Stress (MPa)")
        self.axes.grid(True, alpha=0.3)

        if measurements:
            time_values, stress_values = zip(*measurements)
            self.axes.plot(time_values, stress_values, marker="o")

        self.figure.tight_layout()
        self.canvas.draw()


def main() -> None:
    window = tk.Tk()
    LoadAnalyzerGui(window)
    window.mainloop()


if __name__ == "__main__":
    main()
