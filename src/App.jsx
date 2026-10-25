import { useEffect, useState } from 'react'
import './App.css'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000').replace(/\/$/, '')
const artwork = (id) =>
  `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${id}.png`

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || 'The Pokédex could not be reached.')
  return data
}

function normalizePokemon(pokemon) {
  const stats = pokemon.stats || {}
  const category =
    pokemon.genus ||
    pokemon.classification ||
    pokemon.species?.genus ||
    pokemon.species?.classification ||
    (pokemon.category && pokemon.category.toLowerCase() !== 'pokemon' && pokemon.category.toLowerCase() !== 'pokémon'
      ? pokemon.category
      : 'Category unavailable')
  return {
    ...pokemon,
    image: pokemon.image || artwork(pokemon.id),
    types: pokemon.types || [],
    category,
    abilities: (pokemon.abilities || []).map((ability) =>
      typeof ability === 'string'
        ? { name: ability, description: 'An ability recorded in the Pokédex.' }
        : ability,
    ),
    stats: {
      HP: stats.hp ?? stats.HP ?? 0,
      Attack: stats.attack ?? stats.Attack ?? 0,
      Defense: stats.defense ?? stats.Defense ?? 0,
      'Sp. Atk': stats.specialAttack ?? stats['Sp. Atk'] ?? 0,
      'Sp. Def': stats.specialDefense ?? stats['Sp. Def'] ?? 0,
      Speed: stats.speed ?? stats.Speed ?? 0,
    },
  }
}

async function searchPokemon(query) {
  const value = query.trim()
  const results = await request(`/api/pokemon?search=${encodeURIComponent(value)}`)
  return results.map(normalizePokemon)
}

async function getPokemon(id) {
  try {
    return normalizePokemon(await request(`/api/pokemon/${id}`))
  } catch (error) {
    if (error.message.includes('not found')) return null
    throw error
  }
}

function Pokeball({ small = false }) {
  return <span aria-hidden="true" className={small ? 'pokeball pokeball--small' : 'pokeball'} />
}

function Header({ onHome }) {
  return (
    <header className="site-header">
      <button className="brand" onClick={onHome} aria-label="Go to Pokédex search">
        <Pokeball small />
        <span>POKÉ</span><strong>DEX</strong>
      </button>
      <div className="header-meta"><span className="status-dot" />Database online</div>
    </header>
  )
}

function SearchBox({ compact = false, onSearch, loading = false }) {
  const [query, setQuery] = useState('')
  function submit(event) {
    event.preventDefault()
    if (query.trim()) onSearch(query.trim())
  }
  return (
    <form className={compact ? 'search-box search-box--compact' : 'search-box'} onSubmit={submit}>
      <span className="search-icon" aria-hidden="true" />
      <input aria-label="Search Pokémon" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by name or Pokédex number..." />
      <button type="submit" disabled={loading}>{loading ? 'Searching...' : 'Search'}</button>
    </form>
  )
}

function TypePills({ types }) {
  return <div className="type-row">{types.map((type) => <span className={`type-pill type-${type.toLowerCase()}`} key={type}>{type}</span>)}</div>
}

function PokemonCard({ pokemon, onSelect }) {
  const primaryType = pokemon.types[0]?.toLowerCase() || 'normal'
  return (
    <button className="pokemon-card" onClick={() => onSelect(pokemon)}>
      <div className="card-topline"><span className="mini-index">No. {String(pokemon.id).padStart(4, '0')}</span><span className="card-arrow" aria-hidden="true">↗</span></div>
      <div className={`card-art type-bg-${primaryType}`}><span className="card-number">{String(pokemon.id).padStart(3, '0')}</span><img src={pokemon.image} alt={pokemon.name} /></div>
      <div className="card-copy"><strong>{pokemon.name}</strong><TypePills types={pokemon.types} /></div>
    </button>
  )
}

