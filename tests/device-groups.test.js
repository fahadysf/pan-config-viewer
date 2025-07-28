/**
 * Jest test suite for device group detection
 * Tests the parser and API endpoints for proper device group handling
 */

const axios = require('axios');

// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
const CONFIG_NAME = '16-7-Panorama-Core-688';

// Expected device groups
const EXPECTED_DEVICE_GROUPS = [
  'TCN-DC-SWIFT-VSYS',
  'TCN-DC-Tapping-Vsys',
  'TCN-DC-Vsys1',
  'KIZAD-DC-Vsys1',
  'KIZAD-DC-Tapping-Vsys',
  'KIZAD-DC-SWIFT-VSYS'
];

// Device group details for validation
const DEVICE_GROUP_DETAILS = {
  'TCN-DC-SWIFT-VSYS': {
    addresses: 0,
    services: 0,
    pre_rules: 280,
    post_rules: 0
  },
  'TCN-DC-Tapping-Vsys': {
    addresses: 0,
    services: 0,
    pre_rules: 1,
    post_rules: 0
  },
  'TCN-DC-Vsys1': {
    addresses: 508,
    services: 95,
    pre_rules: 13791,
    post_rules: 4
  },
  'KIZAD-DC-Vsys1': {
    addresses: 684,
    services: 97,
    pre_rules: 19221,
    post_rules: 10
  },
  'KIZAD-DC-Tapping-Vsys': {
    addresses: 0,
    services: 0,
    pre_rules: 1,
    post_rules: 0
  },
  'KIZAD-DC-SWIFT-VSYS': {
    addresses: 3,
    services: 0,
    pre_rules: 294,
    post_rules: 0
  }
};

