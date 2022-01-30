from yearmaps.provider import providers
from yearmaps.utils.util import option_name


# It's difficult to test providers output, so we'll just write some help unittests for provider developers.

def test_no_global_option():
    # "global" is reserved for yearmaps.yml
    for provider in providers:
        command = provider.command
        for param in command.params:
            for opt in param.opts:
                assert option_name(opt) != 'global'
