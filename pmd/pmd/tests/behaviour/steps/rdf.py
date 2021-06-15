import behave.runner
from behave import *


from devtools.behave.rdf import *


@given("some configuration")
def step_impl(context: behave.runner.Context):
    context.turtle = """
        <http://purl.org/dc/terms/modified> <http://www.w3.org/2000/01/rdf-schema#isDefinedBy> <http://purl.org/dc/terms/>.
    """
