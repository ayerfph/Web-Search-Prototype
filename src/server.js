
import "dotenv/config";
import express from "express";
import cors from "cors";

import pokemonRouter from "./routes/pokemon.js";
import {
  checkDatabaseConnection,
  query,
} from "./config/db.js";

const app = express();
const PORT = Number(process.env.PORT || 3000);

async function ensureCategoryColumn() {
  await query(
    "ALTER TABLE pokemon_descriptions ADD COLUMN IF NOT EXISTS category TEXT",
  );
}

// Middleware
app.use(
  cors({
    origin: process.env.FRONTEND_URL || "http://localhost:5173",
  })
);

app.use(express.json());


// home
app.get("/", async (req, res, next) => {
  try {
    const result = await query(`
      SELECT
        p.id,
        p.name,
        p.height,
        p.weight,

        COALESCE(
          (
            SELECT pd.description
            FROM pokemon_descriptions pd
            WHERE pd.id = p.id
          ),
          ''
        ) AS description,

        COALESCE(
          (
            SELECT json_agg(
              json_build_object(
                'type1', pt.type_1,
                'type2', pt.type_2
              )
            )
            FROM pokemon_types pt
            WHERE pt.id = p.id
          ),
          '[]'::json
        ) AS types,

        COALESCE(
          (
            SELECT json_agg(pa.ability_name)
            FROM pokemon_abilities pa
            WHERE pa.id = p.id
          ),
          '[]'::json
        ) AS abilities,

        COALESCE(
          (
            SELECT row_to_json(ps)
            FROM pokemon_stats ps
            WHERE ps.id = p.id
          ),
          '{}'::json
        ) AS stats

      FROM pokemon p
      ORDER BY p.id;
    `);

    res.json(result.rows);
  } catch (error) {
    next(error);
  }
});

// Basic health endpoint
app.get("/api/health", async (req, res) => {
  try {
    await checkDatabaseConnection();
    await ensureCategoryColumn();

    res.json({
      status: "ok",
      database: "connected",
    });
  } catch (error) {
    console.error("Database health check failed:", error.message);

    res.status(503).json({
      status: "error",
      database: "unavailable",
    });
  }
});

// Pokémon routes
app.use("/api/pokemon", pokemonRouter);

// Handle unknown routes
app.use((req, res) => {
  res.status(404).json({
    error: "Endpoint not found.",
  });
});

// Centralized error handler
app.use((error, req, res, next) => {
  console.error("Request failed:", error.message);

  if (res.headersSent) {
    return next(error);
  }

  res.status(500).json({
    error: "An unexpected server error occurred.",
  });
});

/**
 * Starts the server after checking PostgreSQL connectivity.
 */
async function startServer() {
  try {
    await checkDatabaseConnection();

    app.listen(PORT, "0.0.0.0", () => {
      console.log(`Backend running on port ${PORT}`);
      console.log("PostgreSQL connection successful.");
    });
  } catch (error) {
    console.error(
      "Could not connect to PostgreSQL:",
      error.message
    );

    process.exitCode = 1;
  }
}

startServer();
