module.exports = {
  projects: [
    {
      displayName: 'Frontend Tests',
      testEnvironment: 'jsdom',
      testMatch: ['**/tests/integrated-pagination-filtering.test.js', '**/tests/viewer*.test.js'],
      setupFilesAfterEnv: ['./tests/setup-frontend.js']
    },
    {
      displayName: 'Backend Tests',
      testEnvironment: 'node',
      testMatch: ['**/tests/**/*.test.js'],
      testPathIgnorePatterns: ['/node_modules/', 'integrated-pagination-filtering.test.js', 'viewer'],
      setupFilesAfterEnv: ['./tests/setup.js']
    }
  ],
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/tests/'
  ],
  testTimeout: 30000 // 30 seconds for API tests
};