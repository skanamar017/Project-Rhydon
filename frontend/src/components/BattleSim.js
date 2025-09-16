
import React, { useState, useEffect } from 'react';



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
  const [poke1MoveName, setPoke1MoveName] = useState('');
  const [poke2MoveName, setPoke2MoveName] = useState('');
  const [battleLog, setBattleLog] = useState([]);
  const [winner, setWinner] = useState(null);
  const [loading, setLoading] = useState(false);
  const [poke1HP, setPoke1HP] = useState(null);
  const [poke2HP, setPoke2HP] = useState(null);
  const [turn, setTurn] = useState(1);
  const [battleId, setBattleId] = useState(null);
  const [activeIdx1, setActiveIdx1] = useState(0);
  const [activeIdx2, setActiveIdx2] = useState(0);

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

  // Helper to get move options for a TeamPokemon
  function getMoveOptions(pokemon) {
    const moves = [];
    for (let i = 1; i <= 4; i++) {
      const moveId = pokemon[`move${i}_id`];
      const moveName = pokemon[`move${i}_name`] || `Move ${i}`;
      if (moveId) moves.push({ id: moveId, name: moveName });
    }
    return moves;
  }


  // Set HP immediately on Pokémon selection
  useEffect(() => {
    if (poke1Idx !== '' && team1Pokemon[poke1Idx]) {
      setPoke1HP(team1Pokemon[poke1Idx].calculated_hp);
    } else {
      setPoke1HP(null);
    }
  }, [poke1Idx, team1Pokemon]);
  useEffect(() => {
    if (poke2Idx !== '' && team2Pokemon[poke2Idx]) {
      setPoke2HP(team2Pokemon[poke2Idx].calculated_hp);
    } else {
      setPoke2HP(null);
    }
  }, [poke2Idx, team2Pokemon]);

  // Start battle only when user clicks Start Battle
  function handleStartBattle() {
    if (
      poke1Idx !== '' && poke2Idx !== '' &&
      team1Pokemon[poke1Idx] && team2Pokemon[poke2Idx]
    ) {
      setLoading(true);
      setBattleLog([]);
      setWinner(null);
      setBattleId(null);
      setActiveIdx1(0);
      setActiveIdx2(0);
      const party1 = [team1Pokemon[poke1Idx]];
      const party2 = [team2Pokemon[poke2Idx]];
      fetch('/battle/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ teams: [ { party: party1 }, { party: party2 } ] })
      })
        .then(res => res.json())
        .then(data => {
          setBattleId(data.battle_id);
          // Fetch initial status
          fetch(`/battle/status?battle_id=${data.battle_id}`)
            .then(res => res.json())
            .then(status => {
              setPoke1HP(status.teams[0].party[0].current_hp);
              setPoke2HP(status.teams[1].party[0].current_hp);
              setBattleLog([]);
              setWinner(null);
              setTurn(1);
            });
        })
        .finally(() => setLoading(false));
    }
  }

  function handleAttackTurn() {
    if (
      !battleId ||
      poke1Move === '' || poke2Move === '' ||
      poke1HP <= 0 || poke2HP <= 0
    ) return;
    setLoading(true);
    setWinner(null);
    const p1 = team1Pokemon[poke1Idx];
    const p2 = team2Pokemon[poke2Idx];
    const move1 = getMoveOptions(p1).find(m => m.id === parseInt(poke1Move));
    const move2 = getMoveOptions(p2).find(m => m.id === parseInt(poke2Move));
    fetch('/battle/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        battle_id: battleId,
        moves: [
          { move: move1 ? move1.name : '', team: 0 },
          { move: move2 ? move2.name : '', team: 1 }
        ]
      })
    })
      .then(res => res.json())
      .then(data => {
        // Show detailed log for this turn
        const logEntry = data.log;
        let logLines = [];
        if (logEntry) {
          logLines.push(`--- Turn ${logEntry.turn} ---`);
          // Team 0 attacks
          logLines.push(`${p1.pokemon_name} used ${logEntry.moves[0].move}!`);
          logLines.push(`${p2.pokemon_name} took ${logEntry.moves[0].damage} damage. HP left: ${logEntry.moves[0].target_hp}`);
          if (logEntry.moves[0].target_hp === 0) {
            logLines.push(`${p2.pokemon_name} fainted!`);
          }
          // Team 1 attacks
          if (logEntry.moves[1].damage > 0 && logEntry.moves[0].target_hp > 0) {
            logLines.push(`${p2.pokemon_name} used ${logEntry.moves[1].move}!`);
            logLines.push(`${p1.pokemon_name} took ${logEntry.moves[1].damage} damage. HP left: ${logEntry.moves[1].target_hp}`);
            if (logEntry.moves[1].target_hp === 0) {
              logLines.push(`${p1.pokemon_name} fainted!`);
            }
          }
        }
        setBattleLog(prev => [...prev, ...logLines]);
        // Fetch updated status
        fetch(`/battle/status?battle_id=${battleId}`)
          .then(res => res.json())
          .then(status => {
            setPoke1HP(status.teams[0].party[0].current_hp);
            setPoke2HP(status.teams[1].party[0].current_hp);
            setWinner(status.winner);
            setTurn(status.turn);
          });
        setPoke1MoveName(move1 ? move1.name : '');
        setPoke2MoveName(move2 ? move2.name : '');
        setPoke1Move('');
        setPoke2Move('');
      })
      .finally(() => setLoading(false));
  }

  function resetBattle() {
    setBattleLog([]);
    setWinner(null);
    setPoke1Move('');
    setPoke2Move('');
    setPoke1MoveName('');
    setPoke2MoveName('');
    setPoke1HP(null);
    setPoke2HP(null);
    setTurn(1);
    setBattleId(null);
    setActiveIdx1(0);
    setActiveIdx2(0);
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Pokémon Battle Simulator (Turn-Based)</h2>
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
                  <div>HP: {poke1HP !== null ? poke1HP : team1Pokemon[poke1Idx].calculated_hp}</div>
                  <div>Attack: {team1Pokemon[poke1Idx].calculated_attack}</div>
                  <div>Defense: {team1Pokemon[poke1Idx].calculated_defense}</div>
                  <div>Speed: {team1Pokemon[poke1Idx].calculated_speed}</div>
                  <div>Special: {team1Pokemon[poke1Idx].calculated_special}</div>
                  <label>Move: </label>
                  <select value={poke1Move} onChange={e => setPoke1Move(e.target.value)}>
                    <option value=''>Select Move</option>
                    {getMoveOptions(team1Pokemon[poke1Idx]).map((m, i) => (
                      <option key={`${m.id}-${i}`} value={m.id}>{m.name}</option>
                    ))}
                  </select>
                  {poke1MoveName && <div>Last used: {poke1MoveName}</div>}
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
                  <div>HP: {poke2HP !== null ? poke2HP : team2Pokemon[poke2Idx].calculated_hp}</div>
                  <div>Attack: {team2Pokemon[poke2Idx].calculated_attack}</div>
                  <div>Defense: {team2Pokemon[poke2Idx].calculated_defense}</div>
                  <div>Speed: {team2Pokemon[poke2Idx].calculated_speed}</div>
                  <div>Special: {team2Pokemon[poke2Idx].calculated_special}</div>
                  <label>Move: </label>
                  <select value={poke2Move} onChange={e => setPoke2Move(e.target.value)}>
                    <option value=''>Select Move</option>
                    {getMoveOptions(team2Pokemon[poke2Idx]).map((m, i) => (
                      <option key={`${m.id}-${i}`} value={m.id}>{m.name}</option>
                    ))}
                  </select>
                  {poke2MoveName && <div>Last used: {poke2MoveName}</div>}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      <div style={{ marginTop: 24 }}>
  <button onClick={handleStartBattle} disabled={loading || battleId || poke1Idx === '' || poke2Idx === '' || poke1HP == null || poke2HP == null}>Start Battle</button>
  <button onClick={handleAttackTurn} disabled={loading || !battleId || !poke1Move || !poke2Move || poke1HP == null || poke2HP == null || poke1HP <= 0 || poke2HP <= 0 || winner} style={{ marginLeft: 8 }}>Attack!</button>
  <button onClick={resetBattle} style={{ marginLeft: 8 }}>Reset</button>
      </div>
      <div style={{ marginTop: 24, background: '#f9f9f9', padding: 12, minHeight: 80 }}>
        <b>Battle Log:</b>
        <ul>
          {battleLog.map((line, i) => <li key={i}>{line}</li>)}
        </ul>
  {winner !== null && <div style={{color:'green', fontWeight:'bold'}}>Winner: Team {winner + 1}!</div>}
      </div>
    </div>
  );
}

export default BattleSim;
