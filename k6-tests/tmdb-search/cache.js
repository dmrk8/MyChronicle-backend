import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = 'http://localhost:8000';

export const options = {
  vus: 20,
  duration: '30s',
};

const popularQueries = [
  '?page=1&sortBy=popularity.desc',
  '?page=2&sortBy=popularity.desc',
  '?page=3&sortBy=popularity.desc',
];

export default function () {
  const query = popularQueries[Math.floor(Math.random() * popularQueries.length)];
  const url = `${BASE_URL}/media/tmdb/search/movie${query}`;

  const res = http.get(url);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}