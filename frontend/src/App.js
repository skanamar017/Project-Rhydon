import React from 'react';
import './App.css';
import TeamManager from './components/TeamManager';
import BattleSimulator from './components/BattleSimulator';

function App() {
  return (
    <div>
      <h1>Pokémon Team Manager & Battle Simulator</h1>
      <TeamManager />
      <BattleSimulator />
    </div>
  );
}

export default App;
