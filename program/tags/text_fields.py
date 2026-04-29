# text_fields.py

from dataclasses import dataclass


@dataclass(frozen=True)
class TextFieldTags:
    sample_parameters: str = 'Sample parametres text tag'
    image_name: str = 'Name of image text tag'
    table_counts: str = 'Table counts text tag'
    mu_s_counter: str = 'Mu_s counter text tag'
    mu_s_filename: str = 'Mu_s filename text tag'
    mu_s_table_counts: str = 'Mu_s table counts text tag'
    mu_s_images_counter: str = 'Mu_s images counter text tag'
    plots_info: str = 'Plots info text tag'
    save_files_info: str = 'Save files info text tag'
    imaging_processing: str = 'Imaging processing text tag'
    save_images_info: str = 'Save images info text tag'
