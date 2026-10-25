 # Pokémon Web Backend

This folder contains the backend API for the Pokémon web project. It is built with **Node.js** and **Express.js** and provides HTTP endpoints that the frontend can use to retrieve and manage Pokémon data.

## Responsibilities

- Start the Express.js web server.
- Define API routes for Pokémon resources.
- Validate incoming requests.
- Process application and database logic.
- Return JSON responses to the frontend.
- Handle errors and unknown routes.

## Typical project structure

```text
backend/
├── src/
│   ├── app.js              # Express application configuration
│   ├── server.js           # Server entry point
│   ├── routes/             # API route definitions
│   ├── controllers/        # Request and response logic
│   ├── services/           # Business logic and external API calls
│   ├── models/             # Data models
│   └── middleware/         # Validation, authentication, and errors
├── .env                    # Local environment variables
├── package.json            # Dependencies and scripts
└── README.MD
```

The exact structure may differ depending on the implementation.

## Requirements

- Node.js 18 or newer
- npm
- Optional: a database, if configured by the project

## Installation

From this directory, install the dependencies:

```bash
npm install
```

Create a `.env` file when environment variables are required. Example:

```env
PORT=3000
NODE_ENV=development
```

## Running the server

Start the development server:

```bash
npm run dev
```

Start the production server:

```bash
npm start
```

If no npm scripts are defined, run the entry file directly, for example:

```bash
node src/server.js
```

The API is then available at:

```text
http://localhost:3000
```

## API example

An example Pokémon endpoint could be:

```http
GET /api/pokemon
```

Example response:

```json
[
	{
		"id": 1,
		"name": "bulbasaur",
		"types": ["grass", "poison"]
	}
]
```

Routes should be grouped under `/api` and return suitable HTTP status codes, such as `200` for successful requests, `201` for created resources, `400` for invalid input, and `404` when a resource is not found.

## Development notes

- Keep route definitions separate from controllers.
- Store secrets and environment-specific values in `.env`.
- Do not commit passwords, API keys, or private connection strings.
- Validate request parameters before processing them.
- Use centralized error-handling middleware for consistent responses.
- Enable CORS when the frontend runs on a different origin.

## Testing

Run the project tests with:

```bash
npm test
```

## License

Add the project's license information here.
