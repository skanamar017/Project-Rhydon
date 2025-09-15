import { useEffect, useState } from 'react';

export function usePokemonMoves(pokemonId) {
  const [moves, setMoves] = useState([]);
  useEffect(() => {
    if (!pokemonId) return;
    fetch(`/Pokemon/${pokemonId}/moves`)
      .then(res => res.json())
      .then(data => setMoves(Array.isArray(data.moves) ? data.moves : []))
      .catch(() => setMoves([]));
  }, [pokemonId]);
  return moves;
}
