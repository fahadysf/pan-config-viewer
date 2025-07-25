# PAN-OS Configuration Viewer

A web-based frontend for exploring PAN-OS Panorama configurations using the REST API.

## Features

- **Interactive Dashboard**: Browse configuration objects through an intuitive web interface
- **Real-time Data**: All data is fetched live from the API
- **Configuration Selector**: Switch between multiple configuration files
- **Object Browser**: Navigate through:
  - Address Objects and Groups
  - Service Objects and Groups  
  - Device Groups with summary statistics
  - Templates and Template Stacks
  - Security Profiles
- **Search and Filter**: Quick search and location-based filtering
- **Detail Views**: Click any object to see full JSON details

## Technologies

- **Alpine.js**: Reactive JavaScript framework for interactivity
- **Tailwind CSS**: Utility-first CSS framework for styling
- **PinesUI Components**: Additional UI components (planned)
- **Font Awesome**: Icons throughout the interface

## Access

Once the API is running, access the viewer at:
```
http://localhost:8000/viewer
```

## Usage

1. Select a configuration from the dropdown in the top navigation
2. Click on object types in the left sidebar to browse
3. Use search and filters to find specific objects
4. Click on any object to view detailed information

## Screenshots

The viewer provides:
- Clean, modern interface
- Responsive design
- Real-time statistics badges
- Hierarchical navigation
- Modal detail views