function HomePage({ onSelect }) {
  const [results, setResults] = useState([])
  const [heading, setHeading] = useState('Explore the archive')
  const [message, setMessage] = useState('Loading the Pokédex...')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    searchPokemon('')
      .then((data) => {
        setResults(data)
        setMessage('')
      })
      .catch(() => setMessage('The Pokédex could not be reached. Please try again.'))
  }, [])

  async function handleSearch(query) {
    setLoading(true)
    setMessage('Searching the Pokédex...')
    try {
      const found = await searchPokemon(query)
      setResults(found)
      setHeading(`Results for “${query}”`)
      setMessage(found.length ? '' : 'No Pokémon found. Try a name or Pokédex number.')
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main>
      <section className="hero">
        <div className="hero-grid" aria-hidden="true" /><div className="hero-orb hero-orb--one" /><div className="hero-orb hero-orb--two" />
        <p className="eyebrow"><span />National Pokédex Archive</p>
        <h1>Who are you<br />looking for?</h1>
        <p className="hero-copy">Search our complete Pokémon database to discover types, abilities, stats, and more.</p>
        <SearchBox onSearch={handleSearch} loading={loading} />
        <div className="quick-search"><span>Try searching:</span>{['Pikachu', 'Charizard', '#0001'].map((item) => <button key={item} onClick={() => handleSearch(item)}>{item}</button>)}</div>
      </section>
      <section className="catalog">
        <div className="section-heading"><div><p className="section-kicker">Explore the archive</p><h2>{heading}</h2></div><span className="result-count">{results.length} entries</span></div>
        {message && <p className="notice">{message}</p>}
        <div className="card-grid">{results.map((pokemon) => <PokemonCard key={pokemon.id} pokemon={pokemon} onSelect={onSelect} />)}</div>
      </section>
    </main>
  )
}

function StatBar({ name, value }) {
  return <div className="stat"><div><span>{name}</span><strong>{value}</strong></div><div className="stat-track"><span style={{ width: `${Math.min(100, (value / 150) * 100)}%` }} /></div></div>
}

function DetailPage({ pokemon, onBack, onSearch }) {
  const primaryType = pokemon.types[0]?.toLowerCase() || 'normal'
  return (
    <main className="detail-page">
      <div className="detail-tools"><button className="back-button" onClick={onBack}>← Back to Pokédex</button><SearchBox compact onSearch={onSearch} /></div>
      <article className="detail-hero">
        <div className="detail-copy"><p className="dex-number">National No. {String(pokemon.id).padStart(4, '0')}</p><h1>{pokemon.name}</h1><TypePills types={pokemon.types} /><p className="description">{pokemon.description || 'No description is currently available for this Pokémon.'}</p><div className="measurements"><div><span>Height</span><strong>{pokemon.height || '—'}</strong></div><div><span>Weight</span><strong>{pokemon.weight || '—'}</strong></div><div><span>Category</span><strong>{pokemon.category}</strong></div></div></div>
        <div className={`detail-art type-bg-${primaryType}`}><span className="detail-watermark">{String(pokemon.id).padStart(3, '0')}</span><div className="target-rings" /><img src={pokemon.image} alt={pokemon.name} /></div>
      </article>
      <section className="data-grid"><div className="panel"><div className="panel-heading"><span>01</span><h2>Base stats</h2></div><div className="stats-list">{Object.entries(pokemon.stats).map(([name, value]) => <StatBar key={name} name={name} value={value} />)}</div></div><div className="panel"><div className="panel-heading"><span>02</span><h2>Abilities</h2></div><div className="abilities">{pokemon.abilities.map((ability, index) => <div className="ability" key={ability.name}><span>{String(index + 1).padStart(2, '0')}</span><div><strong>{ability.name}</strong><p>{ability.description}</p></div></div>)}</div></div></section>
    </main>
  )
}

function routeId() {
  const match = window.location.pathname.match(/^\/pokemon\/(\d+)/)
  return match ? Number(match[1]) : null
}

function App() {
  const [selected, setSelected] = useState(null)
  const [routeError, setRouteError] = useState('')

  useEffect(() => {
    async function loadRoute() {
      const id = routeId()
      if (!id) return setSelected(null)
      try { setSelected(await getPokemon(id)) } catch (error) { setRouteError(error.message) }
    }
    loadRoute()
    window.addEventListener('popstate', loadRoute)
    return () => window.removeEventListener('popstate', loadRoute)
  }, [])

  function openPokemon(pokemon) {
    window.history.pushState({}, '', `/pokemon/${pokemon.id}`)
    setSelected(pokemon)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  function goHome() { window.history.pushState({}, '', '/'); setSelected(null); setRouteError('') }
  async function detailSearch(query) { const [match] = await searchPokemon(query); if (match) openPokemon(match) }

  return <div className="app-shell"><Header onHome={goHome} />{routeError ? <p className="notice page-notice">{routeError}</p> : selected ? <DetailPage pokemon={selected} onBack={goHome} onSearch={detailSearch} /> : <HomePage onSelect={openPokemon} />}<footer><div><Pokeball small /><strong>POKÉDEX</strong></div><span>Built for trainers, powered by data.</span><span>© 2025 Pokémon Archive</span></footer></div>
}

export default App
