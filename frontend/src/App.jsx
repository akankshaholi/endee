import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [filter, setFilter] = useState(''); // 'veg', 'non-veg', or ''

  const fetchRecommendations = async () => {
    try {
      const resp = await axios.get(`http://localhost:5000/recommend${filter ? `?type=${filter}` : ''}`);
      setRecommendations(resp.data.items || []);
    } catch (err) {
      console.error("Failed to fetch recommendations", err);
    }
  };

  const handleSearch = async (e, forcedQuery) => {
    if (e) e.preventDefault();
    const q = forcedQuery || query;
    if (!q) return;

    try {
      const resp = await axios.get(`http://localhost:5000/search?q=${q}${filter ? `?type=${filter}` : ''}`);
      setResults(resp.data.results || []);
      fetchRecommendations(); // Update recommendations as history changes
    } catch (err) {
      console.error("Search failed", err);
    }
  };

  useEffect(() => {
    fetchRecommendations();
    // Refresh search if filter changes while query exists
    if (query) handleSearch(null, query);
  }, [filter]);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial', maxWidth: '1000px', margin: 'auto' }}>
      <h1>🍽️ Smart Food Search</h1>
      
      {/* Search Input */}
      <div style={{ marginBottom: '20px' }}>
        <form onSubmit={handleSearch}>
          <input 
            type="text" 
            value={query} 
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for 'spicy street food' or 'something healthy'..."
            style={{ width: '70%', padding: '10px', fontSize: '16px', borderRadius: '5px', border: '1px solid #ccc' }}
          />
          <button type="submit" style={{ padding: '10px 20px', marginLeft: '10px', cursor: 'pointer' }}>Search</button>
        </form>
      </div>

      {/* Filters */}
      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => setFilter('')} style={{ fontWeight: filter === '' ? 'bold' : 'normal', marginRight: '10px' }}>All</button>
        <button onClick={() => setFilter('veg')} style={{ fontWeight: filter === 'veg' ? 'bold' : 'normal', marginRight: '10px' }}>Veg Only</button>
        <button onClick={() => setFilter('non-veg')} style={{ fontWeight: filter === 'non-veg' ? 'bold' : 'normal' }}>Non-Veg Only</button>
      </div>

      <div style={{ display: 'flex', gap: '30px' }}>
        {/* Main Results */}
        <div style={{ flex: 2 }}>
          <h2>Search Results</h2>
          {results.length === 0 && <p>Type something above to start searching!</p>}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '20px' }}>
            {results.map(item => (
              <div key={item.id} style={{ border: '1px solid #ddd', padding: '10px', borderRadius: '8px' }}>
                <img src={item.image_url} alt={item.name} style={{ width: '100%', height: '120px', objectFit: 'cover', borderRadius: '4px' }} />
                <h3>{item.name}</h3>
                <p style={{ fontSize: '12px', color: '#666' }}>{item.description}</p>
                <div style={{ fontSize: '11px', background: '#f0f0f0', padding: '5px', marginTop: '10px', borderRadius: '4px' }}>
                  <strong>AI Match:</strong> {item.explanation}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar Recommendations */}
        <div style={{ flex: 1, borderLeft: '1px solid #eee', paddingLeft: '20px' }}>
          <h2>Recommended For You</h2>
          {recommendations.map(item => (
            <div key={item.id} style={{ marginBottom: '15px' }}>
              <img src={item.image_url} alt={item.name} style={{ width: '100%', height: '80px', objectFit: 'cover', borderRadius: '4px' }} />
              <h4 style={{ margin: '5px 0' }}>{item.name}</h4>
              <span style={{ fontSize: '11px', color: '#999' }}>{item.cuisine} • ⭐{item.rating}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default App;
