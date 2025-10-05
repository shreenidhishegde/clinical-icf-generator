// Environment configuration for Clinical ICF Generator
const config = {
  development: {
    API_BASE_URL: 'http://127.0.0.1:8000',
    APP_NAME: 'Clinical ICF Generator',
    APP_VERSION: '1.0.0',
    DEBUG: true
  },
  production: {
  },
  staging: {
  }
}

const currentEnv = import.meta.env.MODE || 'development'

export default config[currentEnv] || config.development
