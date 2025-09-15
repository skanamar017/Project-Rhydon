import React, { useState, useEffect } from 'react';
import AddPokemonToTeam from './AddPokemonToTeam';
import TeamPokemonDetails from './TeamPokemonDetails';

function TeamManager() {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teamName, setTeamName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchTeams = () => {
    setLoading(true);
    fetch('/Teams')
      .then(res => res.json())
      .then(data => setTeams(Array.isArray(data) ? data : []))
      .catch(() => setError('Failed to load teams'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTeams();
  }, []);

  const handleCreateTeam = () => {
    setLoading(true);
    fetch('/Teams', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: teamName })
    })
      .then(res => res.json())
      .then(() => {
        setTeamName('');
        fetchTeams();
      })
      .catch(() => setError('Failed to create team'))
      .finally(() => setLoading(false));
  };

  const [teamPokemon, setTeamPokemon] = useState([]);

  const handleSelectTeam = (team) => {
    setSelectedTeam(team);
    setLoading(true);
    fetch(`/Teams/${team.id}/TeamPokemon/`)
      .then(res => res.json())
      .then(data => {
        console.log('TeamPokemon response:', data);
        setTeamPokemon(Array.isArray(data) ? data : []);
      })
      .catch(() => setError('Failed to load team Pokémon'))
      .finally(() => setLoading(false));
  };

  return (
    <div className="card">
      <h2>Team Management</h2>
      <input
        value={teamName}
        onChange={e => setTeamName(e.target.value)}
        placeholder="Team Name"
      />
      <button onClick={handleCreateTeam}>Create Team</button>
      {loading && <div>Loading...</div>}
      {error && <div style={{color:'red'}}>{error}</div>}
      <ul>
        {teams.map(team => (
          <li key={team.id}>
            <button onClick={() => handleSelectTeam(team)}>
              {team.name}
            </button>
          </li>
        ))}
      </ul>
      {selectedTeam && (
        <div>
          <h3>{selectedTeam.name} Details</h3>
          <AddPokemonToTeam teamId={selectedTeam.id} onPokemonAdded={() => handleSelectTeam(selectedTeam)} />
          <h4>Pokémon on Team:</h4>
          {teamPokemon.length === 0 && <div>No Pokémon yet.</div>}
          {teamPokemon.map(p => (
            <TeamPokemonDetails
              key={p.id || p.pokemon_id}
              pokemon={p}
              teamId={selectedTeam.id}
              onUpdated={() => handleSelectTeam(selectedTeam)}
              onDeleted={() => handleSelectTeam(selectedTeam)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default TeamManager;