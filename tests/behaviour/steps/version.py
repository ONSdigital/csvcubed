from behave import Given

from csvcubed.utils.version import get_csvcubed_version_uri


@Given("the version identifier")
def step_impl(context):
    version_uri = get_csvcubed_version_uri()

    if hasattr(context, "rdf_template_data"):
        context.rdf_template_data["csvcubed_version_identifier"] = version_uri
    else:
        context.rdf_template_data = {"csvcubed_version_identifier": version_uri}
