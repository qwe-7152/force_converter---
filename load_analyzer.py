import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


CSV_PATH = Path(__file__).with_name("load_data.csv")
RESULT_PATH = Path(__file__).with_name("load_result.csv")
PLOT_PATH = Path(__file__).with_name("stress_plot.png")
AREA_MM2 = 100.0
REFERENCE_STRESS_MPA = 6.0
EXPECTED_FIELDS = ["time_s", "force_N"]


def read_measurements(
    csv_path: Path = CSV_PATH,
) -> tuple[list[tuple[float, float]], list[tuple[int, str, str]]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames != EXPECTED_FIELDS:
            raise ValueError(
                f"CSV 열 이름은 {EXPECTED_FIELDS}이어야 합니다. "
                f"현재 열 이름: {reader.fieldnames}"
            )

        measurements = []
        invalid_rows = []
        for row_number, row in enumerate(reader, start=2):
            time_value = row.get("time_s", "")
            force_value = row.get("force_N", "")
            row_is_valid = True
            for field_name, value in (
                ("time_s", time_value),
                ("force_N", force_value),
            ):
                try:
                    float(value)
                except (TypeError, ValueError):
                    invalid_rows.append((row_number, field_name, value or ""))
                    row_is_valid = False

            if not row_is_valid:
                continue

            time_s = float(time_value)
            force_n = float(force_value)
            measurements.append((time_s, force_n))

    return measurements, invalid_rows


def main() -> None:
    measurements, invalid_rows = read_measurements()
    for row_number, field_name, value in invalid_rows:
        print(
            f"제외한 원본 CSV {row_number}행: "
            f"{field_name} 문제값={value!r}"
        )

    excluded_row_count = len({row_number for row_number, _, _ in invalid_rows})
    print(f"제외한 행 수: {excluded_row_count}개")
    print(f"유효한 데이터 수: {len(measurements)}개")
    if not measurements:
        print("유효한 데이터가 없어 계산과 그래프 생성을 중단합니다.")
        return

    maximum_time_s, maximum_force_n = max(measurements, key=lambda item: item[1])
    results = [
        (time_s, force_n, force_n / AREA_MM2)
        for time_s, force_n in measurements
    ]
    maximum_stress_time_s, _, maximum_stress_mpa = max(
        results, key=lambda item: item[2]
    )
    above_reference_count = sum(
        stress_mpa > REFERENCE_STRESS_MPA
        for _, _, stress_mpa in results
    )

    with RESULT_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["time_s", "force_N", "stress_MPa"])
        writer.writerows(results)

    time_values = [time_s for time_s, _, _ in results]
    stress_values = [stress_mpa for _, _, stress_mpa in results]
    plt.plot(time_values, stress_values, marker="o")
    plt.scatter(
        [maximum_stress_time_s],
        [maximum_stress_mpa],
        color="red",
        zorder=3,
    )
    plt.annotate(
        f"{maximum_stress_mpa:g} MPa",
        (maximum_stress_time_s, maximum_stress_mpa),
        xytext=(8, 8),
        textcoords="offset points",
    )
    plt.xlabel("Time (s)")
    plt.ylabel("Stress (MPa)")
    plt.tight_layout()
    plt.savefig(PLOT_PATH)
    plt.close()

    print(f"데이터 개수: {len(measurements)}개")
    print(f"최대 하중: {maximum_force_n:g} N")
    print(f"최대 하중 해당 시간: {maximum_time_s:g} s")
    print(f"최대 응력: {maximum_stress_mpa:g} MPa")
    print(f"최대 응력 해당 시간: {maximum_stress_time_s:g} s")
    print(
        f"기준 응력({REFERENCE_STRESS_MPA:g} MPa) 초과 데이터 개수: "
        f"{above_reference_count}개"
    )


if __name__ == "__main__":
    main()
