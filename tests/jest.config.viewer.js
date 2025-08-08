module.exports = {
    displayName: 'PAN-OS Viewer Tests',
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/setup.js'],
    testMatch: [
        '<rootDir>/viewer.test.js',
        '<rootDir>/viewer-snapshots.test.js'
    ],
    moduleNameMapper: {
        '^jquery$': '<rootDir>/../node_modules/jquery/dist/jquery.js',
        '^datatables.net$': '<rootDir>/../node_modules/datatables.net/js/dataTables.js'
    },
    transform: {
        '^.+\\.js$': 'babel-jest'
    },
    collectCoverageFrom: [
        '<rootDir>/../templates/viewer.html'
    ],
    coverageThreshold: {
        global: {
            branches: 80,
            functions: 80,
            lines: 80,
            statements: 80
        }
    },
    snapshotSerializers: ['jest-serializer-html'],
    globals: {
        'window': {},
        'document': {}
    }
};