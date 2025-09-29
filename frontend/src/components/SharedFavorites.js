import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Button } from './ui/button';
import { Heart, Share2, Copy } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API = `${API_BASE}/api`;

const SharedNameCard = ({ name }) => {
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
    <Card className="h-full transition-all duration-200 hover:shadow-lg">
      <CardHeader className="pb-3">
        <CardTitle className="text-2xl font-bold text-gray-800 flex items-center justify-between">
          {name.name}
          <Heart className="h-5 w-5 fill-red-500 text-red-500" />
        </CardTitle>
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

const SharedFavorites = () => {
  const { shareToken } = useParams();
  const [names, setNames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSharedNames();
  }, [shareToken]);

  const fetchSharedNames = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.get(`${API}/shared/${shareToken}`);
      setNames(response.data);
    } catch (err) {
      console.error('Error fetching shared names:', err);
      if (err.response?.status === 404) {
        setError('This shared favorites list could not be found. It may have been deleted or the link may be incorrect.');
      } else {
        setError('Failed to load shared favorites. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const copyCurrentUrl = () => {
    navigator.clipboard.writeText(window.location.href);
    alert('Link copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading shared favorites...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            Shared Favorite Names
          </h1>
          <p className="text-xl text-gray-600 mb-4">
            Someone special shared their favorite baby names with you
          </p>
          <Button
            onClick={copyCurrentUrl}
            variant="outline"
            className="flex items-center space-x-2 mx-auto"
          >
            <Share2 className="h-4 w-4" />
            <span>Share This List</span>
          </Button>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6 max-w-2xl mx-auto">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {names.length === 0 && !error && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">💔</div>
            <h3 className="text-xl font-medium text-gray-700 mb-2">
              No names in this list
            </h3>
            <p className="text-gray-500">
              This shared list doesn't contain any favorite names yet.
            </p>
          </div>
        )}

        {names.length > 0 && (
          <>
            <div className="text-center mb-6">
              <p className="text-lg text-gray-700">
                <span className="font-semibold">{names.length}</span> favorite name{names.length !== 1 ? 's' : ''} shared with love
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
              {names.map((name) => (
                <SharedNameCard key={name.id} name={name} />
              ))}
            </div>
          </>
        )}

        <div className="text-center mt-12">
          <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              Love these names?
            </h3>
            <p className="text-gray-600 mb-4">
              Create your own account to save favorites and share with others!
            </p>
            <Button
              onClick={() => window.location.href = '/auth'}
              className="w-full"
            >
              Get Started
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SharedFavorites;