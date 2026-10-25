
import "dotenv/config";
import pg from "pg";

const { Pool } = pg;

/**
 * Creates a reusable connection pool for PostgreSQL.
 */
const pool = new Pool({
  host: process.env.POSTGRES_HOST,
  port: Number(process.env.POSTGRES_PORT || 5432),
  database: process.env.POSTGRES_DB,
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  connectionTimeoutMillis: 5000,
  idleTimeoutMillis: 30000,
});

/**
 * Logs unexpected errors from idle database connections.
 */
pool.on("error", (error) => {
  console.error("Unexpected PostgreSQL pool error:", error.message);
});

/**
 * Executes a parameterized SQL query.
 *
 * @param {string} text - SQL query to execute.
 * @param {Array<unknown>} params - Query parameter values.
 * @returns {Promise<import("pg").QueryResult>}
 */
export async function query(text, params = []) {
  return pool.query(text, params);
}

/**
 * Checks whether PostgreSQL is reachable.
 *
 * @returns {Promise<boolean>}
 */
export async function checkDatabaseConnection() {
  await query("SELECT 1");
  return true;
}

export default pool;
