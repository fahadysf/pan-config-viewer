# PAN-OS Configuration Viewer - React Frontend

A modern React-based frontend for viewing and managing PAN-OS configurations, built with React, TypeScript, and shadcn/ui.

## Features

- **Modern Tech Stack**: React 18, TypeScript, Vite, Tailwind CSS
- **Component Library**: shadcn/ui components with Radix UI primitives
- **State Management**: Zustand for global state
- **Data Fetching**: TanStack Query (React Query) for server state
- **Testing**: Vitest with React Testing Library
- **Tables**: Advanced data tables with pagination, filtering, and sorting
- **Real-time API Stats**: Collapsible widget showing API call performance metrics

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/          # Layout components (Header, Sidebar, MainContent)
│   │   ├── tables/          # Table components for each data type
│   │   ├── modals/          # Modal components
│   │   ├── widgets/         # Widget components (API Stats)
│   │   └── ui/              # shadcn/ui components
│   ├── services/            # API service layer
│   ├── stores/              # Zustand stores
│   ├── types/               # TypeScript type definitions
│   └── test/                # Test setup and utilities
├── public/                  # Static assets
└── index.html              # Entry HTML file
```

## Available Views

1. **Addresses**: View and manage network addresses
2. **Address Groups**: Manage groups of addresses
3. **Services**: Configure network services
4. **Service Groups**: Manage service groups
5. **Device Groups**: View device group configurations
6. **Security Policies**: Manage security rules and policies
7. **Templates**: Configuration templates
8. **Security Profiles**: Vulnerability and URL filtering profiles

## Development

### Prerequisites

- Node.js 18+ and npm
- Backend API running on port 8000

### Installation

```bash
cd frontend
npm install
```

### Running the Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Running Tests

```bash
# Run tests once
npm test -- --run

# Run tests in watch mode
npm test

# Run tests with coverage
npm run test:coverage
```

### Building for Production

```bash
npm run build
```

The build output will be in `../static/dist`

## Key Components

### Data Tables
- Server-side pagination
- Column visibility controls
- Global search
- Advanced filtering (coming soon in full implementation)
- Export capabilities (coming soon)

### API Stats Widget
- Real-time API performance tracking
- Collapsible interface
- Shows query time and items retrieved
- Maintains history of last 10 API calls

### Sidebar Navigation
- Collapsible menu
- Real-time item counts
- Nested menu for Security Profiles
- Active section highlighting

## State Management

The app uses Zustand for state management with two main stores:

1. **configStore**: Manages configuration selection and navigation
2. **apiStatsStore**: Tracks API call statistics

## API Integration

All API calls go through a centralized service layer (`services/api.ts`) that:
- Handles authentication
- Tracks API statistics
- Manages error handling
- Provides TypeScript types for all endpoints

## Testing Strategy

- **Unit Tests**: For stores and utility functions
- **Component Tests**: For UI components with React Testing Library
- **Integration Tests**: For API interactions (mocked)

## Future Enhancements

- Complete implementation of all table views
- Advanced column filtering UI
- Export functionality (Excel, PDF)
- Column reordering
- Real-time updates via WebSocket
- Dark mode support
- Keyboard shortcuts
- Bulk operations