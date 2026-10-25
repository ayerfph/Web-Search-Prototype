
import { Router } from "express";
import { query } from "../config/db.js";

const router = Router();

router.get("/", async (req, res, next) => {
  const search = String(req.query.search || "").trim().toLowerCase();

  try {
    const result = await query(
      `SELECT p.id, p.name, p.height, p.weight,
              COALESCE(pd.description, '') AS description,
              COALESCE(pd.category, '') AS category,
              COALESCE(pt.type_1, '') AS type_1,
              COALESCE(pt.type_2, '') AS type_2,
              COALESCE(ps.hp, 0) AS hp,
              COALESCE(ps.attack, 0) AS attack,
              COALESCE(ps.defense, 0) AS defense,
              COALESCE(ps.special_attack, 0) AS special_attack,
              COALESCE(ps.special_defense, 0) AS special_defense,
              COALESCE(ps.speed, 0) AS speed
       FROM pokemon p
       LEFT JOIN pokemon_descriptions pd ON pd.id = p.id
       LEFT JOIN pokemon_types pt ON pt.id = p.id
       LEFT JOIN pokemon_stats ps ON ps.id = p.id
       WHERE ($1 = '' OR LOWER(p.name) LIKE '%' || $1 || '%' OR CAST(p.id AS TEXT) LIKE '%' || REPLACE($1, '#', '') || '%')
       ORDER BY p.id
       LIMIT 100`,
      [search],
    );

    const ids = result.rows.map((row) => row.id);
    const abilities = ids.length
      ? await query(
          `SELECT id, ability_name FROM pokemon_abilities WHERE id = ANY($1::int[]) ORDER BY id`,
          [ids],
        )
      : { rows: [] };
    const abilityMap = new Map();
    for (const row of abilities.rows) {
      const current = abilityMap.get(row.id) || [];
      current.push(row.ability_name);
      abilityMap.set(row.id, current);
    }

    return res.json(result.rows.map((row) => ({
      id: row.id,
      name: row.name,
      height: row.height,
      weight: row.weight,
      description: row.description,
      category: row.category,
      types: [row.type_1, row.type_2].filter(Boolean),
      abilities: abilityMap.get(row.id) || [],
      stats: {
        hp: row.hp,
        attack: row.attack,
        defense: row.defense,
        specialAttack: row.special_attack,
        specialDefense: row.special_defense,
        speed: row.speed,
      },
    })));
  } catch (error) {
    return next(error);
  }
});

/**
 * Searches for a Pokémon by name.
 *
 * GET /api/pokemon/:name
 *
 * @returns {Promise<void>} Sends Pokémon data as JSON.
 */
router.get("/:name", async (req, res, next) => {
  const name = req.params.name.trim().toLowerCase();

  if (!name || name.length > 100) {
    return res.status(400).json({
      error: "Please provide a valid Pokémon name.",
    });
  }

  try {
    // 1. Retrieve the main Pokémon record.
    const pokemonResult = await query(
      `SELECT id, name, height, weight
       FROM pokemon
       WHERE LOWER(name) = $1 OR ($1 ~ '^[0-9]+$' AND id = $1::integer)
       LIMIT 1`,
      [name]
    );

    if (pokemonResult.rows.length === 0) {
      return res.status(404).json({
        error: `Pokémon '${name}' was not found.`,
      });
    }

    const pokemon = pokemonResult.rows[0];

    // 2. Retrieve related records.
    const [descriptionResult, typesResult, abilitiesResult, statsResult] =
      await Promise.all([
        query(
          `SELECT description, category
           FROM pokemon_descriptions
           WHERE id = $1`,
          [pokemon.id]
        ),

        query(
          `SELECT type_1, type_2
           FROM pokemon_types
           WHERE id = $1`,
          [pokemon.id]
        ),

        query(
          `SELECT ability_name
           FROM pokemon_abilities
           WHERE id = $1`,
          [pokemon.id]
        ),

        query(
          `SELECT hp, attack, defense,
                  special_attack, special_defense, speed
           FROM pokemon_stats
           WHERE id = $1`,
          [pokemon.id]
        ),
      ]);

    const description = descriptionResult.rows[0]?.description ?? null;
    const category = descriptionResult.rows[0]?.category ?? null;
    const typeRow = typesResult.rows[0] ?? {};
    const stats = statsResult.rows[0] ?? null;

    // 3. Return a consistent API response.
    return res.json({
      id: pokemon.id,
      name: pokemon.name,
      height: pokemon.height,
      weight: pokemon.weight,
      description,
      category,

      types: [typeRow.type_1, typeRow.type_2].filter(Boolean),

      abilities: abilitiesResult.rows.map(
        (row) => row.ability_name
      ),

      stats: stats
        ? {
            hp: stats.hp,
            attack: stats.attack,
            defense: stats.defense,
            specialAttack: stats.special_attack,
            specialDefense: stats.special_defense,
            speed: stats.speed,
          }
        : null,
    });
  } catch (error) {
    next(error);
  }
});

export default router;
