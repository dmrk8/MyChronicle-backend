import http from 'k6/http';
import { check } from 'k6';

const ids = [ 21, 16498, 101922, 1535, 113415, 21459, 11061, 21087, 5114, 20954, 21519, 11757 ];
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
  const res = http.get(`http://localhost:8000/media/anilist/anime/${id}`);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}