# PAN-OS Panorama Configuration API

A FastAPI-based REST API for exploring Panorama PAN-OS configuration from XML backup files. This application parses Panorama configuration XML files and provides a comprehensive API to access various configuration objects.

## Features

- **Real-time XML parsing** - Reads configuration directly from XML file
- **Comprehensive API endpoints** for:
  - Address Objects and Address Groups
  - Service Objects and Service Groups
  - Security Profiles (Antivirus, Anti-spyware, Vulnerability, URL Filtering, etc.)
  - Device Groups and Templates
  - Security Rules and NAT Rules
  - Log Forwarding Profiles
  - Schedules
- **Location tracking** - Every object includes:
  - XPath location in the XML
  - Parent device-group (for Panorama configs)
  - Parent template (for Panorama configs)
  - Parent vsys (for firewall configs)
- **Multi-location support** - Objects from shared, device-groups, templates, and vsys
- **XPath search** - Find any object by its exact XML path
- **Auto-generated Swagger documentation**
- **Filtering support** on most endpoints
- **Pydantic models** for data validation and serialization
- **Docker support** for easy deployment

## Quick Start with Docker

### Using Docker Compose (Recommended)

1. Create a directory for your XML configuration files:
```bash
mkdir config-files
```

2. Copy your Panorama XML backup files to the `config-files` directory:
```bash
cp your-panorama-backup.xml config-files/
```

3. Build and run with docker-compose:
```bash
docker-compose up -d
```

4. Access the API:
   - List available configs: http://localhost:8000/api/v1/configs
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

5. Stop the container:
```bash
docker-compose down
```

### Using Docker Directly

1. Build the Docker image:
```bash
docker build -t pan-config-viewer .
```

2. Create a directory for your XML files:
```bash
mkdir config-files
cp your-panorama-backup.xml config-files/
```

3. Run the container:
```bash
docker run -d \
  --name pan-config-api \
  -p 8000:8000 \
  -v $(pwd)/config-files:/config-files:ro \
  -e CONFIG_FILES_PATH=/config-files \
  pan-config-viewer
```

4. Stop and remove the container:
```bash
docker stop pan-config-api
docker rm pan-config-api
```

### Using Multiple XML Files

The API supports multiple XML configuration files. Simply place all your XML files in the `config-files` directory. Each file will be accessible via its filename (without the .xml extension) in the API path.

For example, if you have:
- `config-files/production.xml`
- `config-files/staging.xml`
- `config-files/development.xml`

You can access them via:
- `/api/v1/configs/production/addresses`
- `/api/v1/configs/staging/addresses`
- `/api/v1/configs/development/addresses`

## Local Installation (Without Docker)

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Update the `XML_FILE_PATH` variable in `main.py` to point to your Panorama XML backup file:
```python
XML_FILE_PATH = "/path/to/your/panorama-backup.xml"
```

4. Run the application:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the application is running, access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Configuration Management
- `GET /api/v1/configs` - List all available configuration files
- `GET /api/v1/configs/{config_name}/info` - Get information about a specific configuration

### Address Objects
- `GET /api/v1/configs/{config_name}/addresses` - Get all address objects
- `GET /api/v1/configs/{config_name}/addresses/{name}` - Get specific address object
- `GET /api/v1/configs/{config_name}/address-groups` - Get all address groups
- `GET /api/v1/configs/{config_name}/address-groups/{name}` - Get specific address group

### Service Objects
- `GET /api/v1/configs/{config_name}/services` - Get all service objects
- `GET /api/v1/configs/{config_name}/services/{name}` - Get specific service object
- `GET /api/v1/configs/{config_name}/service-groups` - Get all service groups

### Security Profiles
- `GET /api/v1/configs/{config_name}/security-profiles/vulnerability` - Get vulnerability profiles
- `GET /api/v1/configs/{config_name}/security-profiles/url-filtering` - Get URL filtering profiles

### Device Management
- `GET /api/v1/configs/{config_name}/device-groups` - Get all device groups (summary with counts)
- `GET /api/v1/configs/{config_name}/device-groups/{name}` - Get specific device group details
- `GET /api/v1/configs/{config_name}/device-groups/{name}/addresses` - Get addresses in device group
- `GET /api/v1/configs/{config_name}/device-groups/{name}/address-groups` - Get address groups in device group
- `GET /api/v1/configs/{config_name}/device-groups/{name}/services` - Get services in device group
- `GET /api/v1/configs/{config_name}/device-groups/{name}/service-groups` - Get service groups in device group
- `GET /api/v1/configs/{config_name}/device-groups/{name}/rules` - Get security rules for device group
- `GET /api/v1/configs/{config_name}/templates` - Get all templates
- `GET /api/v1/configs/{config_name}/templates/{name}` - Get specific template
- `GET /api/v1/configs/{config_name}/template-stacks` - Get all template stacks
- `GET /api/v1/configs/{config_name}/template-stacks/{name}` - Get specific template stack

### Logging
- `GET /api/v1/configs/{config_name}/log-profiles` - Get log forwarding profiles
- `GET /api/v1/configs/{config_name}/schedules` - Get schedules

### System
- `GET /api/v1/health` - Health check endpoint

**Note**: Replace `{config_name}` with the name of your XML file (without the .xml extension)

## Query Parameters

