import time
import random
import datetime
from typing import List, Tuple
import gradio as gr

print("Program started at:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Selection sort code
ALGO_CODE = [
    "for i in range(n):                                           #Iterate through each index of the list",
    "    min_idx = i                                               #Assume the current index is the minimum",
    "    for j in range(i + 1, n):                              #Check the rest of the list after index i",
    "        if a[j] < a[min_idx]:                               #If a smaller element is found",
    "            min_idx = j                                       #Update min_idx to the new minimum element's index",
    "    if min_idx != i:                                          #If the minimum is not already at position i",
    "        a[i], a[min_idx] = a[min_idx], a[i]          #Swap the current element with the found minimum",
]
#Action state mapping
LINE_MAP = {
    "start_i": 0,
    "set_min": 1,
    "compare": 2,
    "if_check": 3,
    "new_min": 4,
    "swap": 6,
}


def highlight_code(active_line: int) -> str:
    """
    Render the code as HTML with one active line highlighted.
    """
    html_lines = []
    for idx, line in enumerate(ALGO_CODE):
        if idx == active_line:
            html_lines.append(
                f'<div style="background:#f587ce; padding:5px; border-radius:5px; font-family:monospace;">{line}</div>'
            )
        else:
            html_lines.append(
                f'<div style="padding:5px; font-family:monospace;">{line}</div>'
            )
    return "<pre>" + "\n".join(html_lines) + "</pre>"


# ----------------------------------------------------------------
# Selection Sort + detailed step capture
def selection_sort_steps(a: List[int]):
    steps = []
    arr = a[:]
    n = len(arr)

    for i in range(n):
        steps.append((i, i, arr[:], None, "start_i"))

        for j in range(i + 1, n):
            # Highlight the IF check line
            steps.append((i, i, arr[:], j, "if_check"))

            if arr[j] < arr[i]:
                steps.append((i, j, arr[:], j, "new_min"))

        # Find min index manually (same logic as above)
        min_idx = min(range(i, n), key=lambda k: arr[k])

        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            steps.append((i, min_idx, arr[:], None, "swap"))

    return steps

# Use HTML to show the array
def render_list_html(a: List[int], i: int, min_idx: int, j: int | None) -> str:
    parts = []

    for idx, val in enumerate(a):
        labels = []
        if idx == i:
            labels.append("i")
        if idx == min_idx:
            labels.append("min")
        if j is not None and idx == j:
            labels.append("j")

        label = ",".join(labels)

        style = (
            "padding:8px 12px; margin:4px; border-radius:20px; "
            "font-family:monospace; font-size:21px;"
        )

        if label:
            style += "border:2px solid #333;"
        else:
            style += "border:1px solid #aaa;"

        parts.append(f'<span style="{style}">{val}<sub>{label}</sub></span>')

    return "<div>" + "".join(parts) + "</div>"

# do animation by the state machine
def animate_selection_sort(nums_str: str, speed: float):
    arr = [int(x.strip()) for x in nums_str.split(",") if x.strip()]
    steps = selection_sort_steps(arr)

    for step_num, (i, min_idx, snapshot, j, action) in enumerate(steps, 1):
        active_line = LINE_MAP.get(action, -1)

#explain each steps
        if action == "start_i":
            explanation = (
                f"Step {step_num}: Starting outer loop at i = {i}. "
                "We now search for the smallest value from index i to the end, "
                "and place it in position i."
            )

        elif action == "if_check":
            explanation = (
                f"Step {step_num}: Comparing a[j] (j={j}, value={snapshot[j]}) "
                f"with current minimum a[min_idx] (index={min_idx}, value={snapshot[min_idx]})."
            )

        elif action == "new_min":
            explanation = (
                f"Step {step_num}: A new minimum was found at j = {j} "
                f"(value={snapshot[j]}). We update min_idx to {j}."
            )

        elif action == "swap":
            explanation = (
                f"Step {step_num}: Swapping a[i] (index {i}, value {snapshot[min_idx]}) "
                f"with the smallest value found (index {min_idx}). "
                "This places the correct element into its final sorted position."
            )

        else:
            explanation = f"Step {step_num}"

        array_html = render_list_html(snapshot, i, min_idx, j)
        code_html = highlight_code(active_line)

        # Yield: description + array visual + code + i/j/min values
        yield explanation, array_html, code_html, str(i), str(j), str(min_idx)

        time.sleep(speed)

#generate random list
def generate_random_list():
    nums = [random.randint(1, 20) for _ in range(6)]
    return ", ".join(map(str, nums))

#Gradio App
with gr.Blocks() as demo:
    gr.Markdown("## Let's Learn Selection Sort!")

    with gr.Row():
        input_box = gr.Textbox(
            label="Input List",
            value=generate_random_list(),
            interactive=True,
        )
        random_btn = gr.Button("Generate Random Numbers")

    speed_slider = gr.Slider(
        label="Animation Speed (seconds per step)",
        minimum=0.1,
        maximum=2.0,
        value=0.6,
        step=0.1,
    )

    run_button = gr.Button("Run Selection Sort")
    status_out = gr.Textbox(label="Current Step", interactive=False)
    html_array = gr.HTML(label="Array Visualization")
    code_view = gr.HTML(label="Running Code (Highlighted)")

    with gr.Row():
        i_box = gr.Textbox(label="i", value="", interactive=False)
        j_box = gr.Textbox(label="j", value="", interactive=False)
        min_box = gr.Textbox(label="min", value="", interactive=False)

    random_btn.click(
        fn=lambda: generate_random_list(),
        inputs=[],
        outputs=[input_box],
    )

    run_button.click(
        animate_selection_sort,
        inputs=[input_box, speed_slider],
        outputs=[status_out, html_array, code_view, i_box, j_box, min_box],
    )


if __name__ == "__main__":
    demo.launch()