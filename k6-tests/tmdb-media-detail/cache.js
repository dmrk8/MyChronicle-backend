import http from 'k6/http';
import { check } from 'k6';

const ids = [862, 13, 24, 19995, 10191, 27205, 157336, 550];

export const options = {
  scenarios: {
    one_per_id: {
      executor: 'per-vu-iterations',
      vus: ids.length,
      iterations: 1,
      maxDuration: '1m',
    },
  },
};

export default function () {
  const id = ids[__VU - 1]; 
  const res = http.get(`http://localhost:8000/media/tmdb/movie/${id}`);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}