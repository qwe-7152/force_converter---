import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


FORCE_UNITS = {
    "N": 1.0,
    "kN": 1000.0,
    "kgf": 9.80665,
    "lbf": 4.4482216152605,
}


def convert_force(value, from_unit, to_unit):
    """Convert a force value between supported units."""
    if value < 0:
        raise ValueError("힘은 음수가 될 수 없습니다.")

    value_in_newtons = value * FORCE_UNITS[from_unit]
    return value_in_newtons / FORCE_UNITS[to_unit]


def main():
    window = tk.Tk()
    window.title("힘 단위 변환기")
    window.geometry("430x320")
    window.resizable(False, False)

    title_label = tk.Label(window, text="힘 단위 변환기", font=("맑은 고딕", 16, "bold"))
    title_label.pack(pady=(20, 12))

    input_frame = tk.Frame(window)
    input_frame.pack()

    unit_names = list(FORCE_UNITS)
    from_unit = tk.StringVar(value="kN")
    to_unit = tk.StringVar(value="N")

    tk.Label(input_frame, text="입력 단위", font=("맑은 고딕", 11)).grid(
        row=0, column=0, padx=(0, 8), pady=5, sticky="e"
    )
    force_entry = tk.Entry(input_frame, width=18, font=("맑은 고딕", 11), justify="right")
    force_entry.grid(row=1, column=1, padx=(0, 8))
    ttk.Combobox(
        input_frame,
        textvariable=from_unit,
        values=unit_names,
        state="readonly",
        width=8,
    ).grid(row=0, column=1, padx=(0, 8), sticky="w")
    tk.Label(input_frame, text="변환할 값", font=("맑은 고딕", 11)).grid(
        row=1, column=0, padx=(0, 8), pady=5, sticky="e"
    )
    tk.Label(input_frame, text="출력 단위", font=("맑은 고딕", 11)).grid(
        row=2, column=0, padx=(0, 8), pady=5, sticky="e"
    )
    ttk.Combobox(
        input_frame,
        textvariable=to_unit,
        values=unit_names,
        state="readonly",
        width=8,
    ).grid(row=2, column=1, padx=(0, 8), sticky="w")
    force_entry.focus_set()

    result_label = tk.Label(
        window,
        text="변환 결과가 여기에 표시됩니다.",
        justify="left",
        font=("맑은 고딕", 11),
        width=30,
        height=3,
        relief="groove",
        anchor="w",
        padx=10,
    )
    result_label.pack(pady=18)

    def convert():
        try:
            value = float(force_entry.get().strip())
            converted_value = convert_force(value, from_unit.get(), to_unit.get())
        except ValueError as error:
            messagebox.showerror("입력 오류", str(error) or "숫자를 입력하세요.")
            force_entry.focus_set()
            force_entry.selection_range(0, tk.END)
            return

        result_label.config(text=f"{value:,.6f} {from_unit.get()} =\n{converted_value:,.6f} {to_unit.get()}")

    def clear():
        force_entry.delete(0, tk.END)
        result_label.config(text="변환 결과가 여기에 표시됩니다.")
        force_entry.focus_set()

    def swap_units():
        current_from_unit = from_unit.get()
        from_unit.set(to_unit.get())
        to_unit.set(current_from_unit)

    button_frame = tk.Frame(window)
    button_frame.pack()
    tk.Button(button_frame, text="변환", width=10, command=convert).grid(
        row=0, column=0, padx=4
    )
    tk.Button(button_frame, text="지우기", width=10, command=clear).grid(
        row=0, column=1, padx=4
    )
    tk.Button(button_frame, text="종료", width=10, command=window.destroy).grid(
        row=0, column=2, padx=4
    )
    tk.Button(button_frame, text="단위 교환", width=10, command=swap_units).grid(
        row=0, column=3, padx=4
    )

    force_entry.bind("<Return>", lambda event: convert())
    window.mainloop()


if __name__ == "__main__":
    main()