describe('Device Group Detection Tests', () => {
  
  describe('API Health Check', () => {
    test('API should be running and healthy', async () => {
      const response = await axios.get(`${API_BASE_URL}/health`);
      expect(response.status).toBe(200);
      expect(response.data.status).toBe('healthy');
      expect(response.data.configs_available).toBeGreaterThan(0);
    });
  });

  describe('Device Groups Summary Endpoint', () => {
    let deviceGroups;

    beforeAll(async () => {
      const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups`);
      deviceGroups = response.data;
    });

    test('should return all expected device groups', () => {
      expect(deviceGroups).toHaveLength(EXPECTED_DEVICE_GROUPS.length);
    });

    test('should contain all expected device group names', () => {
      const groupNames = deviceGroups.map(g => g.name);
      EXPECTED_DEVICE_GROUPS.forEach(expectedGroup => {
        expect(groupNames).toContain(expectedGroup);
      });
    });

    test('each device group should have correct structure', () => {
      deviceGroups.forEach(group => {
        expect(group).toHaveProperty('name');
        expect(group).toHaveProperty('address_count');
        expect(group).toHaveProperty('service_count');
        expect(group).toHaveProperty('pre_security_rules_count');
        expect(group).toHaveProperty('post_security_rules_count');
        expect(group).toHaveProperty('xpath');
      });
    });

    test('device groups should match snapshot', () => {
      // Sort for consistent snapshot
      const sortedGroups = [...deviceGroups].sort((a, b) => a.name.localeCompare(b.name));
      expect(sortedGroups).toMatchSnapshot();
    });
  });

  describe('Individual Device Group Endpoints', () => {
    EXPECTED_DEVICE_GROUPS.forEach(groupName => {
      describe(`Device Group: ${groupName}`, () => {
        let deviceGroup;

        beforeAll(async () => {
          const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}`);
          deviceGroup = response.data;
        });

        test('should return device group details', () => {
          expect(deviceGroup).toBeDefined();
          expect(deviceGroup.name).toBe(groupName);
        });

        test('should have expected properties', () => {
          expect(deviceGroup).toHaveProperty('name');
          expect(deviceGroup).toHaveProperty('devices');
          expect(deviceGroup).toHaveProperty('pre_rules');
          expect(deviceGroup).toHaveProperty('post_rules');
          expect(deviceGroup).toHaveProperty('xpath');
        });

        test('addresses endpoint should work', async () => {
          const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}/addresses`);
          expect(response.status).toBe(200);
          expect(Array.isArray(response.data)).toBe(true);
          
          // Validate count matches expected
          const expectedDetails = DEVICE_GROUP_DETAILS[groupName];
          expect(response.data.length).toBe(expectedDetails.addresses);
        });

        test('services endpoint should work', async () => {
          const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}/services`);
          expect(response.status).toBe(200);
          expect(Array.isArray(response.data)).toBe(true);
          
          // Validate count matches expected
          const expectedDetails = DEVICE_GROUP_DETAILS[groupName];
          expect(response.data.length).toBe(expectedDetails.services);
        });

        test('rules endpoint should work', async () => {
          const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}/rules`);
          expect(response.status).toBe(200);
          expect(Array.isArray(response.data)).toBe(true);
          
          // Total rules should be pre + post
          const expectedDetails = DEVICE_GROUP_DETAILS[groupName];
          const expectedTotal = expectedDetails.pre_rules + expectedDetails.post_rules;
          expect(response.data.length).toBe(expectedTotal);
        });

        test('address groups endpoint should work', async () => {
          const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}/address-groups`);
          expect(response.status).toBe(200);
          expect(Array.isArray(response.data)).toBe(true);
        });

        test('service groups endpoint should work', async () => {
          const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}/service-groups`);
          expect(response.status).toBe(200);
          expect(Array.isArray(response.data)).toBe(true);
        });
      });
    });
  });

  describe('Device Group Filtering', () => {
    test('should filter device groups by name', async () => {
      const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups?name=KIZAD`);
      expect(response.status).toBe(200);
      
      const groups = response.data;
      expect(groups.length).toBe(3); // KIZAD-DC-Vsys1, KIZAD-DC-Tapping-Vsys, KIZAD-DC-SWIFT-VSYS
      groups.forEach(group => {
        expect(group.name).toContain('KIZAD');
      });
    });

    test('should filter rules by rulebase type', async () => {
      const groupName = 'KIZAD-DC-Vsys1';
      
      // Test pre-rules only
      const preResponse = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}/rules?rulebase=pre`);
      expect(preResponse.status).toBe(200);
      
      // Test post-rules only
      const postResponse = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}/rules?rulebase=post`);
      expect(postResponse.status).toBe(200);
      
      // Test all rules
      const allResponse = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}/rules?rulebase=all`);
      expect(allResponse.status).toBe(200);
      
      // Verify counts
      const preRules = preResponse.data;
      const postRules = postResponse.data;
      const allRules = allResponse.data;
      
      expect(allRules.length).toBe(preRules.length + postRules.length);
    });
  });

  describe('Error Handling', () => {
    test('should return 404 for non-existent device group', async () => {
      try {
        await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/NonExistentGroup`);
        fail('Should have thrown 404 error');
      } catch (error) {
        expect(error.response.status).toBe(404);
        expect(error.response.data.detail).toContain('not found');
      }
    });

    test('should handle empty results gracefully', async () => {
      // Test with a device group that has no services
      const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/TCN-DC-SWIFT-VSYS/services`);
      expect(response.status).toBe(200);
      expect(response.data).toEqual([]);
    });
  });

  describe('Data Integrity Tests', () => {
    test('device group objects should have consistent parent references', async () => {
      // Get addresses from a device group
      const groupName = 'KIZAD-DC-Vsys1';
      const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}/addresses`);
      
      response.data.forEach(address => {
        expect(address.parent_device_group).toBe(groupName);
        expect(address.parent_template).toBeNull();
        expect(address.parent_vsys).toBeNull();
      });
    });

    test('security rules should have proper structure', async () => {
      const groupName = 'TCN-DC-SWIFT-VSYS';
      const response = await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/${groupName}/rules`);
      
      const rules = response.data;
      expect(rules.length).toBeGreaterThan(0);
      
      rules.forEach(rule => {
        expect(rule).toHaveProperty('name');
        expect(rule).toHaveProperty('from_');
        expect(rule).toHaveProperty('to');
        expect(rule).toHaveProperty('source');
        expect(rule).toHaveProperty('destination');
        expect(rule).toHaveProperty('action');
        expect(rule).toHaveProperty('parent_device_group');
        expect(rule.parent_device_group).toBe(groupName);
      });
    });
  });

  describe('Performance Tests', () => {
    test('device groups endpoint should respond quickly', async () => {
      const start = Date.now();
      await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups`);
      const duration = Date.now() - start;
      
      expect(duration).toBeLessThan(1000); // Should respond within 1 second
    });

    test('large device group rules should load efficiently', async () => {
      const start = Date.now();
      await axios.get(`${API_BASE_URL}/configs/${CONFIG_NAME}/device-groups/KIZAD-DC-Vsys1/rules`);
      const duration = Date.now() - start;
      
      expect(duration).toBeLessThan(5000); // Even large rule sets should load within 5 seconds
    });
  });
});