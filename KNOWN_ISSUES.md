# Known Issues

## Security Policies Endpoint Error

The `/api/v1/configs/{config_name}/security-policies` endpoint has a bug where it tries to set fields on the SecurityRule model that don't exist:

```python
# In main.py, get_all_security_policies function:
rule.device_group = dg.name  # SecurityRule doesn't have this field
rule.rule_type = 'Device Group' if rule.parent_device_group else 'Shared'  # Doesn't exist
rule.order = index + 1  # Doesn't exist
rule.rulebase_location = f"{dg.name} #{index + 1}"  # Doesn't exist
```

The SecurityRule model is a Pydantic model that doesn't allow setting arbitrary attributes. These fields should either be:
1. Added to the SecurityRule model definition
2. Handled using a wrapper/response model
3. Added as computed properties

**Impact**: The security-policies endpoint returns a 500 Internal Server Error when accessed.

**Workaround**: Use the device-group-specific endpoints instead:
- `/api/v1/configs/{config_name}/device-groups/{group_name}/security-policies`