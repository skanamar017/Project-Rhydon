import React, { useState } from 'react';

function BattleSimulator() {
  const [battleId, setBattleId] = useState(null);
  const [status, setStatus] = useState(null);
  const [move, setMove] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const startBattle = () => {
    setLoading(true);
    fetch('/battle/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    })
      .then(res => res.json())
      .then(data => setBattleId(data.battle_id))
      .catch(() => setError('Failed to start battle'))
      .finally(() => setLoading(false));
  };

  const getStatus = () => {
    if (!battleId) return;
    setLoading(true);
    fetch(`/battle/status?battle_id=${battleId}`)
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(() => setError('Failed to get status'))
      .finally(() => setLoading(false));
  };

  const makeMove = () => {
    setLoading(true);
    fetch('/battle/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ battle_id: battleId, move })
    })
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(() => setError('Failed to make move'))
      .finally(() => setLoading(false));
  };

  return (
    <div className="card">
      <h2>Battle Simulator</h2>
      <button onClick={startBattle}>Start Battle</button>
      {battleId && (
        <div>
          <p>Battle ID: {battleId}</p>
          <button onClick={getStatus}>Get Status</button>
          <input
            value={move}
            onChange={e => setMove(e.target.value)}
            placeholder="Move name or ID"
          />
          <button onClick={makeMove} disabled={!move}>Make Move</button>
          {loading && <div>Loading...</div>}
          {error && <div style={{color:'red'}}>{error}</div>}
          {status && <pre>{JSON.stringify(status, null, 2)}</pre>}
        </div>
      )}
    </div>
  );
}

export default BattleSimulator;