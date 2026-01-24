import streamlit as st

from common.actions import QueueActions, HeapActions
from common.types import Step, StepLabelAction, StepLabelValue

_STEP_LABELS: dict[StepLabelAction, StepLabelValue] = {
    QueueActions.INSERT: ("Player added to queue", "green"),
    QueueActions.REMOVE: ("Player removed from queue", "red"),
    QueueActions.ANCHOR: ("Selecting anchor player", "violet"),
    QueueActions.GAME_FOUND: ("Best game found", "green"),
    QueueActions.GAME_NOT_FOUND: ("No valid game found", "orange"),
    HeapActions.INSERT: ("Game added to heap", "blue"),
    HeapActions.REMOVE: ("Game removed from heap", "red"),
}


def _get_step_label(queue_action: QueueActions, heap_action: HeapActions) -> StepLabelValue:
    """
    Get label and color for step type based on actions.
    :param queue_action: The current action performed on the player queue.
    :param heap_action: The current action performed on the game heap.
    :return: A tuple containing the label and color for the step.
    """
    return _STEP_LABELS.get(queue_action) or _STEP_LABELS.get(heap_action) or ("Idle", "gray")


def render(steps: list, current_index: int, is_executing: bool, is_on_final_step: bool) -> None:
    """
    Render status bar showing a brief description of the current step, number of steps and if an async operation is occurring.
    :param steps: List of recorded simulation steps.
    :param current_index: The current step index being displayed.
    :param is_executing: Whether an asynchronous operation is currently executing.
    :param is_on_final_step: Whether the simulation is on the final step.
    """
    total_steps: int = len(steps)
    if is_executing:
        step: Step = steps[current_index] if steps and current_index < len(steps) else None
        if step:
            queue_action: QueueActions = step.queue_snapshot.action if step.queue_snapshot else QueueActions.IDLE
            heap_action: HeapActions = step.heap_snapshot.action if step.heap_snapshot else HeapActions.IDLE
            label, color = _get_step_label(queue_action, heap_action)
            st.markdown(f"**Step {current_index + 1} / {total_steps}** - :{color}[{label}] :blue[(Executing...)]")
        else:
            st.markdown(f"**Executing... {total_steps} steps recorded** - :blue[Polling for updates]")
        st.progress((current_index + 1) / total_steps if total_steps > 0 else 0)
    elif not is_on_final_step and steps:
        step: Step = steps[current_index]
        queue_action: QueueActions = step.queue_snapshot.action if step.queue_snapshot else QueueActions.IDLE
        heap_action: HeapActions = step.heap_snapshot.action if step.heap_snapshot else HeapActions.IDLE
        label, color = _get_step_label(queue_action, heap_action)
        st.markdown(f"**Step {current_index + 1} / {total_steps}** - :{color}[{label}]")
        st.progress((current_index + 1) / total_steps)
    else:
        st.markdown("**Not animating** - Add players or create a match to see visualisation")
        st.progress(0)
