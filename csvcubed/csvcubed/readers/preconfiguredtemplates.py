"""
Pre-configured JSON Templates
-----------------------------

Functionality to help augment JSON files with configuration from some pre-configured templates.
"""
import logging

from typing import Dict, Any
from requests.exceptions import JSONDecodeError

from csvcubed.utils.cache import session

def get_template_file_from_template_lookup(template_value: str, version_module_path: str) -> str:
    """
    Given the `from_template` value, look up the template in the git repo
    """

    template_lookup_url =  f"https://raw.githubusercontent.com/GSS-Cogs/csvcubed/main/csvcubed/csvcubed/readers/{version_module_path}/templates/preset_column_config.json"
    template_lookup_response = session.get(template_lookup_url)
    logging.debug("The template is at: %s", template_lookup_url)
   
    if template_lookup_response.status_code != 200:
        logging.warning("Status code: %s.", template_lookup_response.status_code)

    try:
        template_lookup = template_lookup_response.json()
    except JSONDecodeError as e:
        raise Exception(f"Could not access template lookup file at {template_lookup_url}") from e

    template_file = template_lookup.get(template_value)

    return template_file


def get_propeties_from_template_file(template_file: str, version_module_path: str) -> dict:
    """
    Given the file path to the template, read in all the propeties of that particular template
    """
    template_template_lookup_url = f"https://raw.githubusercontent.com/GSS-Cogs/csvcubed/main/csvcubed/csvcubed/readers/{version_module_path}/templates/{template_file}"
    template_response = session.get(template_template_lookup_url)
    logging.critical(template_response)
    if template_response.status_code != 200:
        logging.warning("Status code: %s.", template_response.status_code)

    try:
        fetch_template = template_response.json() 
    except JSONDecodeError as e:
        raise Exception(f"Could not access template at {template_template_lookup_url}") from e

    return fetch_template


def apply_preconfigured_values_from_template(column_config: Dict[str, Any], version_module_path: str) -> None:
    """
    Preset templates are found through template lookup file. Propeties are then taken from templates and 
    added to column config, with user specified propeties overriding template propeties.
    """
    # if column_config doesn't have the `from_template` property, just terminate the function now
    if "from_template" not in column_config:
        return
        
    # if column_config has `from_template` property, extract that value
    # remove the `from_template` property
    template_value = column_config["from_template"]
    del column_config["from_template"]

    # given the `from_template` value, look up the template in the git repo
    template_file = get_template_file_from_template_lookup(template_value, version_module_path)

    # given the file path to the template, read in all the propeties of that particular template
    fetch_template = get_propeties_from_template_file(template_file, version_module_path)

    # insert values from column_config (as long as the user hasn't provided an overriding value for them)
    for propety in fetch_template:
        if propety not in column_config:
            column_config[propety] = fetch_template[propety]
    