"""
Pre-configured JSON Templates
-----------------------------

Functionality to help augment JSON files with configuration from some pre-configured templates.
"""
import json
import logging
from typing import Dict, Any
from csvcubed.utils.cache import session

def apply_preconfigured_values_from_template(column_config: Dict[str, Any], version_module_path: str) -> None:
    # if column_config doesn't have the `from_template` property, just terminate the function now
    if "from_template" not in column_config:
        return
        
    # if column_config has `from_template` property, extract that value
    # remove the `from_template` property
    template_value = column_config["from_template"]
    del column_config["from_template"]

    # given the `from_template` value, look up the template in the git repo
    url =  f"https://raw.githubusercontent.com/GSS-Cogs/csvcubed/main/csvcubed/csvcubed/readers/{version_module_path}/templates/preset_column_config.json"
    url_response = session(url)
    logging.critical(url_response.status_code)
    logging.debug("The template is at: ", url)
   
    
    if url_response.status_code != "200":
        logging.error("Status code: %s. Couldn't retrieve propeties from template at: %s" % (url_response.status_code, url))

    template_file = url_response.json().get(template_value)
    template_url = f"https://raw.githubusercontent.com/GSS-Cogs/csvcubed/main/csvcubed/csvcubed/readers/{version_module_path}/templates/{template_file}"
    template_response = session(template_url)
    logging.critical(template_response)
    if template_response.status_code != "200":
        logging.error("Status code: %s. Couldn't retrieve propeties from template at: %s" % (template_response.status_code, url))

    # insert values frSnto column_config (as long as . Che user hasn't provided an overriding value for them)
    read_template = json.loads(template_response.text) 
    for key in read_template:
        if key not in column_config:
            column_config[key] = read_template[key]
