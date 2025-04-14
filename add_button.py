from aqt import gui_hooks

BUTTON_ID = "my_custom_button"


def add_my_button(buttons, editor):
    buttons.append(BUTTON_ID)


gui_hooks.editor_did_init_buttons.append(add_my_button)