Most endpoints support filtering:
- `name` - Filter by name (partial match)
- `tag` - Filter by tag (where applicable)
- `protocol` - Filter by protocol (for services)
- `parent` - Filter by parent (for device groups)
- `rulebase` - Filter by rulebase type (for security rules)
- `location` - Filter by location (all/shared/device-group/template/vsys) for addresses

## Enhanced Object Information

Every configuration object now includes:
- `xpath` - The exact XPath location in the XML file
- `parent_device_group` - The parent device group name (if applicable)
- `parent_template` - The parent template name (if applicable)
- `parent_vsys` - The parent virtual system name (if applicable)

This allows you to:
1. Know exactly where each object is defined
2. Understand inheritance and override relationships
3. Search for objects by their XML path
4. Filter objects by their location context

## Device Group Summary

The device groups endpoint now returns a summary with counts instead of full objects:

```json
{
  "name": "production-dg",
  "description": "Production environment device group",
  "parent_dg": "shared-dg",
  "devices_count": 5,
  "address_count": 125,
  "address_group_count": 15,
  "service_count": 45,
  "service_group_count": 8,
  "pre_security_rules_count": 50,
  "post_security_rules_count": 20,
  "pre_nat_rules_count": 10,
  "post_nat_rules_count": 5,
  "xpath": "/config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='production-dg']"
}
```

To get the actual objects, use the specific endpoints like:
- `/api/v1/configs/{config_name}/device-groups/production-dg/addresses`
- `/api/v1/configs/{config_name}/device-groups/production-dg/rules`

## Example Usage

```bash
# List available configurations
curl http://localhost:8000/api/v1/configs

# Get all address objects from a specific config
curl http://localhost:8000/api/v1/configs/pan-bkp-202507151414/addresses

# Get address objects with "server" in the name
curl http://localhost:8000/api/v1/configs/pan-bkp-202507151414/addresses?name=server

# Get a specific device group
curl http://localhost:8000/api/v1/configs/pan-bkp-202507151414/device-groups/production-dg

# Get security rules for a device group
curl http://localhost:8000/api/v1/configs/pan-bkp-202507151414/device-groups/production-dg/rules?rulebase=pre

# Get addresses from device groups only
curl http://localhost:8000/api/v1/configs/pan-bkp-202507151414/addresses?location=device-group

# Search for an object by XPath
curl http://localhost:8000/api/v1/configs/pan-bkp-202507151414/search/by-xpath?xpath=/config/shared/address/entry[@name='web-server']

# Get device groups summary with counts
curl http://localhost:8000/api/v1/configs/pan-bkp-202507151414/device-groups

# Get addresses from a specific device group
curl http://localhost:8000/api/v1/configs/pan-bkp-202507151414/device-groups/production-dg/addresses

# Get services from a device group
curl http://localhost:8000/api/v1/configs/pan-bkp-202507151414/device-groups/production-dg/services
```

## Development

The application consists of three main components:

1. **models.py** - Pydantic models for all configuration objects
2. **parser.py** - XML parsing logic using lxml
3. **main.py** - FastAPI application and endpoints

## Testing

The application includes comprehensive tests for all endpoints. See [TESTS.md](TESTS.md) for detailed testing guide.

### Quick Start

Using the Makefile:
```bash
# Run tests locally (no Docker required)
make test

# Run tests with Docker
make test-docker

# Run full test suite with error handling
make test-full

# Run tests with coverage
make test-coverage

# Run basic smoke tests (API must be running)
make test-basic
```

Using test scripts directly:
```bash
# Run all tests with Docker (starts API automatically)
./run_tests.sh

# Run full test suite (continues on failures)
./run_tests_full.sh

# Run tests locally without Docker
./run_tests_local.sh
```

### Test Files

- `tests/test_api.py` - Tests with sample XML data
- `tests/test_real_config.py` - Tests with your actual configuration
- `tests/test_basic.py` - Quick smoke tests
- `tests/conftest.py` - Test configuration and fixtures
- `TESTS.md` - Comprehensive testing documentation

For more details, see [TESTS.md](TESTS.md)

## Production Deployment

For production deployments, use the production docker-compose file:

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` to set your configuration:
```bash
# API Configuration
API_PORT=8000

# XML File Configuration  
XML_FILE_PATH=./your-panorama-backup.xml

# Application Settings
LOG_LEVEL=info
WORKERS=4
```

3. Run with production settings:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

This production configuration includes:
- Resource limits (CPU and memory)
- Automatic restart policy
- Log rotation
- Environment variable configuration
- Health checks

## Docker Image Management

Build and tag the image:
```bash
docker build -t pan-config-viewer:latest .
docker tag pan-config-viewer:latest pan-config-viewer:1.0.0
```

Save the image for distribution:
```bash
docker save pan-config-viewer:latest | gzip > pan-config-viewer.tar.gz
```

Load the image on another system:
```bash
docker load < pan-config-viewer.tar.gz
```

## Troubleshooting

### Container won't start
- Check that the XML file exists and is readable
- Verify the XML file path in docker-compose.yml or .env
- Check container logs: `docker-compose logs -f`

### API returns 404 for objects
- Ensure the XML file contains the expected configuration sections
- Verify the XML file is a valid Panorama backup
- Check that the XML file path is correctly mounted

### Performance issues
- Increase memory limits in docker-compose.prod.yml
- For large XML files, consider increasing the WORKERS environment variable
- Monitor container resources: `docker stats pan-config-viewer`

## License

Apache 2.0