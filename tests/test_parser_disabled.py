import os
import tempfile
import pytest
from parser import PanoramaXMLParser


def _build_config(disabled_value=None):
    disabled_tag = ""
    if disabled_value is not None:
        disabled_tag = f"<disabled>{disabled_value}</disabled>"

    return f"""<config>
  <devices>
    <entry name="localhost.localdomain">
      <device-group>
        <entry name="dg1">
          <pre-rulebase>
            <security>
              <rules>
                <entry name="test-rule">
                  <from><member>trust</member></from>
                  <to><member>untrust</member></to>
                  <source><member>any</member></source>
                  <destination><member>any</member></destination>
                  <application><member>any</member></application>
                  <service><member>any</member></service>
                  <action>allow</action>
                  {disabled_tag}
                </entry>
              </rules>
            </security>
          </pre-rulebase>
        </entry>
      </device-group>
    </entry>
  </devices>
</config>"""


def _parse_rule(disabled_value=None):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(_build_config(disabled_value))
        path = f.name

    try:
        parser = PanoramaXMLParser(path)
        rules = parser.get_device_group_security_rules("dg1", "pre")
        assert len(rules) == 1
        return rules[0]
    finally:
        os.unlink(path)


def test_disabled_tag_missing_means_enabled():
    rule = _parse_rule(disabled_value=None)
    assert rule.disabled is False


def test_disabled_no_means_enabled():
    rule = _parse_rule(disabled_value="no")
    assert rule.disabled is False


def test_disabled_yes_means_disabled():
    rule = _parse_rule(disabled_value="yes")
    assert rule.disabled is True


def test_disabled_yes_with_whitespace_means_disabled():
    rule = _parse_rule(disabled_value=" yes ")
    assert rule.disabled is True


def test_disabled_no_with_whitespace_means_enabled():
    rule = _parse_rule(disabled_value=" no ")
    assert rule.disabled is False
