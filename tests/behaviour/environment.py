from behave import fixture

from csvcubed import feature_flags


@fixture
def set_env_vars(context):
    feature_flags.ATTRIBUTE_VALUE_CODELISTS = True
    context.feature_flag = feature_flags.ATTRIBUTE_VALUE_CODELISTS
