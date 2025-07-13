# Startup Bakery - Frontend

A modern, responsive chat interface built with React and TypeScript, designed to work with the Startup Bakery backend.

## Features

- Real-time message display
- Responsive design that works on all devices
- Clean, modern UI with styled-components
- Type-safe with TypeScript
- Seamless integration with the Startup Bakery backend
- Simulated bot responses for demonstration

## Prerequisites

- Node.js (v14 or later)
- npm (v6 or later) or Yarn
- Startup Bakery backend service (see [Backend Setup](#backend-setup))

## Getting Started

### Backend Setup

Before starting the frontend, ensure the backend server is running. Follow the instructions in the [backend README](../backend/README.md) to set up and start the backend service.

### Frontend Installation

1. Clone the repository (if you haven't already):
   ```bash
   git clone <repository-url>
   cd startup-bakery/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Configure environment variables (if needed):
   ```bash
   cp .env.example .env
   # Edit .env to configure API endpoints
   ```

## Running the Application

### Development Mode

To run the frontend in development mode:

```bash
npm start
# or
yarn start
```

The application will open automatically in your default browser at [http://localhost:3000](http://localhost:3000).

### Production Build

To create a production build:

```bash
npm run build
# or
yarn build
```

This will create an optimized production build in the `build` folder.

## Project Structure

```
src/
  components/
    Chatbot/
      Chatbot.tsx     # Main chat component
      ChatInput.tsx   # Input component for messages
      ChatMessage.tsx # Component for displaying messages
  App.tsx            # Main application component
  index.tsx          # Application entry point
  types/             # TypeScript type definitions
  styles/            # Global styles (if any)
  utils/             # Utility functions
```

## Connecting to Backend

By default, the frontend is configured to work with the backend running at `http://localhost:8000`. To change this, update the API base URL in the configuration.

## Development

### Available Scripts

- `npm start`: Runs the app in development mode
- `npm test`: Launches the test runner
- `npm run build`: Builds the app for production
- `npm run eject`: Ejects from Create React App (use with caution)

## License

This project is open source and available under the [MIT License](../LICENSE).

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
