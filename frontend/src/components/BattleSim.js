
import React, { useState, useEffect } from 'react';
import { usePokemonMoves } from './usePokemonMoves';



function BattleSim() {
  const [teams, setTeams] = useState([]);
  const [team1Id, setTeam1Id] = useState('');
  const [team2Id, setTeam2Id] = useState('');
  const [team1Pokemon, setTeam1Pokemon] = useState([]);
  const [team2Pokemon, setTeam2Pokemon] = useState([]);
  const [poke1Idx, setPoke1Idx] = useState('');
  const [poke2Idx, setPoke2Idx] = useState('');
  const [poke1Move, setPoke1Move] = useState('');
  const [poke2Move, setPoke2Move] = useState('');
  const [battleLog, setBattleLog] = useState([]);
  const [winner, setWinner] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/Teams')
      .then(res => res.json())
      .then(data => setTeams(Array.isArray(data) ? data : []));
  }, []);

  useEffect(() => {
    if (team1Id) {
      fetch(`/Teams/${team1Id}/TeamPokemon/`)
        .then(res => res.json())
        .then(data => setTeam1Pokemon(Array.isArray(data) ? data : []));
    } else {
      setTeam1Pokemon([]);
    }
    setPoke1Idx('');
    setPoke1Move('');
  }, [team1Id]);

  useEffect(() => {
    if (team2Id) {
      fetch(`/Teams/${team2Id}/TeamPokemon/`)
        .then(res => res.json())
        .then(data => setTeam2Pokemon(Array.isArray(data) ? data : []));
    } else {
      setTeam2Pokemon([]);
    }
    setPoke2Idx('');
    setPoke2Move('');
  }, [team2Id]);

  function handleSimulate() {
    if (
      poke1Idx === '' || poke2Idx === '' ||
      !team1Pokemon[poke1Idx] || !team2Pokemon[poke2Idx] ||
      !poke1Move || !poke2Move
    ) return;
    setLoading(true);
    setBattleLog([]);
    setWinner(null);
    const p1 = team1Pokemon[poke1Idx];
    const p2 = team2Pokemon[poke2Idx];
    fetch('/battle/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pokemon1: { id: p1.pokemon_id, level: p1.level, move_id: parseInt(poke1Move) },
        pokemon2: { id: p2.pokemon_id, level: p2.level, move_id: parseInt(poke2Move) }
      })
    })
      .then(res => res.json())
      .then(data => {
        setBattleLog(data.log || []);
        setWinner(data.winner);
      })
      .finally(() => setLoading(false));
  }

  function resetBattle() {
    setBattleLog([]);
    setWinner(null);
    setPoke1Move('');
    setPoke2Move('');
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Pokémon Battle Simulator (Team vs Team)</h2>
      <div style={{ display: 'flex', gap: 32 }}>
        <div>
          <h3>Team 1</h3>
          <select value={team1Id} onChange={e => setTeam1Id(e.target.value)}>
            <option value=''>Select Team</option>
            {teams.map(t => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
          {team1Pokemon.length > 0 && (
            <div>
              <label>Pokémon: </label>
              <select value={poke1Idx} onChange={e => setPoke1Idx(e.target.value)}>
                <option value=''>Select Pokémon</option>
                {team1Pokemon.map((p, idx) => (
                  <option key={p.id} value={idx}>{p.pokemon_name} (Lv. {p.level})</option>
                ))}
              </select>
              {poke1Idx !== '' && team1Pokemon[poke1Idx] && (
                <div>
                  <div>HP: {team1Pokemon[poke1Idx].calculated_hp}</div>
                  <div>Attack: {team1Pokemon[poke1Idx].calculated_attack}</div>
                  <div>Defense: {team1Pokemon[poke1Idx].calculated_defense}</div>
                  <div>Speed: {team1Pokemon[poke1Idx].calculated_speed}</div>
                  <div>Special: {team1Pokemon[poke1Idx].calculated_special}</div>
                  <label>Move: </label>
                  <select value={poke1Move} onChange={e => setPoke1Move(e.target.value)}>
                    <option value=''>Select Move</option>
                    {[1,2,3,4].map(i => {
                      const moveId = team1Pokemon[poke1Idx][`move${i}_id`];
                      return moveId ? <option key={moveId} value={moveId}>Move {i} (ID: {moveId})</option> : null;
                    })}
                  </select>
                </div>
              )}
            </div>
          )}
        </div>
        <div>
          <h3>Team 2</h3>
          <select value={team2Id} onChange={e => setTeam2Id(e.target.value)}>
            <option value=''>Select Team</option>
            {teams.map(t => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
          {team2Pokemon.length > 0 && (
            <div>
              <label>Pokémon: </label>
              <select value={poke2Idx} onChange={e => setPoke2Idx(e.target.value)}>
                <option value=''>Select Pokémon</option>
                {team2Pokemon.map((p, idx) => (
                  <option key={p.id} value={idx}>{p.pokemon_name} (Lv. {p.level})</option>
                ))}
              </select>
              {poke2Idx !== '' && team2Pokemon[poke2Idx] && (
                <div>
                  <div>HP: {team2Pokemon[poke2Idx].calculated_hp}</div>
                  <div>Attack: {team2Pokemon[poke2Idx].calculated_attack}</div>
                  <div>Defense: {team2Pokemon[poke2Idx].calculated_defense}</div>
                  <div>Speed: {team2Pokemon[poke2Idx].calculated_speed}</div>
                  <div>Special: {team2Pokemon[poke2Idx].calculated_special}</div>
                  <label>Move: </label>
                  <select value={poke2Move} onChange={e => setPoke2Move(e.target.value)}>
                    <option value=''>Select Move</option>
                    {[1,2,3,4].map(i => {
                      const moveId = team2Pokemon[poke2Idx][`move${i}_id`];
                      return moveId ? <option key={moveId} value={moveId}>Move {i} (ID: {moveId})</option> : null;
                    })}
                  </select>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      <div style={{ marginTop: 24 }}>
        <button onClick={handleSimulate} disabled={loading || !poke1Move || !poke2Move || poke1Idx === '' || poke2Idx === ''}>Simulate Battle!</button>
        <button onClick={resetBattle} style={{ marginLeft: 8 }}>Reset</button>
      </div>
      <div style={{ marginTop: 24, background: '#f9f9f9', padding: 12, minHeight: 80 }}>
        <b>Battle Log:</b>
        <ul>
          {battleLog.map((line, i) => <li key={i}>{line}</li>)}
        </ul>
        {winner && <div><b>Winner: Team {winner}</b></div>}
      </div>
    </div>
  );
}

export default BattleSim;
