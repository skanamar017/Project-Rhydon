import React from 'react';
import './App.css';

import TeamManager from './components/TeamManager';
import BattleSim from './components/BattleSim';


function App() {
  const [view, setView] = React.useState('team');
  return (
    <div>
      <h1>Pokémon Team Manager & Battle Simulator</h1>
      <div style={{ marginBottom: 16 }}>
        <button onClick={() => setView('team')}>Team Manager</button>
        <button onClick={() => setView('battle')}>Battle Simulator</button>
      </div>
      {view === 'team' && <TeamManager />}
      {view === 'battle' && <BattleSim />}
    </div>
  );
}

export default App;
