import gradio as gr
from pathlib import Path
from modules import (
    script_callbacks,
    shared,
    shared_items,
    scripts,
    ui_common,
    sd_models,
)
from modules.ui_settings import create_setting_component
import json
import os

# Webui root path
ROOT_DIR = Path().absolute()


def create_dropdown():
    info = shared.OptionInfo(
        None,
        "Sticky Stable Diffusion checkpoint",
        gr.Dropdown,
        lambda: {"choices": shared_items.list_checkpoint_tiles()},
        refresh=shared_items.refresh_checkpoints,
        infotext="Model hash",
    )

    def fun():
        return info.default

    t = type(info.default)

    args = (
        info.component_args() if callable(info.component_args) else info.component_args
    )

    comp = info.component

    elem_id = f"sticky_checkpoint"

    res = comp(label=info.label, value=fun(), elem_id=elem_id, **(args or {}))
    ui_common.create_refresh_button(
        res, info.refresh, info.component_args, f"refresh_sticky_checkpoint"
    )

    return res

    # modules.scripts.scripts_txt2img


class Script(scripts.Script):
    def __init__(self) -> None:
        super().__init__()

        script_callbacks.on_after_component(self.after_component)

    def title(self):
        return "Sticky Checkpoint"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        self.dropdown = create_dropdown()
        return [self.dropdown]

    def after_component(self, comp, **kwargs):
        if (
            "elem_id" not in kwargs
            or kwargs["elem_id"] != "setting_sd_model_checkpoint"
        ):
            return
        print("after_component", comp, kwargs)

        def change(value):
            return value

        source = comp
        dest = self.dropdown
        source.change(fn=change, inputs=[source], outputs=[dest])
        dest.value = source.value

    def before_process(self, p, dropdown):
        if (
            dropdown is None
            or dropdown == ""
            or dropdown == shared.sd_model.sd_checkpoint_info.title
        ):
            return
        shared.opts.sd_model_checkpoint = dropdown
        sd_models.reload_model_weights()

        # p.sd_model = shared_items.get_checkpoint(shared.opts.sticky_checkpoint)
