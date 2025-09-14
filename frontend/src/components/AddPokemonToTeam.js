import React, { useState, useEffect } from 'react';

function AddPokemonToTeam({ teamId, onPokemonAdded }) {
  const [pokemonList, setPokemonList] = useState([]);
  const [selectedPokemon, setSelectedPokemon] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    fetch('/Teams/pokemon_list')
      .then(res => res.json())
      .then(data => setPokemonList(data.pokemon || []))
      .catch(() => setError('Failed to load Pokémon list'))
      .finally(() => setLoading(false));
  }, []);

  const handleAdd = () => {
    setLoading(true);
    fetch(`/Teams/${teamId}/add_pokemon`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pokemon_id: selectedPokemon })
    })
      .then(res => res.json())
      .then(() => {
        setSelectedPokemon('');
        onPokemonAdded();
      })
      .catch(() => setError('Failed to add Pokémon'))
      .finally(() => setLoading(false));
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{color:'red'}}>{error}</div>;

  return (
    <div>
      <select value={selectedPokemon} onChange={e => setSelectedPokemon(e.target.value)}>
        <option value="">Select Pokémon</option>
        {pokemonList.map(p => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </select>
      <button onClick={handleAdd} disabled={!selectedPokemon}>Add to Team</button>
    </div>
  );
}

export default AddPokemonToTeam;