import { defineConfig } from 'orval';

export default defineConfig({
  petstore: {
    output: {
      mode: 'single',
      target: './my-app/lib/api/generate/backend-api.ts',
      schemas: './my-app/lib/api/generate/model',
      client: 'react-query',
      httpClient: 'fetch',
      // mock: true,
      mock: false,
    },
    input: {
      target: 'http://localhost:8000/openapi.json',
    },
  },
});