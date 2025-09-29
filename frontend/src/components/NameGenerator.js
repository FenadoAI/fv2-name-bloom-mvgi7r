import React, { useState, useEffect } from 'react';
import { useAuth } from '../App';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Heart, RefreshCw, Share2, Copy, Sparkles, Filter } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API = `${API_BASE}/api`;

const NameCard = ({ name, onToggleFavorite, isFavorite, showActions = true }) => {
  const { user } = useAuth();

  const getGenderColor = (gender) => {
    switch (gender) {
      case 'boy': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'girl': return 'bg-pink-100 text-pink-800 border-pink-200';
      case 'unisex': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPopularityLevel = (score) => {
    if (score >= 80) return { text: 'Very Popular', color: 'bg-green-100 text-green-800' };
    if (score >= 60) return { text: 'Popular', color: 'bg-yellow-100 text-yellow-800' };
    if (score >= 40) return { text: 'Moderate', color: 'bg-orange-100 text-orange-800' };
    return { text: 'Unique', color: 'bg-red-100 text-red-800' };
  };

  const popularity = getPopularityLevel(name.popularity_score);

  return (
    <Card className="h-full transition-all duration-200 hover:shadow-lg hover:scale-105">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <CardTitle className="text-2xl font-bold text-gray-800">
            {name.name}
          </CardTitle>
          {showActions && user && (
            <Button
              onClick={() => onToggleFavorite(name.id)}
              variant="ghost"
              size="sm"
              className="p-1"
            >
              <Heart
                className={`h-5 w-5 ${isFavorite ? 'fill-red-500 text-red-500' : 'text-gray-400'}`}
              />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline" className={getGenderColor(name.gender)}>
            {name.gender === 'unisex' ? 'Unisex' : name.gender.charAt(0).toUpperCase() + name.gender.slice(1)}
          </Badge>
          <Badge variant="outline" className={popularity.color}>
            {popularity.text}
          </Badge>
        </div>

        <div className="space-y-2 text-sm">
          <div>
            <span className="font-medium text-gray-700">Origin:</span>
            <span className="ml-2 text-gray-600">{name.origin}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Meaning:</span>
            <span className="ml-2 text-gray-600">{name.meaning}</span>
          </div>
          <div className="flex items-center">
            <span className="font-medium text-gray-700">Popularity:</span>
            <div className="ml-2 flex-1 bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${name.popularity_score}%` }}
              ></div>
            </div>
            <span className="ml-2 text-xs text-gray-500">{name.popularity_score}/100</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const FilterPanel = ({ filters, onFiltersChange }) => {
  const [tempFilters, setTempFilters] = useState(filters);

  const handleApplyFilters = () => {
    onFiltersChange(tempFilters);
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Filter className="h-5 w-5" />
          <span>Filters</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gender
            </label>
            <select
              value={tempFilters.gender || ''}
              onChange={(e) => setTempFilters({ ...tempFilters, gender: e.target.value || null })}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">All</option>
              <option value="boy">Boy</option>
              <option value="girl">Girl</option>
              <option value="unisex">Unisex</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Style
            </label>
            <select
              value={tempFilters.style || ''}
              onChange={(e) => setTempFilters({ ...tempFilters, style: e.target.value || null })}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">All Styles</option>
              <option value="traditional">Traditional</option>
              <option value="modern">Modern</option>
              <option value="unique">Unique</option>
              <option value="classic">Classic</option>
              <option value="trendy">Trendy</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Count
            </label>
            <Input
              type="number"
              min="1"
              max="50"
              value={tempFilters.count}
              onChange={(e) => setTempFilters({ ...tempFilters, count: parseInt(e.target.value) || 10 })}
            />
          </div>
        </div>

        <div className="mt-4">
          <Button onClick={handleApplyFilters} className="w-full">
            Apply Filters
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

const NameGenerator = ({ showFavoritesOnly = false }) => {
  const [names, setNames] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    gender: null,
    count: 10,
    style: null
  });
  const [shareUrl, setShareUrl] = useState('');
  const [showShareModal, setShowShareModal] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchFavorites();
    }
    if (showFavoritesOnly) {
      fetchFavorites();
    } else {
      generateNames();
    }
  }, [user, showFavoritesOnly]);

  const fetchFavorites = async () => {
    if (!user) return;

    try {
      const response = await axios.get(`${API}/favorites`);
      setFavorites(response.data);
      if (showFavoritesOnly) {
        setNames(response.data);
      }
    } catch (err) {
      console.error('Error fetching favorites:', err);
    }
  };

  const generateNames = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/names/generate`, filters);
      setNames(response.data);
    } catch (err) {
      console.error('Error generating names:', err);
      setError('Failed to generate names. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async (nameId) => {
    if (!user) return;

    const isFavorite = favorites.some(fav => fav.id === nameId);

    try {
      if (isFavorite) {
        await axios.delete(`${API}/favorites/remove/${nameId}`);
      } else {
        await axios.post(`${API}/favorites/add/${nameId}`);
      }
      fetchFavorites();
    } catch (err) {
      console.error('Error toggling favorite:', err);
    }
  };

  const shareList = async () => {
    if (!user || favorites.length === 0) return;

    try {
      const response = await axios.post(`${API}/favorites/share`);
      const fullShareUrl = `${window.location.origin}/shared/${response.data.share_token}`;
      setShareUrl(fullShareUrl);
      setShowShareModal(true);
    } catch (err) {
      console.error('Error creating share link:', err);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareUrl);
    alert('Share link copied to clipboard!');
  };

  const displayNames = showFavoritesOnly ? favorites : names;

  return (
    <div className="max-w-7xl mx-auto">
      {!showFavoritesOnly && (
        <FilterPanel filters={filters} onFiltersChange={setFilters} />
      )}

      <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
        <div className="flex items-center space-x-4">
          {!showFavoritesOnly && (
            <Button
              onClick={generateNames}
              disabled={loading}
              className="flex items-center space-x-2"
            >
              <Sparkles className="h-4 w-4" />
              <span>{loading ? 'Generating...' : 'Generate Names'}</span>
            </Button>
          )}

          {showFavoritesOnly && (
            <Button
              onClick={fetchFavorites}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh</span>
            </Button>
          )}
        </div>

        {user && favorites.length > 0 && (
          <Button
            onClick={shareList}
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Share2 className="h-4 w-4" />
            <span>Share Favorites</span>
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {displayNames.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">👶</div>
          <h3 className="text-xl font-medium text-gray-700 mb-2">
            {showFavoritesOnly ? 'No favorites yet' : 'No names generated yet'}
          </h3>
          <p className="text-gray-500">
            {showFavoritesOnly
              ? 'Start by generating some names and adding them to your favorites!'
              : 'Click "Generate Names" to discover beautiful baby names!'
            }
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {displayNames.map((name) => (
          <NameCard
            key={name.id}
            name={name}
            onToggleFavorite={toggleFavorite}
            isFavorite={favorites.some(fav => fav.id === name.id)}
            showActions={!showFavoritesOnly || user}
          />
        ))}
      </div>

      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
      )}

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Share Your Favorites</h3>
            <p className="text-gray-600 mb-4">
              Share this link with family and friends to show them your favorite names:
            </p>
            <div className="flex items-center space-x-2 mb-4">
              <Input value={shareUrl} readOnly className="flex-1" />
              <Button onClick={copyToClipboard} size="sm">
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex justify-end space-x-2">
              <Button
                onClick={() => setShowShareModal(false)}
                variant="outline"
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NameGenerator;