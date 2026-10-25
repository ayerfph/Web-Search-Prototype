# Pokémon Frontend

The frontend for the Pokémon project is a React application powered by Vite. It provides the browser UI, manages component state, and communicates with the project’s backend or Pokémon data service.

## Technology stack

- **React** – component-based UI development.
- **Vite** – fast development server and production bundler.
- **JavaScript/JSX** – application logic and React markup.
- **ESLint** – catches common JavaScript and React issues.

## Prerequisites

- Node.js 18 or newer (Node.js 20+ is recommended).
- npm, or another compatible package manager.
- A running backend/API if the application is configured to load data remotely.

## Installation

From this directory, install the dependencies:

```bash
npm install
```

## Development

Start the Vite development server:

```bash
npm run dev
```

Open the URL printed in the terminal, normally `http://localhost:5173`. Vite provides fast refresh, so most saved source changes appear immediately without manually reloading the page.

## Available scripts

The exact scripts are defined in `package.json`:

```bash
npm run dev      # Start the local development server
npm run build    # Create an optimized production build
npm run preview  # Preview the production build locally
npm run lint     # Run ESLint
```

Run only scripts that are present in the local `package.json`.

## Project structure

The main Vite entry points are typically:

```text
frontend/
├── public/          # Static files copied without bundling
├── src/             # React application source
│   ├── assets/      # Images, icons, and other imported assets
│   ├── components/  # Reusable UI components
│   ├── pages/       # Page-level views, when used
│   ├── App.*        # Root application component
│   └── main.*       # React entry point
├── index.html       # HTML shell used by Vite
├── package.json     # Dependencies and npm scripts
└── vite.config.*    # Vite configuration
```

The actual folders may differ as the application grows. Keep reusable presentation in components and keep page or feature-specific behavior close to the feature that uses it.

## Application flow

1. Vite serves `index.html`.
2. The entry file in `src` mounts React into the page.
3. `App` composes the Pokémon screens and reusable components.
4. Components render loading, success, empty, and error states.
5. API or service calls retrieve Pokémon data and update React state.

Use controlled inputs for search and filtering, stable keys when rendering lists, and clear feedback when a request fails or returns no results.

## Environment variables

If the frontend needs configurable service URLs, define them in a local `.env` file using the `VITE_` prefix:

```env
VITE_API_URL=http://localhost:8000
```

Access client-side variables with `import.meta.env.VITE_API_URL`. Do not put passwords, private tokens, or other secrets in frontend environment variables; values exposed to Vite are included in the browser bundle.

## Production build

Create and preview an optimized build with:

```bash
npm run build
npm run preview
```

The generated files are placed in `dist/`. Deploy that directory to a static host, or configure the deployment platform to run the build command and serve the resulting directory. If client-side routing is added, configure the host to fall back to `index.html` for application routes.

## Development guidelines

- Keep components small and focused on one responsibility.
- Prefer semantic HTML and accessible labels for interactive controls.
- Show loading and error states for asynchronous requests.
- Avoid hard-coding environment-specific API URLs in components.
- Run linting before committing changes.
- Keep dependencies up to date and remove unused imports and files.

## Useful references

- [React documentation](https://react.dev/)
- [Vite documentation](https://vite.dev/)
- [ESLint documentation](https://eslint.org/)
