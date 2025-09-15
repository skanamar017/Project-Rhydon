import React, { useState, useEffect } from 'react';
import { usePokemonMoves } from './usePokemonMoves';

function TeamPokemonDetails({ pokemon, teamId, onUpdated, onDeleted }) {
  const [editing, setEditing] = useState(false);
  const [evs, setEvs] = useState({
    hp: pokemon.ev_hp || 0,
    attack: pokemon.ev_attack || 0,
    defense: pokemon.ev_defense || 0,
    speed: pokemon.ev_speed || 0,
    special: pokemon.ev_special || 0,
  });
  const [moves, setMoves] = useState([
    pokemon.move1_id || '',
    pokemon.move2_id || '',
    pokemon.move3_id || '',
    pokemon.move4_id || '',
  ]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const availableMoves = usePokemonMoves(pokemon.pokemon_id || pokemon.id);

  const handleDelete = () => {
    if (!window.confirm('Delete this Pokémon from the team?')) return;
    setSaving(true);
    fetch(`/Teams/${teamId}/TeamPokemon/${pokemon.id}`, { method: 'DELETE' })
      .then(res => {
        if (!res.ok) throw new Error('Delete failed');
        onDeleted();
      })
      .catch(() => setError('Failed to delete'))
      .finally(() => setSaving(false));
  };

  const handleSave = () => {
    setSaving(true);
    fetch(`/Teams/${teamId}/TeamPokemon/${pokemon.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...evs,
        move1_id: moves[0],
        move2_id: moves[1],
        move3_id: moves[2],
        move4_id: moves[3],
      })
    })
      .then(res => res.json())
      .then(() => {
        setEditing(false);
        onUpdated();
      })
      .catch(() => setError('Failed to update'))
      .finally(() => setSaving(false));
  };

  if (editing) {
    return (
      <div style={{ border: '1px solid #ccc', margin: 8, padding: 8 }}>
        <strong>{pokemon.pokemon_name}</strong> (Lv. {pokemon.level})
        <div>EVs:
          {['hp','attack','defense','speed','special'].map(stat => (
            <span key={stat} style={{ marginLeft: 8 }}>
              {stat.toUpperCase()}: <input type="number" min="0" max="65535" value={evs[stat]} onChange={e => setEvs({ ...evs, [stat]: Number(e.target.value) })} style={{ width: 60 }} />
            </span>
          ))}
        </div>
        <div>Moves:
          {[0,1,2,3].map(i => (
            <select
              key={i}
              value={moves[i]}
              onChange={e => {
                const newMoves = [...moves];
                newMoves[i] = e.target.value;
                setMoves(newMoves);
              }}
              style={{ marginLeft: 8 }}
            >
              <option value="">None</option>
              {availableMoves.map((m, j) => (
                <option key={`${m.move_id}-${j}`} value={m.move_id}>{m.name}</option>
              ))}
            </select>
          ))}
        </div>
        <button onClick={handleSave} disabled={saving}>Save</button>
        <button onClick={() => setEditing(false)} disabled={saving}>Cancel</button>
        {error && <div style={{color:'red'}}>{error}</div>}
      </div>
    );
  }

  return (
    <div style={{ border: '1px solid #eee', margin: 8, padding: 8 }}>
      <strong>{pokemon.pokemon_name}</strong> (Lv. {pokemon.level})
      <div>EVs: HP {pokemon.ev_hp}, Atk {pokemon.ev_attack}, Def {pokemon.ev_defense}, Spd {pokemon.ev_speed}, Spc {pokemon.ev_special}</div>
      <div>Moves: {pokemon.move1_id}, {pokemon.move2_id}, {pokemon.move3_id}, {pokemon.move4_id}</div>
      <button onClick={() => setEditing(true)} disabled={saving}>Edit</button>
      <button onClick={handleDelete} disabled={saving}>Delete</button>
      {error && <div style={{color:'red'}}>{error}</div>}
    </div>
  );
}

export default TeamPokemonDetails;
