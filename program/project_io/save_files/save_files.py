# project_io/save_files.py


import dearpygui.dearpygui as dpg
from pathlib import Path
import numpy as np
from ...tags import TAGS
from ...state import STATE
from .utilities import save_csv, get_selected_fields, to_npz_safe
from .csv_collector import collect_boundaries_csv, collect_mu_s_csv, collect_av_int_csv, save_params_csv
from .raw_collector import save_boundaries_raw_npz



def save_files_dialog_show():
    if (dpg.get_value(TAGS.checkboxes.boundaries) or dpg.get_value(TAGS.checkboxes.mu_s) or
            dpg.get_value(TAGS.checkboxes.av_int) or dpg.get_value(TAGS.checkboxes.params)):
        dpg.show_item(TAGS.dialogs.save_files_to_project)
    else:
        return


def save_selected_tables(sender, app_data):
    # --------------------------------------------------
    # 1. Подготовка
    # --------------------------------------------------
    save_dir = Path(app_data["file_path_name"])
    save_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(STATE.project.fs.octp_file).stem

    time_list = (
        STATE.time.time_list
        if STATE.time.time_list
        else list(range(len(STATE.tables.boundaries)))
    )

    dpg.set_value(
        TAGS.text_fields.save_files_info,
        "\tSaving in progress..."
    )

    # --------------------------------------------------
    # 2. Boundaries
    # --------------------------------------------------
    if dpg.get_value(TAGS.checkboxes.boundaries):
        fields = get_selected_fields(
            TAGS.checkboxes.boundaries,
            TAGS.checkboxes.all_boundaries,
            TAGS.boundaries_checkboxes
        )
        print('Fields:', fields)
        print(STATE.tables.boundaries)
        # CSV (только статистика)
        rows = collect_boundaries_csv(
            STATE.tables.boundaries,
            time_list,
            fields
        )
        save_csv(rows, save_dir / f"{stem}_boundaries.csv")

        # NPZ (raw)
        save_boundaries_raw_npz(
            STATE.tables.boundaries,
            save_dir / f"{stem}_boundaries_raw.npz",
            fields
        )

    # --------------------------------------------------
    # 3. mu_s
    # --------------------------------------------------
    if dpg.get_value(TAGS.checkboxes.mu_s):
        fields = get_selected_fields(
            enabled_checkbox=TAGS.checkboxes.mu_s,
            all_checkbox=TAGS.checkboxes.all_mu_s,
            fields_checkboxes=TAGS.mu_s_checkboxes
        )

        # CSV — агрегаты
        csv_fields = [f for f in fields if f != "raw"]
        if csv_fields:
            rows = collect_mu_s_csv(
                STATE.tables.mu_s,
                time_list,
                csv_fields
            )
            save_csv(
                rows,
                save_dir / f"{stem}_mu_s.csv"
            )

        # NPZ — raw
        if "raw" in fields:
            raw_mu_s = {
                f"mu_s_raw_{i}": to_npz_safe(row["raw_mu_s_data"])
                for i, row in enumerate(STATE.tables.mu_s)
                if "raw_mu_s_data" in row
            }

            if raw_mu_s:
                np.savez(
                    save_dir / f"{stem}_mu_s_raw.npz",
                    **raw_mu_s
                )

    # --------------------------------------------------
    # 4. Average intensity
    # --------------------------------------------------
    if dpg.get_value(TAGS.checkboxes.av_int):
        fields = get_selected_fields(
            enabled_checkbox=TAGS.checkboxes.av_int,
            all_checkbox=TAGS.checkboxes.all_av_int,
            fields_checkboxes=TAGS.av_int_checkboxes
        )
        print(STATE.tables.av_int)
        # CSV — агрегаты
        csv_fields = [f for f in fields if f != "raw"]
        if csv_fields:
            rows = collect_av_int_csv(
                STATE.tables.av_int,
                time_list,
                csv_fields
            )
            save_csv(
                rows,
                save_dir / f"{stem}_av_int.csv"
            )

        # NPZ — raw
        if "raw" in fields:
            raw_int = {
                f"av_int_raw_{i}": to_npz_safe(row["raw_intensity_data"])
                for i, row in enumerate(STATE.tables.av_int)
                if "raw_intensity_data" in row
            }

            if raw_int:
                np.savez(
                    save_dir / f"{stem}_av_int_raw.npz",
                    **raw_int
                )

    # --------------------------------------------------
    # 5. Params
    # --------------------------------------------------
    if dpg.get_value(TAGS.checkboxes.params):
        params_dict = {
            "phi": dpg.get_value(TAGS.inputs.phi_0),
            "tau_w": dpg.get_value(TAGS.inputs.tau_w),
            "tau_g": dpg.get_value(TAGS.inputs.tau_g),
        }

        save_params_csv(
            params_dict,
            save_dir / f"{stem}_params.csv"
        )

    # --------------------------------------------------
    # 6. Завершение
    # --------------------------------------------------
    STATE.settings.last_save_folder_for_files = str(save_dir)
    STATE.settings.save()

    dpg.configure_item(
        TAGS.dialogs.save_files_to_project,
        default_path=STATE.settings.last_save_folder_for_files
    )

    dpg.set_value(
        TAGS.text_fields.save_files_info,
        f"\tFiles are saved in {save_dir}"
    )